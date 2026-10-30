"""Ronaldo no Telegram: ouve o Guilherme (texto e áudio) e responde como assistente.

Fica rodando o tempo todo (o Agendador do Windows o reinicia se cair). A cada
mensagem do chat do Guilherme:
  1. se for áudio, transcreve localmente (faster-whisper, nada sai do computador);
  2. descobre com quem ele fala: o Ronaldo (padrão) ou outro agente, se a mensagem
     começar pelo nome ("Pedri, ...", "/casemiro ...", "Luiz Henrique, ...");
  3. chama o Claude Code em modo headless com a persona do agente, poucas
     ferramentas e permissão de edição só nas pastas dele;
  4. confere se os JSON/CSV continuam válidos (senão restaura o backup) e responde.

Só o chat em TELEGRAM_CHAT_ID é atendido; o resto é ignorado.
O avisar.py (lembretes) NÃO lê mensagens: só este programa consome o getUpdates.

Uso:
  python produtividade/ronaldo_telegram.py                  fica ouvindo (é o que o agendador chama)
  python produtividade/ronaldo_telegram.py --testar "texto"  mostra a resposta sem usar o Telegram
  python produtividade/ronaldo_telegram.py --transcrever arq.wav   testa a transcrição
"""
import argparse
import json
import os
import re
import shutil
import socket
import subprocess
import sys
import tempfile
import threading
import time
import urllib.request
from datetime import datetime
from pathlib import Path

import avisar
from avisar import DIAS, PASTA, RAIZ, ler_json, telegram

OFFSET = PASTA / ".ronaldo_offset"
FEITOS = PASTA / ".feitos.json"
LOG = PASTA / ".ronaldo.log"
CUSTO = PASTA / ".ronaldo_custo.jsonl"

ORCAMENTO_POR_MENSAGEM = "0.30"
TEMPO_LIMITE = 300
TURNOS_DE_HISTORICO = 10
MAX_AUDIO_SEG = 300
PORTA_TRAVA = 47811  # uma instância só
VIVO = PASTA / ".ronaldo_vivo.json"
TRAVADO_SEG = 480  # sem sinal de vida por tanto tempo = travou
ARQUIVOS_PROTEGIDOS = ["agenda.json", "lembretes.json", "agenda.md"]
MOVIMENTOS = RAIZ / "financas" / "movimentos.csv"
DASHBOARD = RAIZ / "financas" / "dashboard.py"

PALAVRAS_FEITO = {"feito", "ok", "pronto", "fiz", "feita"}
FRASE_FEITO = re.compile(r"\b(fiz|feito|feita|acabei|apontei|lancei|terminei|conclu[ií]|pronto|j[aá] (foi|fiz|apontei))\b", re.I)

# ---------- agentes acessíveis pelo Telegram ----------
# cwd = onde o agente pode editar (acceptEdits vale para o cwd e para os --add-dir);
# arquivos = o que vai pronto no contexto, para ele quase nunca precisar de ferramenta (economiza token).
AGENTES = {
    "ronaldo": dict(nome="Ronaldo", id="ronaldo-assistente", modelo="haiku", cwd=PASTA,
                    dirs=["financas"],
                    arquivos=[("produtividade/agenda.json", 6000), ("produtividade/lembretes.json", 6000),
                              ("produtividade/tarefas.md", 4000), ("financas/movimentos.csv", 4000),
                              ("financas/saldos.csv", 1500)]),
    "pedri": dict(nome="Pedri", id="pedri-gestor-tarefas", modelo="haiku", cwd=PASTA, dirs=["ecossistema"],
                  arquivos=[("produtividade/tarefas.md", 6000), ("produtividade/agenda.json", 4000)],
                  regra="Você edita só `tarefas.md`. Marque tarefa concluída como `feita` (não apague) e mova para o fim da seção."),
    "rodri": dict(nome="Rodri", id="rodri-apontamento-horas", modelo="haiku", cwd=PASTA, dirs=["ecossistema"],
                  arquivos=[("produtividade/horas.md", 6000), ("produtividade/tarefas.md", 3000)],
                  regra=("Você edita só `horas.md`. Nunca arredonde horas para fechar a conta; mostre a diferença. "
                         "Se ele responder ao aviso \"Hora de apontar as horas de hoje\" dizendo que já apontou, os avisos de hoje já foram encerrados: "
                         "confirme, anote em `horas.md` que o dia foi apontado no sistema da empresa (sem inventar projeto nem horas) e, se `horas.md` "
                         "não tiver o detalhe, pergunte UMA vez, em tom leve, quantas horas e em qual projeto, para fechar o registro.")),
    "kroos": dict(nome="Kroos", id="kroos-acessos-seguranca", modelo="haiku", cwd=PASTA, dirs=["ecossistema"],
                  arquivos=[("produtividade/acessos.md", 6000), ("produtividade/lembretes.json", 4000)],
                  regra=("Você edita só `acessos.md` e, para avisos de troca de senha, acrescenta itens em `lembretes.json` "
                         "(`id` novo, `agente` \"Ronaldo\", `texto` genérico sem a senha, `quando` AAAA-MM-DD HH:MM, `repete` \"nunca\"): "
                         "no vencimento e 3 dias antes. NUNCA peça, repita ou grave senha; se ele colar uma, diga para trocá-la.")),
    "lamine": dict(nome="Lamine Yamal", id="lamine-yamal-linkedin", modelo="sonnet", cwd=PASTA, dirs=["ecossistema"],
                   arquivos=[("produtividade/linkedin/rascunhos.md", 6000), ("produtividade/tarefas.md", 3000)],
                   regra=("Você edita só `linkedin/rascunhos.md`. Só rascunha: nunca publica. Nada confidencial da empresa, de clientes "
                          "ou de colegas nos posts. Entregue o texto do post pronto para copiar.")),
    "casemiro": dict(nome="Casemiro", id="casemiro-financeiro", modelo="sonnet", cwd=RAIZ / "financas",
                     dirs=["produtividade", "ecossistema"],
                     arquivos=[("financas/contexto.md", 5000), ("financas/movimentos.csv", 5000), ("financas/saldos.csv", 1500),
                               ("financas/pendencias.md", 2000)],
                     regra=("Você edita só arquivos de `financas/` (`movimentos.csv`, `saldos.csv`, `pendencias.md`). O estado ATUAL das contas está só nos CSV (`contexto.md` é a foto da manhã de 30/10: histórico e regras). Siga à risca as regras de "
                            "`contexto.md`: nunca invente valor, nunca marque pago sem o Guilherme dizer que pagou, nunca duplique, simulação não "
                            "altera dado real. Ao mudar `movimentos.csv`, o dashboard é refeito sozinho.")),
    "guardiola": dict(nome="Guardiola", id="guardiola-po-agilista", modelo="sonnet", cwd=PASTA, dirs=["ecossistema"],
                      arquivos=[("produtividade/kanban.md", 6000), ("produtividade/tarefas.md", 4000)],
                      regra=("Você edita só `kanban.md` (uma linha `- Título · detalhes` por cartão, na coluna certa; WIP máximo 3 em Fazendo). "
                             "O Kanban é sincronizado com o Trello a cada 10 min e o que o Guilherme mexer no Trello vale: nunca desfaça.")),
    # De Bruyne trabalha em SEGUNDO PLANO (vídeos levam minutos): ver iniciar_tarefa()/rodar_tarefa().
    "debruyne": dict(nome="De Bruyne", id="debruyne-orquestrador", segundo_plano=True),
    "luiz": dict(nome="Luiz Henrique", id="luiz-henrique-ecossistema", modelo="sonnet", cwd=RAIZ, dirs=[],
                 arquivos=[("ecossistema/README.md", 9000)],
                 regra=("Você pode criar e editar agentes (`.claude/agents/*.md`), pastas de setor e `ecossistema/README.md`. Por esta via "
                        "NUNCA edite `.env`, tokens, `client_secret*`, nem arquivos `.py`, `output/`, `render/`, `media/` ou o `CLAUDE.md` do canal: "
                        "se o pedido exigir isso, diga o que precisaria mudar e que ele deve pedir no computador.")),
}
ALIASES = {"luiz henrique": "luiz", "lamine yamal": "lamine", "de bruyne": "debruyne"}
NOMES_RE = "luiz henrique|lamine yamal|de bruyne|debruyne|ronaldo|pedri|rodri|kroos|lamine|casemiro|guardiola|luiz"

DICAS = {
    "pedri": 'Ex.: "Pedri, o que está parado?" ou "Pedri, cria a tarefa X no projeto Y".',
    "rodri": 'Ex.: "Rodri, aponta 4h no projeto X hoje" ou "Rodri, como está minha semana?".',
    "kroos": 'Ex.: "Kroos, troquei a senha do GitHub hoje" ou "Kroos, o que vence essa semana?". Nunca me mande a senha.',
    "lamine": 'Ex.: "Lamine, faz um post sobre organização de tarefas".',
    "casemiro": 'Ex.: "Casemiro, gastei 40 no mercado" ou "Casemiro, como estão as finanças?".',
    "guardiola": 'Ex.: "Guardiola, prioriza meu Kanban" ou "Guardiola, cria o cartão X em Pronto para fazer".',
    "debruyne": 'Ex.: "De Bruyne, me sugere 5 temas de vídeo sobre metodologia ágil" ou "De Bruyne, produz um vídeo sobre X". Ele trabalha em segundo plano e eu aviso quando terminar.',
    "luiz": 'Ex.: "Luiz Henrique, como está o ecossistema?" ou "Luiz Henrique, cria um agente para X".',
}

AJUDA = """🤖 Oi, Guilherme! Eu sou o Ronaldo.

Pode escrever ou mandar áudio 🎙️, como se eu fosse uma pessoa.

──────────────

👀 O QUE EU RESPONDO

• Compromissos e tarefas de hoje e dos próximos dias
• Contas a pagar e vencimentos
• Como estão as finanças (entradas, saídas, sobra)

──────────────

✏️ O QUE EU ATUALIZO

• Tarefas: "tomei café", "terminei o seguro"
• Compromissos: "tenho dentista amanhã às 15h" (vai para a sua Agenda do Google)
• Lembretes: "me lembra de ligar pro João às 16h"
• Contas: "paguei a luz"
• Gastos e recebimentos: "gastei 30 no mercado"

──────────────

⚡ ATALHOS (instantâneos e sem custo)

/hoje  resumo do dia
/dashboard  imagem das finanças
/ajuda  esta mensagem

──────────────

👥 OUTROS AGENTES

Comece a mensagem pelo nome do agente (ou toque no menu /):

• Pedri  tarefas e projetos
• Rodri  horas
• Kroos  senhas e acessos (nunca me mande senha)
• Lamine  posts do LinkedIn (só rascunho)
• Casemiro  finanças
• Guardiola  Kanban
• De Bruyne  vídeos do canal (trabalha em segundo plano e te avisa)
• Luiz Henrique  criar agentes e setores, ecossistema

Ex.: "Casemiro, quanto gastei esta semana?"

──────────────

⚠️ O QUE NÃO FAZEMOS POR AQUI

Publicar post, lançar horas ou pagar conta: isso é sempre com você. Postar vídeo no YouTube/LinkedIn também.

🔎 Podemos errar. Confira o ✅ quando disser que anotou algo."""

COMANDOS = [("hoje", "Resumo do dia"), ("dashboard", "Imagem das finanças"), ("ajuda", "O que o Ronaldo faz"),
            ("pedri", "Tarefas e projetos"), ("rodri", "Horas"), ("kroos", "Senhas e acessos"),
            ("lamine", "Posts do LinkedIn"), ("casemiro", "Finanças"), ("guardiola", "Kanban"),
            ("debruyne", "De Bruyne: vídeos do canal"),
            ("luiz", "Luiz Henrique: agentes e ecossistema")]

_modelo_voz = None


def log(msg):
    with LOG.open("a", encoding="utf-8") as f:
        f.write(f"{datetime.now():%Y-%m-%d %H:%M:%S} {msg}\n")
    if LOG.stat().st_size > 500_000:  # mantém o log pequeno
        LOG.write_text(LOG.read_text(encoding="utf-8")[-200_000:], encoding="utf-8")


# ---------- áudio ----------

_trava_voz = threading.Lock()


def carregar_voz():
    """Carrega o Whisper uma vez. Usa só o modelo já baixado (sem consultar a internet, que chegou a levar 1,5 min);
    a internet só entra se o modelo ainda não existir no computador."""
    global _modelo_voz
    with _trava_voz:
        if _modelo_voz is None:
            from faster_whisper import WhisperModel
            t = time.time()
            try:
                _modelo_voz = WhisperModel("small", device="cpu", compute_type="int8", local_files_only=True)
            except Exception:  # noqa: BLE001
                _modelo_voz = WhisperModel("small", device="cpu", compute_type="int8")
            log(f"modelo de voz carregado em {time.time() - t:.1f}s")
    return _modelo_voz


def transcrever(arquivo):
    segs, _ = carregar_voz().transcribe(str(arquivo), language="pt", beam_size=1, vad_filter=True)
    return " ".join(s.text.strip() for s in segs).strip()


def baixar_arquivo(file_id):
    info = telegram("getFile", file_id=file_id)["result"]
    url = f"https://api.telegram.org/file/bot{os.environ['TELEGRAM_BOT_TOKEN']}/{info['file_path']}"
    destino = Path(tempfile.gettempdir()) / f"ronaldo_{int(time.time())}{Path(info['file_path']).suffix or '.ogg'}"
    with urllib.request.urlopen(url, timeout=60) as r, destino.open("wb") as f:
        shutil.copyfileobj(r, f)
    return destino


# ---------- roteamento ----------

def rotear(texto):
    """('pedri', 'resto da mensagem') se começar pelo nome de um agente; senão ('ronaldo', texto)."""
    m = re.match(rf"^[/@]?({NOMES_RE})\b(?:@\w+)?[\s,:;.\-–]*(.*)$", texto.strip(), re.I | re.S)
    if not m:
        if re.search(r"\bde ?bruyne\b", texto, re.I):  # "pede pro De Bruyne..." vai direto para ele, com a frase inteira
            return "debruyne", texto.strip()
        return "ronaldo", texto.strip()
    nome = m.group(1).lower()
    return ALIASES.get(nome, nome), m.group(2).strip()


# ---------- Claude ----------

REGRAS_TELEGRAM = """## Como responder no Telegram
- Texto simples, sem markdown (sem **, #, tabelas). Curto e direto.
- **O relógio do Guilherme não mostra emoji.** A PRIMEIRA linha da resposta tem que ser só texto, sem nenhum emoji, e já dizer o essencial (a prévia da notificação mostra só ela). O estado de cada item vai sempre em palavras (feito, pendente, atrasado, vence hoje), nunca só no emoji. Depois da primeira linha os emojis continuam normais, porque ele os vê no celular.
- Formato limpo para ler no celular: uma ideia por parágrafo, linha em branco entre os blocos, um item por linha nas listas, nunca um textão. Para listas com mais de um assunto, título do bloco em MAIÚSCULAS com um emoji (ex.: "📅 COMPROMISSOS"). No máximo 12 linhas, a menos que ele peça detalhes.
- Emojis com bom senso: ⏳ pendente, ✅ feito, 📅 compromisso, ⏰ horário, 📍 local, 🔴 atrasado, e um do assunto (☕ café, 🏋️ academia, 🚗 carro/mãe, 💳 contas, 💼 trabalho, 🎤 show).
- Se a mensagem dele terminar com "[Contexto: ... respondeu a esta mensagem ...]", ele está respondendo àquela mensagem (um aviso ou uma resposta sua). Entenda a fala dentro desse contexto e NUNCA pergunte "o que você quer dizer" ou do que se trata: o assunto é o da mensagem citada.
- Pergunte só o que faltar. Não invente horário, valor, data nem fato.
- Só diga que fez algo se de fato editou o arquivo (confira que a edição foi aceita). Se a edição falhar, diga com honestidade. NUNCA diga que avisou, cobrou ou mandou recado a outro agente (você não consegue): só quem recebe a mensagem é quem ela nomeia. Se ele pedir algo para outro agente, diga para começar a mensagem pelo nome dele.
- Responda direto, sem introdução tipo "Olha só" e sem perguntar no final se está tudo ok.
- Nunca peça nem repita senha, token ou chave.
- Você não tem terminal (sem Bash) e não acessa a internet: só lê e edita arquivos.
"""

REGRAS_RONALDO = """- Quando ele disser que fez algo ("tomei café", "terminei o seguro"), marque `"feito": true` no item de `agenda.json` e confirme com ✅. Se pedir para adicionar compromisso ou tarefa, inclua em `agenda.json` (com `id`, `data` AAAA-MM-DD, `hora`, `titulo`) (o aviso 1 hora antes e a ida para o Google Agenda são automáticos: não crie lembrete para isso). Mantenha o JSON válido e não apague itens que ele não mencionou.
- Se ele pedir "me lembra de X às HH:MM", crie um lembrete único em `lembretes.json` (`id` novo, `agente` "Ronaldo", `texto` curto e genérico, `quando` "AAAA-MM-DD HH:MM", `repete` "nunca"). Hora já passada: pergunte.
- Edite só `agenda.json`, `lembretes.json`, `agenda.md` e, nos casos abaixo, `movimentos.csv`. Para tarefas do trabalho, horas, Kanban, senhas e LinkedIn, diga que ele pode chamar o agente certo por aqui pelo nome (Pedri, Rodri, Guardiola, Kroos, Lamine) e deixe o recado em `agenda.md` na linha `RECADO para <Craque>: ...`.
- Finanças (`movimentos.csv`, colunas data,tipo,categoria,descricao,valor,status): você pode (a) marcar uma conta como paga **somente** quando o Guilherme disser que pagou: troque `a pagar` por `pago` e acrescente ` (pago em DD/MM)` à descrição; (b) acrescentar UMA linha nova quando ele contar um gasto ou recebimento (data de hoje, valor que ele disse, categoria curta, status `pago`). Nunca apague nem altere outra linha, nunca invente valor, nunca registre simulação, não duplique. Saldo bancário real é desconhecido: nunca o afirme. Dúvida: pergunte antes de editar. Para análises financeiras mais profundas, sugira chamar o Casemiro.
"""


def historico_arq(chave):
    return PASTA / f".ronaldo_historico_{chave}.json"


def montar_contexto(chave, agora, historico):
    ag = AGENTES[chave]

    def ler(rel, limite):
        try:
            return (RAIZ / rel).read_text(encoding="utf-8")[:limite]
        except FileNotFoundError:
            return "(não existe)"

    hist = "\n".join(f"Guilherme: {h['u']}\n{ag['nome']}: {h['r']}" for h in historico[-TURNOS_DE_HISTORICO:]) or "(sem conversa recente)"
    regra = REGRAS_RONALDO if chave == "ronaldo" else f"- {ag['regra']}\n"
    arquivos = "\n".join(f"## {rel}\n{ler(rel, lim)}\n" for rel, lim in ag["arquivos"])
    texto = f"""# Contexto desta conversa (Telegram)

Agora: {DIAS[agora.weekday()]}, {agora:%d/%m/%Y %H:%M}. Você é {ag['nome']} e está conversando com o Guilherme pelo Telegram, no celular dele.

{REGRAS_TELEGRAM}
## Arquivos e permissões
- A raiz do projeto é `{RAIZ}`. Nas ferramentas de arquivo use SEMPRE caminhos absolutos (ex.: `{RAIZ.as_posix()}/produtividade/agenda.json`) e leia o arquivo com Read antes de editar. Os nomes abaixo são relativos a essa raiz.
- Você só consegue editar dentro de `{ag['cwd']}`.
{regra}
## Conversa recente
{hist}

# Arquivos (já lidos para você)
{arquivos}"""
    arq = PASTA / f".ronaldo_contexto_{chave}.md"
    arq.write_text(texto, encoding="utf-8")
    return arq


def validar_movimentos(antes):
    """Se alguém mexeu em movimentos.csv: confere, restaura se quebrou, refaz o dashboard se está ok."""
    if antes is None or MOVIMENTOS.read_bytes() == antes:
        return ""
    import csv
    import io

    def linhas(b):
        return list(csv.reader(io.StringIO(b.decode("utf-8"))))
    try:
        novo, velho = linhas(MOVIMENTOS.read_bytes()), linhas(antes)
        assert novo[0] == velho[0] and len(novo) >= len(velho)
        assert all(len(r) == len(novo[0]) for r in novo)
        for r in novo[1:]:
            float(r[4])
        assert all(r in novo for r in velho[1:]) or sum(1 for r in velho[1:] if r not in novo) <= 1
    except Exception as e:  # noqa: BLE001
        MOVIMENTOS.write_bytes(antes)
        log(f"movimentos.csv inválido ({e!r}); backup restaurado")
        return "\n\n⚠️ Não consegui registrar na planilha local direito. Nada foi mudado; pode repetir?"
    subprocess.run([sys.executable, str(DASHBOARD)], capture_output=True, timeout=60)
    log("movimentos.csv alterado; dashboard refeito")
    return ""


def perguntar_claude(chave, texto_usuario, agora):
    ag = AGENTES[chave]
    historico = ler_json(historico_arq(chave), [])
    contexto = montar_contexto(chave, agora, historico)

    backups = {nome: (PASTA / nome).read_bytes() for nome in ARQUIVOS_PROTEGIDOS if (PASTA / nome).exists()}
    csv_antes = MOVIMENTOS.read_bytes() if MOVIMENTOS.exists() else None

    env = dict(os.environ)
    for linha in (RAIZ / ".env").read_text(encoding="utf-8").splitlines():  # nenhuma chave do .env vai para o Claude
        if "=" in linha and not linha.lstrip().startswith("#"):
            env.pop(linha.split("=", 1)[0].strip(), None)
    env["CLAUDE_CODE_DISABLE_CLAUDE_MDS"] = "1"
    env["CLAUDE_CODE_DISABLE_AUTO_MEMORY"] = "1"

    cmd = [
        shutil.which("claude") or "claude", "-p",
        "--agent", ag["id"],
        "--model", ag["modelo"], "--effort", "low",
        "--append-system-prompt-file", str(contexto),
        "--permission-mode", "acceptEdits",  # só aceita edição dentro do cwd e dos --add-dir
        "--tools", "Read,Edit,Write,Glob,Grep",
        "--disable-slash-commands", "--strict-mcp-config", "--no-session-persistence",
        "--max-budget-usd", ORCAMENTO_POR_MENSAGEM,
        "--output-format", "json",
    ]
    for d in ag["dirs"]:
        cmd += ["--add-dir", str(RAIZ / d)]
    r = subprocess.run(cmd, input=texto_usuario, capture_output=True, text=True, encoding="utf-8",
                       cwd=ag["cwd"], env=env, timeout=TEMPO_LIMITE)
    if r.returncode != 0:
        raise RuntimeError(f"claude saiu com {r.returncode}: {r.stderr[:500]} {r.stdout[:500]}")
    dados = json.loads(r.stdout)
    resposta = (dados.get("result") or "").strip()
    if dados.get("permission_denials"):
        log(f"negado ({chave}): " + json.dumps(dados["permission_denials"], ensure_ascii=False)[:600])
    with CUSTO.open("a", encoding="utf-8") as f:
        f.write(json.dumps({"quando": agora.isoformat(timespec="seconds"), "agente": chave,
                            "usd": dados.get("total_cost_usd"), "turnos": dados.get("num_turns")}) + "\n")

    for nome, original in backups.items():  # JSON quebrado? restaura
        arq = PASTA / nome
        if nome.endswith(".json"):
            try:
                json.loads(arq.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, FileNotFoundError):
                arq.write_bytes(original)
                log(f"{nome} ficou inválido; backup restaurado")
                resposta += "\n\n⚠️ Não consegui salvar a alteração direito. Nada foi mudado; pode repetir?"
    resposta += validar_movimentos(csv_antes)
    resposta = resposta.replace("**", "").replace("__", "")  # Telegram está sem markdown
    historico.append({"u": texto_usuario[:400], "r": resposta[:700]})
    historico_arq(chave).write_text(json.dumps(historico[-20:], ensure_ascii=False), encoding="utf-8")
    resposta = resposta or "Anotado ✅"
    return resposta if chave == "ronaldo" else f"{ag['nome']}: {resposta}"  # 1ª linha segue só com texto


def dono_da_citacao(citado):
    """Agente que escreveu a mensagem citada, pelo prefixo 'Rodri: ...' que o avisar.py e as respostas usam."""
    m = re.match(rf"^({NOMES_RE})\s*:", citado.strip(), re.I)
    if not m:
        return None
    nome = m.group(1).lower()
    return ALIASES.get(nome, nome)


def responder(texto, agora, citado=None):
    """Mensagem -> texto de resposta, escolhendo o agente. Devolve None quando não há o que enviar.
    `citado` é o texto da mensagem que o Guilherme respondeu (recurso "responder" do Telegram)."""
    chave, resto = rotear(texto)
    if citado and resto:
        dono = dono_da_citacao(citado)
        if dono and chave == "ronaldo" and not re.match(r"^[/@]?ronaldo\b", texto.strip(), re.I):
            chave = dono  # resposta a um aviso/mensagem do Rodri vai para o Rodri
        resto += (f"\n\n[Contexto: o Guilherme respondeu, usando o 'responder' do Telegram, a esta mensagem "
                  f"enviada pelo bot: «{citado.strip()[:300]}». A fala dele é sobre isso.]")
    if not resto:
        if chave == "ronaldo":
            return AJUDA
        return f"{AGENTES[chave]['nome']} por aqui. Escreva o pedido depois do nome.\n\n{DICAS[chave]}"
    if AGENTES[chave].get("segundo_plano"):  # trabalho pesado: fica no Remote Control (sem custo extra pelo Telegram)
        return f"{AGENTES[chave]['nome']} trabalha pelo Claude Remote, não pelo Telegram. Abra o app do Claude no celular e escolha a sessão 'Ecossistema'."
    telegram("sendChatAction", chat_id=os.environ["TELEGRAM_CHAT_ID"], action="typing")
    return perguntar_claude(chave, resto, agora)


# ---------- tarefas em segundo plano (De Bruyne) ----------

TRAVA_TAREFA = PASTA / ".ronaldo_tarefa.json"
ORCAMENTO_TAREFA = "3.00"
TEMPO_TAREFA = 90 * 60
REGRAS_TAREFA = """Você foi chamado pelo Guilherme pelo Telegram e roda em SEGUNDO PLANO no computador dele, sem ninguém para responder perguntas.
- Siga o CLAUDE.md e o fluxo do canal. Decida o rotineiro sozinho e registre as suposições.
- Se o pedido for só sugerir/listar (temas, ideias), responda isso e pare; não produza o vídeo.
- Se faltar informação INDISPENSÁVEL, devolva perguntas objetivas ou opções numeradas e pare.
- NUNCA publique em YouTube, LinkedIn ou qualquer lugar, nunca gaste dinheiro (sem --allow-paid) e nunca mostre chaves do .env.
- Sua resposta final vai por Telegram (relógio inclui): texto simples, sem markdown, 1ª linha só texto sem emoji com o essencial, no máximo 15 linhas. Diga a pasta output/<slug> do que foi gerado."""


def tarefa_em_andamento():
    t = ler_json(TRAVA_TAREFA, None)
    if not t:
        return None
    try:
        out = subprocess.run(["tasklist", "/FI", f"PID eq {t['pid']}"], capture_output=True, text=True).stdout
        if str(t["pid"]) in out:
            return t
    except Exception:  # noqa: BLE001
        pass
    TRAVA_TAREFA.unlink(missing_ok=True)
    return None


def iniciar_tarefa(chave, pedido, agora):
    ag = AGENTES[chave]
    atual = tarefa_em_andamento()
    if atual:
        return f"{ag['nome']} ainda está ocupado com: {atual['pedido'][:120]}. Quando ele terminar eu aviso, aí você manda o próximo."
    arq = PASTA / f".ronaldo_tarefa_{agora:%H%M%S}.txt"
    arq.write_text(pedido, encoding="utf-8")
    py = Path(sys.executable)
    py = py.with_name("pythonw.exe") if py.with_name("pythonw.exe").exists() else py
    proc = subprocess.Popen([str(py), str(Path(__file__).resolve()), "--tarefa", str(arq), chave],
                            cwd=str(PASTA), creationflags=0x00000008 | 0x00000200, close_fds=True,
                            stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    TRAVA_TAREFA.write_text(json.dumps({"pid": proc.pid, "pedido": pedido[:300], "inicio": agora.isoformat(timespec="seconds")}),
                            encoding="utf-8")
    log(f"tarefa em segundo plano ({chave}) pid {proc.pid}: {pedido[:100]}")
    return (f"{ag['nome']} recebeu o pedido e já está trabalhando.\n\nPedido: {pedido[:200]}\n\n"
            f"Aviso aqui assim que terminar (vídeo leva alguns minutos; ideias, menos). Pode seguir conversando comigo enquanto isso.")


def rodar_tarefa(arq, chave):
    """Roda no processo separado: chama o agente com todas as ferramentas e devolve o resultado por Telegram."""
    ag = AGENTES[chave]
    pedido = Path(arq).read_text(encoding="utf-8")
    inicio = time.time()
    env = dict(os.environ)
    for linha in (RAIZ / ".env").read_text(encoding="utf-8").splitlines():
        if "=" in linha and not linha.lstrip().startswith("#"):
            env.pop(linha.split("=", 1)[0].strip(), None)
    env["CLAUDE_CODE_DISABLE_AUTO_MEMORY"] = "1"
    regras = PASTA / ".ronaldo_regras_tarefa.md"
    regras.write_text(REGRAS_TAREFA, encoding="utf-8")
    cmd = [shutil.which("claude") or "claude", "-p", "--agent", ag["id"], "--model", "sonnet",
           "--append-system-prompt-file", str(regras), "--permission-mode", "acceptEdits",
           "--allowedTools", "Agent,Read,Write,Edit,Glob,Grep,WebSearch,WebFetch,Bash(python run.py *),Bash(python -m media.sketch *),Bash(ls *),Bash(dir *)",
           "--strict-mcp-config", "--no-session-persistence", "--max-budget-usd", ORCAMENTO_TAREFA,
           "--output-format", "json"]
    try:
        r = subprocess.run(cmd, input=pedido, capture_output=True, text=True, encoding="utf-8",
                           cwd=RAIZ, env=env, timeout=TEMPO_TAREFA)
        dados = json.loads(r.stdout) if r.stdout.strip().startswith("{") else {}
        texto = (dados.get("result") or "").strip() or f"Terminou sem resposta (código {r.returncode}). {r.stderr[:200]}"
        with CUSTO.open("a", encoding="utf-8") as f:
            f.write(json.dumps({"quando": datetime.now().isoformat(timespec="seconds"), "agente": chave,
                                "usd": dados.get("total_cost_usd"), "turnos": dados.get("num_turns")}) + "\n")
    except subprocess.TimeoutExpired:
        texto = "Passou de 90 minutos e parei. Veja a pasta output/ no computador para o que já ficou pronto."
    except Exception as e:  # noqa: BLE001
        log(f"tarefa {chave} falhou: {e!r}")
        texto = "Deu erro ao rodar. Tente de novo ou me peça o status."
    texto = texto.replace("**", "").replace("__", "")
    avisar.enviar(f"{ag['nome']}: {texto}")
    novos = [v for v in (RAIZ / "output").glob("*/video.mp4") if v.stat().st_mtime >= inicio]
    for v in novos[:1]:
        try:
            if v.stat().st_size < 49_000_000:
                avisar.enviar_arquivo(v, f"🎬 {v.parent.name}")
            else:
                avisar.enviar(f"🎬 Vídeo pronto, mas grande para o Telegram. Está em output/{v.parent.name}/video.mp4")
        except Exception as e:  # noqa: BLE001
            log(f"envio do vídeo falhou: {e!r}")
    Path(arq).unlink(missing_ok=True)
    TRAVA_TAREFA.unlink(missing_ok=True)


# ---------- Telegram ----------

def tratar(msg):
    agora = datetime.now()
    if msg.get("voice") or msg.get("audio"):
        midia = msg.get("voice") or msg["audio"]
        if midia.get("duration", 0) > MAX_AUDIO_SEG:
            avisar.enviar("🎙️ Esse áudio é longo demais (máximo 5 minutos). Pode mandar em partes?")
            return
        telegram("sendChatAction", chat_id=os.environ["TELEGRAM_CHAT_ID"], action="typing")
        t0 = time.time()
        arq = baixar_arquivo(midia["file_id"])
        t1 = time.time()
        try:
            texto = transcrever(arq)
        finally:
            arq.unlink(missing_ok=True)
        log(f"áudio {midia.get('duration', 0)}s: download {t1 - t0:.1f}s, transcrição {time.time() - t1:.1f}s")
        if not texto:
            avisar.enviar("🎙️ Não consegui entender o áudio. Pode repetir ou mandar por texto?")
            return
        avisar.enviar(f"🎙️ Entendi: “{texto}”")
    elif msg.get("text"):
        texto = msg["text"].strip()
    else:
        avisar.enviar("Por enquanto eu entendo texto e áudio 🙂")
        return

    citada = msg.get("reply_to_message") or {}
    citado = (citada.get("text") or citada.get("caption") or "").strip()

    # resposta a um aviso "(responda 'feito'...)" dizendo que já fez: encerra os avisos de hoje, e segue para o agente registrar
    if citado and "responda 'feito'" in citado and FRASE_FEITO.search(texto):
        grupo = ler_json(PASTA / ".estado_avisos.json", {}).get("ultimo_grupo")
        if grupo:
            feitos = ler_json(FEITOS, {})
            feitos[f"{grupo}|{agora:%Y-%m-%d}"] = True
            FEITOS.write_text(json.dumps(feitos), encoding="utf-8")
            log(f"aviso {grupo} encerrado por resposta: {texto[:60]}")

    if texto.lower().rstrip("!. ") in PALAVRAS_FEITO:
        estado = ler_json(PASTA / ".estado_avisos.json", {})
        grupo = estado.get("ultimo_grupo")
        if grupo:
            feitos = ler_json(FEITOS, {})
            feitos[f"{grupo}|{agora:%Y-%m-%d}"] = True
            FEITOS.write_text(json.dumps(feitos), encoding="utf-8")
            avisar.enviar("Anotado ✅ Sem mais avisos sobre isso hoje.")
            return

    comando = texto.lower().split("@")[0].strip().rstrip("!. ")
    if comando in {"/ajuda", "/start", "ajuda", "menu", "/menu", "o que você faz", "o que voce faz"}:
        avisar.enviar(AJUDA)  # atalhos sem Claude (zero token)
        return
    if comando in {"/hoje", "hoje", "resumo", "/resumo"}:
        avisar.enviar(avisar.montar_resumo(agora))
        return
    if "dashboard" in texto.lower():  # atalho sem Claude: refaz e manda a imagem (zero token)
        subprocess.run([sys.executable, str(DASHBOARD)], capture_output=True, timeout=60)
        avisar.enviar_foto(RAIZ / "financas" / "dashboard.png", f"📊 Dashboard financeiro · {agora:%d/%m %H:%M}")
        return

    t = time.time()
    resposta = responder(texto, agora, citado)
    log(f"resposta em {time.time() - t:.1f}s")
    if resposta:
        avisar.enviar(resposta)


def ouvir():
    trava = socket.socket()
    try:
        trava.bind(("127.0.0.1", PORTA_TRAVA))
    except OSError:
        # já tem um Ronaldo ouvindo; se ele parou de dar sinal de vida (travou), derruba e assume
        vivo = ler_json(VIVO, {})
        if time.time() - vivo.get("t", 0) < TRAVADO_SEG or not vivo.get("pid"):
            sys.exit(0)
        log(f"Ronaldo pid {vivo['pid']} sem sinal há {int(time.time() - vivo['t'])}s; reiniciando")
        subprocess.run(["taskkill", "/F", "/PID", str(vivo["pid"])], capture_output=True)
        time.sleep(3)
        try:
            trava.bind(("127.0.0.1", PORTA_TRAVA))
        except OSError:
            sys.exit(0)
    chat = os.environ["TELEGRAM_CHAT_ID"]
    offset = int(OFFSET.read_text()) if OFFSET.exists() else 0
    try:  # menu de comandos do bot (o "/" no Telegram)
        telegram("setMyCommands", commands=json.dumps([{"command": c, "description": d} for c, d in COMANDOS]))
    except Exception as e:  # noqa: BLE001
        log(f"setMyCommands falhou: {e!r}")
    log("ouvindo")
    threading.Thread(target=carregar_voz, daemon=True).start()  # primeiro áudio já encontra o modelo pronto
    while True:
        VIVO.write_text(json.dumps({"pid": os.getpid(), "t": time.time()}), encoding="utf-8")
        try:
            for upd in telegram("getUpdates", offset=offset + 1, timeout=50).get("result", []):
                offset = max(offset, upd["update_id"])
                OFFSET.write_text(str(offset))
                msg = upd.get("message") or {}
                if str(msg.get("chat", {}).get("id")) != chat:
                    continue
                try:
                    tratar(msg)
                except Exception as e:  # noqa: BLE001
                    log(f"erro ao tratar mensagem: {e!r}")
                    avisar.enviar("Deu um problema aqui do meu lado 😅 Tenta de novo em instantes.")
        except Exception as e:  # noqa: BLE001
            log(f"erro de conexão: {e!r}")
            time.sleep(15)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--testar")
    ap.add_argument("--transcrever")
    ap.add_argument("--tarefa", nargs=2, metavar=("ARQ", "AGENTE"))
    args = ap.parse_args()
    avisar.carregar_env()
    if sys.stdout:
        sys.stdout.reconfigure(encoding="utf-8")
    if args.tarefa:
        rodar_tarefa(*args.tarefa)
    elif args.transcrever:
        print(transcrever(args.transcrever))
    elif args.testar:
        print(responder(args.testar, datetime.now()))
    else:
        ouvir()


if __name__ == "__main__":
    main()
