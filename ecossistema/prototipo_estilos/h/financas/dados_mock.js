/* MOCK INVENTADO da tela de Finanças (PROG-024b). Nenhum valor aqui vem dos CSV reais.
   Mesmo formato de window.FINANCAS (programacao/tecnico/prog-024-contrato-financas.md): centavos, datas ISO.
   Datas são relativas a hoje para a tela parecer viva. Escolha o cenário com ?cenario=
   normal | atrasado | divergente | sem_vencimentos | vazio | erro | velho | carregando.
   Na integração real, troque este arquivo por <script src="../../app/dados/financas.js"> (ver a especificação). */
(function () {
  var q = (location.search.match(/[?&]cenario=([^&]*)/) || [])[1] || "normal";
  window.FINANCAS_CENARIOS = [
    ["normal", "Normal"], ["atrasado", "Vencimento atrasado"], ["divergente", "Saldo divergente"],
    ["sem_vencimentos", "Sem vencimentos"], ["vazio", "Vazio"], ["erro", "Erro: arquivo ausente"], ["velho", "Dados velhos"], ["carregando", "Carregando"]
  ];
  window.FINANCAS_MOCK = q;

  function p2(n) { return (n < 10 ? "0" : "") + n; }
  function iso(off) { var d = new Date(); d.setDate(d.getDate() + off); return d.getFullYear() + "-" + p2(d.getMonth() + 1) + "-" + p2(d.getDate()); }
  function ym(off) { var d = new Date(); d.setDate(1); d.setMonth(d.getMonth() + off); return d.getFullYear() + "-" + p2(d.getMonth() + 1); }
  function agora(offDias, hh) { return iso(offDias) + "T" + hh; }
  function soma(l, k) { return l.reduce(function (a, x) { return a + x[k]; }, 0); }

  function normal() {
    var venc = [
      { data: iso(2), descricao: "Internet fibra", categoria: "contas", valor: 12990, dias_restantes: 2, atrasado: false, status: "a pagar" },
      { data: iso(6), descricao: "Seguro do carro", categoria: "transporte", valor: 38700, dias_restantes: 6, atrasado: false, status: "a pagar" },
      { data: iso(12), descricao: "Condomínio", categoria: "moradia", valor: 44610, dias_restantes: 12, atrasado: false, status: "a pagar" }
    ];
    var cats = [["moradia", 150000], ["mercado", 96400], ["contas", 62300], ["transporte", 48500], ["restaurantes", 41200], ["assinaturas", 29800], ["lazer", 27120], ["saude", 15700], ["outros", 10000]];
    var tc = cats.reduce(function (a, c) { return a + c[1]; }, 0);
    var serie = [
      { mes: ym(-5), recebido: 580000, previsto: 0, gasto_pago: 402300, gasto_a_pagar: 0 },
      { mes: ym(-4), recebido: 590000, previsto: 0, gasto_pago: 371900, gasto_a_pagar: 0 },
      { mes: ym(-3), recebido: 575000, previsto: 0, gasto_pago: 398450, gasto_a_pagar: 0 },
      { mes: ym(-2), recebido: 600000, previsto: 0, gasto_pago: 366200, gasto_a_pagar: 0 },
      { mes: ym(-1), recebido: 590000, previsto: 0, gasto_pago: 421800, gasto_a_pagar: 0 },
      { mes: ym(0), recebido: 612000, previsto: 150000, gasto_pago: 384720, gasto_a_pagar: soma(venc, "valor") }
    ];
    return {
      gerado_em: agora(0, "08:40:00"), moeda: "BRL", unidade: "centavos", mes_atual: ym(0),
      saldos: {
        contas: [
          { conta: "Banco Azul", data: iso(-1), saldo: 842310, observacao: "", nao_confirmado: false, historico: false, idade_dias: 1 },
          { conta: "Carteira Digital", data: iso(-2), saldo: 120550, observacao: "", nao_confirmado: false, historico: false, idade_dias: 2 }
        ],
        disponivel: 962860, contas_fora_do_disponivel: [],
        observacao: "Saldo bancário informado; não é o resultado das movimentações."
      },
      recebido: { mes: 612000, previsto_mes: 150000, total_6m: soma(serie, "recebido"), previsto_6m: 150000 },
      gastos: { pagos_mes: 384720, a_pagar_mes: soma(venc, "valor"), pagos_6m: soma(serie, "gasto_pago"), a_pagar_6m: soma(venc, "valor") },
      serie_mensal: serie,
      receitas_x_gastos: { mes: ym(0), receitas: 612000, gastos: 384720 },
      categorias: cats.map(function (c) { return { categoria: c[0], valor: c[1], percentual: Math.round(c[1] * 1000 / tc) / 10 }; }),
      vencimentos: venc,
      movimentos_recentes: [
        { data: iso(-1), tipo: "gasto", categoria: "mercado", descricao: "Compra da semana", valor: 21890, status: "pago" },
        { data: iso(-1), tipo: "gasto", categoria: "restaurantes", descricao: "Almoço de domingo", valor: 8650, status: "pago" },
        { data: iso(-2), tipo: "receita", categoria: "renda", descricao: "Projeto de cliente", valor: 150000, status: "pago" },
        { data: iso(-3), tipo: "gasto", categoria: "assinaturas", descricao: "Streaming de vídeo", valor: 3990, status: "pago" },
        { data: iso(-4), tipo: "gasto", categoria: "transporte", descricao: "Combustível", valor: 19000, status: "pago" },
        { data: iso(-6), tipo: "gasto", categoria: "saude", descricao: "Farmácia", valor: 5710, status: "pago" },
        { data: iso(-8), tipo: "receita", categoria: "renda", descricao: "Salário", valor: 462000, status: "pago" },
        { data: iso(9), tipo: "receita", categoria: "renda", descricao: "Parcela do projeto", valor: 150000, status: "a receber" }
      ],
      alertas: [
        { tipo: "valor_estimado", mensagem: "O valor do seguro do carro é uma estimativa.", origem: "movimentos.csv, linha 14" },
        { tipo: "pendencia_aberta", mensagem: "Confirmar o valor real do seguro do carro.", origem: "pendencias.md" }
      ],
      pendencias: { abertas: ["Confirmar o valor real do seguro do carro"], resolvidas: 3, arquivo_ausente: false },
      fonte: {
        arquivos: { "movimentos.csv": agora(0, "08:30:00"), "saldos.csv": agora(-1, "21:10:00"), "transferencias.csv": null, "pendencias.md": agora(-2, "18:00:00") },
        contagens: { movimentos: 31, contas: 2, vencimentos: 3 }
      }
    };
  }

  function atrasado(F) {
    F.vencimentos = [
      { data: iso(-5), descricao: "Conta de energia", categoria: "contas", valor: 21890, dias_restantes: -5, atrasado: true, status: "vencido" },
      { data: iso(0), descricao: "Mensalidade da academia", categoria: "saude", valor: 12900, dias_restantes: 0, atrasado: false, status: "vence hoje" },
      { data: iso(4), descricao: "Condomínio", categoria: "moradia", valor: 44610, dias_restantes: 4, atrasado: false, status: "a pagar" }
    ];
    var t = soma(F.vencimentos, "valor");
    F.gastos.a_pagar_mes = t; F.gastos.a_pagar_6m = t; F.serie_mensal[5].gasto_a_pagar = t;
    F.fonte.contagens.vencimentos = 3;
    F.alertas = [{ tipo: "pendencia_aberta", mensagem: "Confirmar se a conta de energia já foi paga.", origem: "pendencias.md" }];
    F.pendencias.abertas = ["Confirmar se a conta de energia já foi paga"];
    return F;
  }

  function divergente(F) {
    F.saldos.contas = [
      { conta: "Banco Azul", data: iso(-1), saldo: 842310, observacao: "extrato cita R$ 8.273,10", nao_confirmado: false, historico: false, idade_dias: 1 },
      { conta: "Carteira Digital", data: iso(-3), saldo: 120550, observacao: "NÃO CONFIRMADO", nao_confirmado: true, historico: false, idade_dias: 3 },
      { conta: "Reserva antiga", data: iso(-20), saldo: 500000, observacao: "histórico", nao_confirmado: false, historico: true, idade_dias: 20 }
    ];
    F.saldos.disponivel = 842310;
    F.saldos.contas_fora_do_disponivel = ["Carteira Digital", "Reserva antiga"];
    F.alertas = [
      { tipo: "saldo_divergente", mensagem: "O extrato citado na observação difere do saldo informado do Banco Azul.", origem: "saldos.csv, linha 3" },
      { tipo: "pago_sem_lancamento", mensagem: "Seguro do carro diz \"pago em\" na descrição, mas segue como a pagar.", origem: "movimentos.csv, linha 14" },
      { tipo: "saldo_nao_confirmado", mensagem: "Carteira Digital está marcada como não confirmada.", origem: "saldos.csv, linha 4" },
      { tipo: "saldo_velho", mensagem: "Reserva antiga tem saldo de 20 dias atrás.", origem: "saldos.csv, linha 5" },
      { tipo: "linha_invalida", mensagem: "Uma linha foi ignorada: data fora do formato AAAA-MM-DD.", origem: "movimentos.csv, linha 22" },
      { tipo: "pendencia_aberta", mensagem: "Conferir o extrato do Banco Azul.", origem: "pendencias.md" }
    ];
    F.pendencias.abertas = ["Conferir o extrato do Banco Azul", "Confirmar o saldo da Carteira Digital"];
    F.fonte.contagens.contas = 3;
    return F;
  }

  function semVenc(F) {
    F.vencimentos = []; F.gastos.a_pagar_mes = 0; F.gastos.a_pagar_6m = 0; F.serie_mensal[5].gasto_a_pagar = 0;
    F.fonte.contagens.vencimentos = 0; F.alertas = []; F.pendencias.abertas = [];
    F.movimentos_recentes = F.movimentos_recentes.filter(function (m) { return m.status === "pago"; });
    return F;
  }

  function vazio() {
    var s = [];
    for (var i = -5; i <= 0; i++) s.push({ mes: ym(i), recebido: 0, previsto: 0, gasto_pago: 0, gasto_a_pagar: 0 });
    return {
      gerado_em: agora(0, "08:40:00"), moeda: "BRL", unidade: "centavos", mes_atual: ym(0),
      saldos: { contas: [], disponivel: 0, contas_fora_do_disponivel: [], observacao: "Saldo bancário informado; não é o resultado das movimentações." },
      recebido: { mes: 0, previsto_mes: 0, total_6m: 0, previsto_6m: 0 },
      gastos: { pagos_mes: 0, a_pagar_mes: 0, pagos_6m: 0, a_pagar_6m: 0 },
      serie_mensal: s, receitas_x_gastos: { mes: ym(0), receitas: 0, gastos: 0 },
      categorias: [], vencimentos: [], movimentos_recentes: [], alertas: [],
      pendencias: { abertas: [], resolvidas: 0, arquivo_ausente: true },
      fonte: { arquivos: { "movimentos.csv": agora(0, "08:30:00"), "saldos.csv": agora(0, "08:30:00"), "transferencias.csv": null, "pendencias.md": null }, contagens: { movimentos: 0, contas: 0, vencimentos: 0 } }
    };
  }

  function velho(F) {
    F.gerado_em = agora(-4, "08:40:00");
    F.saldos.contas.forEach(function (c) { c.idade_dias += 4; });
    return F;
  }

  if (q === "carregando") window.FINANCAS_ESTADO = "carregando";
  else if (q === "erro") { /* arquivo ausente: window.FINANCAS não existe */ }
  else if (q === "atrasado") window.FINANCAS = atrasado(normal());
  else if (q === "divergente") window.FINANCAS = divergente(normal());
  else if (q === "sem_vencimentos") window.FINANCAS = semVenc(normal());
  else if (q === "vazio") window.FINANCAS = vazio();
  else if (q === "velho") window.FINANCAS = velho(normal());
  else window.FINANCAS = normal();
})();
