"""CLI: python -m clipes <comando>. Ver clipes/README.md."""
import argparse
import json
import sys

from . import estado as E
from . import perfis as PF
from . import pipeline as p


def main() -> None:
    ap = argparse.ArgumentParser(prog="clipes")
    sub = ap.add_subparsers(dest="cmd", required=True)

    a = sub.add_parser("tudo", help="ingest + transcrever + momentos + cortar")
    a.add_argument("origem", help="URL ou arquivo local")
    a.add_argument("--autor", required=True, help="criador original (crédito)")
    a.add_argument("--autorizacao", required=True, choices=sorted(p.AUTORIZACOES))
    a.add_argument("--prova", default="", help="link/e-mail/print da permissão")
    a.add_argument("--titulo", default="", help="título do vídeo original")
    a.add_argument("--slug")
    a.add_argument("--quantos", type=int, help="padrão: a quantidade do perfil")
    a.add_argument("--modelo", default="small", help="whisper: tiny/base/small/medium")
    a.add_argument("--perfil", default=PF.PADRAO_NOVOS, help="id do perfil: geral (qualquer vídeo, padrão) ou gta6")
    a.add_argument("--fluxo", choices=["v2", "v1"], default="v2",
                   help="v2 = fluxo configurável (dispara os agentes, para na revisão); v1 = só código, agentes pelo Pelé")

    for nome, ajuda in (("momentos", "reescolhe os melhores momentos"),
                        ("cortar", "gera os cortes 9:16"),
                        ("check", "gate de publicação")):
        s = sub.add_parser(nome, help=ajuda)
        s.add_argument("slug")
        if nome == "momentos":
            s.add_argument("--quantos", type=int, help="padrão: a quantidade do perfil")
        if nome == "cortar":
            s.add_argument("--ids", type=int, nargs="*")
            s.add_argument("--gancho")
            s.add_argument("--layout", choices=list(p.LAYOUTS), default=None,
                           help="padrão: preset do perfil. zoom = câmera em cima e jogo ampliado embaixo")
            s.add_argument("--cam", default=p.CAM_PADRAO,
                           help="x:y:w:h da câmera no vídeo 1920x1080, ou 'nenhuma'")

    e = sub.add_parser("estado", help="reporta o estado de um nó do fluxo (agentes usam isto)")
    e.add_argument("slug")
    e.add_argument("no", choices=list(E.NOS))
    e.add_argument("status", choices=list(E.STATUS))
    e.add_argument("msg", nargs="?", default="")
    e.add_argument("--agente")
    e.add_argument("--detalhe", action="append", default=[], help="o que aconteceu (repita a opção)")
    e.add_argument("--resolver", default="", help="como resolver")
    e.add_argument("--progresso", type=float, help="0 a 1, só se o andamento for medido de verdade")

    aj = sub.add_parser("ajustar", help="refaz um corte com novo intervalo/legenda/enquadramento/áudio")
    aj.add_argument("slug")
    aj.add_argument("--id", type=int, required=True)
    aj.add_argument("--ini", type=float, required=True)
    aj.add_argument("--fim", type=float, required=True)
    aj.add_argument("--layout", choices=list(p.LAYOUTS), default="borrado")
    aj.add_argument("--sem-legenda", action="store_true")
    aj.add_argument("--sem-audio", action="store_true")

    av = sub.add_parser("avaliar", help="plano B: o Totti avalia o potencial dos cortes pedidos (o fluxo já faz isso)")
    av.add_argument("slug")
    av.add_argument("--ids", type=int, nargs="*", default=[], help="cortes; vazio = os que ainda não têm nota")

    lg = sub.add_parser("legendas", help="transcrição rápida pela legenda automática do YouTube (sem Whisper)")
    lg.add_argument("slug")
    lg.add_argument("--lang", default="pt-orig")
    lg.add_argument("--forcar", action="store_true")

    td = sub.add_parser("triagem-dados", help="mede a fonte (dados para o Rivaldo): triagem_dados.json")
    td.add_argument("slug")

    rf = sub.add_parser("refinar", help="retranscreve só os momentos escolhidos com modelo melhor")
    rf.add_argument("slug")
    rf.add_argument("--modelo", default="small")

    ro = sub.add_parser("rodar", help="roda o fluxo do projeto de onde parou (ou --desde uma etapa)")
    ro.add_argument("slug")
    ro.add_argument("--desde", help="refaz a partir desta etapa (tentar de novo)")
    ro.add_argument("--refazer", action="store_true", help="apaga o resultado da etapa --desde antes")

    de = sub.add_parser("decidir", help="aceita/rejeita sugestões ou ajusta limites (segundos do original)")
    de.add_argument("slug")
    de.add_argument("--aceitar", type=int, nargs="*", default=[])
    de.add_argument("--rejeitar", type=int, nargs="*", default=[])
    de.add_argument("--id", type=int, help="com --ini/--fim: ajusta os limites desta sugestão")
    de.add_argument("--ini", type=float)
    de.add_argument("--fim", type=float)

    ap_ = sub.add_parser("aprovar", help="fecha o fluxo depois de revisar os cortes")
    ap_.add_argument("slug")

    pf = sub.add_parser("perfis", help="lista ou mostra perfis de conteúdo")
    pf.add_argument("acao", nargs="?", default="listar", choices=["listar", "mostrar", "duplicar", "arquivar", "restaurar"])
    pf.add_argument("id", nargs="?")
    pf.add_argument("--nome", help="nome da cópia (duplicar)")
    pf.add_argument("--todos", action="store_true", help="inclui arquivados")

    em = sub.add_parser("embalar", help="textos de postagem por plataforma")
    em.add_argument("slug")

    pa = sub.add_parser("painel", help="abre o painel visual do setor (porta 8767)")
    pa.add_argument("--porta", type=int, default=8767)
    pa.add_argument("--sem-navegador", action="store_true")
    pa.add_argument("--rede", action="store_true", help="abre também para outros PCs da rede, com senha")

    r = ap.parse_args()
    if r.cmd == "perfis":
        if r.acao == "listar":
            for x in PF.listar(r.todos):
                print(f"{x['id']:<20} v{x['versao']:<3} {x['nome']}{'  (arquivado)' if x['arquivado'] else ''}")
            return
        if not r.id:
            raise SystemExit("informe o id do perfil")
        if r.acao == "mostrar":
            print(json.dumps(PF.carregar(r.id), ensure_ascii=False, indent=2))
        elif r.acao == "duplicar":
            print(f"criado: {PF.duplicar(r.id, r.nome)['id']}")
        else:
            x = PF.arquivar(r.id, r.acao == "arquivar")
            print(f"{x['id']}: {'arquivado' if x['arquivado'] else 'ativo'}")
        return
    if r.cmd == "rodar":
        from .orquestrador import rodar
        fim = rodar(p.pasta(r.slug), r.desde, r.refazer)
        print(f"[rodar] {fim}")
        return
    if r.cmd == "decidir":
        d = p.pasta(r.slug)
        for i in r.aceitar:
            p.decidir(d, i, "aceito")
        for i in r.rejeitar:
            p.decidir(d, i, "rejeitado")
        if r.id is not None:
            print(p.decidir(d, r.id, None, r.ini, r.fim))
        return
    if r.cmd == "aprovar":
        from .orquestrador import aprovar
        aprovar(p.pasta(r.slug))
        return
    if r.cmd == "tudo":
        from . import etapas as T
        from .orquestrador import rodar
        if r.fluxo == "v2" and r.slug:
            # o fluxo do projeto existe DESDE O INÍCIO: todos os agentes (inclusive o Rivaldo) aparecem no painel
            # durante o download, não só depois dele
            d0 = p.pasta(r.slug)
            if not (d0 / "fluxo.json").exists() and not (d0 / "momentos.json").exists():
                fl0 = T.padrao()
                for e in fl0["etapas"]:
                    if e["id"] == "transcricao":
                        e["ferramentas"]["modelo"] = r.modelo
                T.gravar(d0, fl0)
        d = p.ingest(r.origem, r.slug, r.autorizacao, r.prova, r.autor, r.titulo, r.perfil)
        if r.fluxo == "v1" or (d / "momentos.json").exists() and not (d / "fluxo.json").exists():
            # V1 (ou projeto antigo retomado): mesmo encadeamento de antes; agentes pelo Pelé
            p.transcrever(d, r.modelo)
            p.momentos(d, r.quantos)
            p.cortar(d)
            if p.check(d):
                p.embalar(d)
            return
        if not (d / "fluxo.json").exists():
            fl = T.padrao()
            for e in fl["etapas"]:
                if e["id"] == "transcricao":
                    e["ferramentas"]["modelo"] = r.modelo
            T.gravar(d, fl)
        # Com a triagem do Rivaldo ativa, os momentos saem DEPOIS dela (os N melhores): não calcular antes.
        if r.quantos and not (d / "momentos.json").exists() and not T.ativa(d, "triagem"):  # quantidade diferente da do perfil
            p.transcrever(d, r.modelo)
            p.momentos(d, r.quantos)
        print(f"[tudo] {rodar(d)}")
        return
    if r.cmd == "painel":
        from .painel import servir
        servir(r.porta, not r.sem_navegador, r.rede)
    elif r.cmd == "estado":
        E.marcar(p.pasta(r.slug), r.no, r.status, r.msg, r.agente, r.detalhe, r.resolver, r.progresso)
    elif r.cmd == "legendas":
        from .legendas_youtube import importar
        importar(p.pasta(r.slug), r.lang, r.forcar)
    elif r.cmd == "triagem-dados":
        from .triagem import coletar
        dd = coletar(p.pasta(r.slug))
        print(f"[triagem-dados] {dd['duracao_min']} min; {dd['seletor']['candidatos_integros']} candidatos íntegros; "
              f"{dd['seletor']['momentos_fortes']} momento(s) forte(s) ({dd['seletor']['momentos_fortes_por_10min']} por 10 min).")
    elif r.cmd == "avaliar":
        from .orquestrador import avaliar_potencial
        res = avaliar_potencial(p.pasta(r.slug), r.ids or None)
        print(f"[avaliar] {res}")
        if res.startswith("falhou"):
            raise SystemExit(1)
    elif r.cmd == "ajustar":
        p.reeditar(p.pasta(r.slug), r.id, r.ini, r.fim, r.layout, not r.sem_legenda, not r.sem_audio)
    elif r.cmd == "refinar":
        p.refinar(p.pasta(r.slug), r.modelo)
    elif r.cmd == "embalar":
        p.embalar(p.pasta(r.slug))
    else:
        d = p.pasta(r.slug)
        if r.cmd == "momentos":
            (d / "momentos.json").unlink(missing_ok=True)
            p.momentos(d, r.quantos)
        elif r.cmd == "cortar":
            p.cortar(d, r.ids, r.gancho, r.layout, r.cam)
        else:
            ok = p.check(d)
            if ok:
                p.embalar(d)
            sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
