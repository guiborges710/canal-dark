/* Tela de Clipes (PROG-033c). Gerencia projetos de clipes, fluxo em tempo real, filtros e ações.
   Dados carregados via /api/clipes (mock se rota não existir), SSE em /api/eventos.
   Estado local: filtro, tema, selecionado, carregando. */
(function () {
  var app = document.getElementById("app"), esc = B.esc;
  var KT = "ce_h_cli_tema", KF = "ce_h_cli_filtro", KS = "ce_h_cli_selec";
  GH.tema(KT, "claro");

  var S = {
    fase: "carregando", // carregando | pronto | erro | vazio
    filtro: "todas", // todas | fazendo | esperando_voce | prontos | erro
    selecionado: null,
    projetos: [],
    sse: null,
    motivo: "",
    area: "clipes"
  };

  var FILTROS = ["todas", "fazendo", "esperando_voce", "prontos", "erro"];
  var CORES_STATUS = {
    "fazendo": { cor: "--c-rodando", label: "● Rodando", class: "e-rodando" },
    "esperando_voce": { cor: "--c-pendente", label: "⏳ Espera", class: "e-pendente" },
    "prontos": { cor: "--c-ok", label: "✓ Pronto", class: "e-ok" },
    "erro": { cor: "--c-erro", label: "⚠ Erro", class: "e-erro" }
  };

  /* ---------- carregamento de dados ---------- */
  function carregarProjetos() {
    S.fase = "carregando";
    render();

    var url = "/api/clipes";
    fetch(url)
      .then(function (r) {
        if (!r.ok) throw new Error("Status " + r.status);
        return r.json();
      })
      .then(function (d) {
        S.projetos = d.projetos || [];
        S.fase = S.projetos.length > 0 ? "pronto" : "vazio";
        conectarSSE();
        render();
      })
      .catch(function (e) {
        // Tenta com dados de demo para teste
        return fetch("clipes_demo.json")
          .then(function (r) {
            if (!r.ok) throw new Error("Demo também não disponível");
            return r.json();
          })
          .then(function (d) {
            S.projetos = d.projetos || [];
            S.fase = S.projetos.length > 0 ? "pronto" : "vazio";
            conectarSSE();
            render();
          })
          .catch(function (e2) {
            S.fase = "erro";
            S.motivo = "Não foi possível carregar os projetos (nem a API nem os dados de demo)";
            render();
          });
      });
  }

  function conectarSSE() {
    if (S.sse) return;
    try {
      S.sse = new EventSource("/api/eventos");
      S.sse.onmessage = function (evt) {
        try {
          var evento = JSON.parse(evt.data);
          atualizarCartao(evento.slug);
        } catch (e) {}
      };
      S.sse.onerror = function () {
        S.sse = null;
      };
    } catch (e) {}
  }

  function atualizarCartao(slug) {
    var idx = S.projetos.findIndex(function (p) { return p.slug === slug; });
    if (idx < 0) return;

    // Piscar o cartão por 1.5s
    var cartao = document.querySelector('[data-slug="' + slug + '"]');
    if (cartao) {
      cartao.classList.add("atualizado");
      setTimeout(function () {
        cartao.classList.remove("atualizado");
      }, 1500);
    }
  }

  /* ---------- atalhos de teclado ---------- */
  function instalarAtalhos() {
    document.addEventListener("keydown", function (e) {
      if (e.target !== document.body && e.target !== app) return;

      if ((e.ctrlKey || e.metaKey) && e.key === "k") {
        e.preventDefault();
        var input = document.querySelector(".cli-busca");
        if (input) input.focus();
      } else if (e.key === "n") {
        e.preventDefault();
        modalNovoProject();
      } else if (e.key === "f") {
        e.preventDefault();
        alternarFiltro();
      } else if (e.key === "a" && S.selecionado) {
        e.preventDefault();
        var proj = S.projetos.find(function (p) { return p.slug === S.selecionado; });
        if (proj && proj.status === "esperando_voce") {
          aprovarProjeto(S.selecionado);
        }
      } else if (e.key === "r" && S.selecionado) {
        e.preventDefault();
        var proj = S.projetos.find(function (p) { return p.slug === S.selecionado; });
        if (proj && (proj.status === "esperando_voce" || proj.status === "erro")) {
          rejeitarProjeto(S.selecionado);
        }
      } else if (/^[1-5]$/.test(e.key)) {
        e.preventDefault();
        var fIdx = +e.key - 1;
        if (fIdx < FILTROS.length) {
          S.filtro = FILTROS[fIdx];
          salvarFiltro();
          render();
        }
      } else if (e.key === "j" || e.key === "k") {
        e.preventDefault();
        navegarProjeto(e.key === "j" ? -1 : 1);
      }
    });
  }

  function alternarFiltro() {
    var idx = FILTROS.indexOf(S.filtro);
    S.filtro = FILTROS[(idx + 1) % FILTROS.length];
    salvarFiltro();
    render();
  }

  function navegarProjeto(dir) {
    var visíveis = projetosFiltrados();
    if (visíveis.length === 0) return;
    var idx = S.selecionado ? visíveis.findIndex(function (p) { return p.slug === S.selecionado; }) : -1;
    idx = (idx + dir + visíveis.length) % visíveis.length;
    S.selecionado = visíveis[idx].slug;
    try { localStorage.setItem(KS, S.selecionado); } catch (e) {}
    render();
  }

  /* ---------- filtro e busca ---------- */
  function projetosFiltrados() {
    var q = (document.querySelector(".cli-busca") || {}).value || "";
    return S.projetos.filter(function (p) {
      var match = S.filtro === "todas" || p.status === S.filtro;
      if (!match) return false;
      if (!q) return true;
      return p.slug.includes(q) || p.titulo.toLowerCase().includes(q.toLowerCase()) || (p.fonte.criador || "").toLowerCase().includes(q.toLowerCase());
    });
  }

  function salvarFiltro() {
    try { localStorage.setItem(KF, S.filtro); } catch (e) {}
  }

  function carregarFiltro() {
    try { S.filtro = localStorage.getItem(KF) || "todas"; } catch (e) {}
  }

  /* ---------- ações ---------- */
  function modalNovoProject() {
    var overlay = document.createElement("div");
    overlay.className = "modal-overlay";
    overlay.innerHTML = tmplModalNovoProject();
    document.body.appendChild(overlay);

    // Instalar handlers do modal
    var btFechar = overlay.querySelector(".modal-fechar");
    var btCancelar = overlay.querySelector(".modal-cancelar");
    var btIniciar = overlay.querySelector(".modal-iniciar");
    var campoUrl = overlay.querySelector(".modal-url");
    var campoAutor = overlay.querySelector(".modal-autor");
    var campoAutorizacao = overlay.querySelector(".modal-autorizacao");
    var campoPerfil = overlay.querySelector(".modal-perfil");
    var msgErro = overlay.querySelector(".modal-erro");

    function fecharModal() {
      overlay.remove();
    }

    function validarUrl(url) {
      if (!url.trim()) return "URL não pode estar vazia";
      var urlObj;
      try {
        urlObj = new URL(url);
      } catch (e) {
        return "URL inválida";
      }
      var host = urlObj.hostname.toLowerCase();
      if (!host.includes("youtube") && !host.includes("twitch") && !host.includes("youtu.be")) {
        return "Suporte apenas para YouTube e Twitch";
      }
      return null;
    }

    function validarAutor(autor) {
      if (!autor.trim()) return "Autor não pode estar vazio";
      return null;
    }

    function iniciarProjeto(evt) {
      evt.preventDefault();
      msgErro.textContent = "";

      var url = campoUrl.value;
      var autor = campoAutor.value;
      var autorizacao = campoAutorizacao.value;
      var perfil = campoPerfil.value;

      var erroUrl = validarUrl(url);
      if (erroUrl) {
        msgErro.textContent = erroUrl;
        campoUrl.focus();
        return;
      }

      var erroAutor = validarAutor(autor);
      if (erroAutor) {
        msgErro.textContent = erroAutor;
        campoAutor.focus();
        return;
      }

      // Desabilitar botão durante envio
      btIniciar.disabled = true;
      btIniciar.textContent = "⏳ Enviando...";

      var payload = {
        url: url,
        autor: autor,
        autorizacao: autorizacao,
        perfil: perfil
      };

      fetch("/api/clipes/novo", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      })
        .then(function (r) {
          if (!r.ok) throw new Error("Status " + r.status);
          return r.json();
        })
        .then(function (data) {
          if (data.slug) {
            fecharModal();
            // Recarregar a lista de projetos
            carregarProjetos();
            // Mostrar toast de sucesso
            var toast = document.getElementById("toast");
            if (toast) {
              toast.innerHTML = '<div class="toast-item" style="background: var(--c-ok); color: #fff; padding: 12px 16px; border-radius: 8px; margin-bottom: 8px;">' +
                '✓ Projeto iniciado: ' + esc(data.slug) + '</div>';
              setTimeout(function () {
                toast.innerHTML = "";
              }, 3000);
            }
          } else {
            throw new Error("Sem slug na resposta");
          }
        })
        .catch(function (e) {
          btIniciar.disabled = false;
          btIniciar.textContent = "Iniciar";
          msgErro.textContent = "Erro ao criar projeto: " + e.message;
        });
    }

    btFechar.addEventListener("click", fecharModal);
    btCancelar.addEventListener("click", fecharModal);
    btIniciar.addEventListener("click", iniciarProjeto);

    // Fechar ao clicar fora
    overlay.addEventListener("click", function (evt) {
      if (evt.target === overlay) {
        fecharModal();
      }
    });

    // Foco inicial
    campoUrl.focus();
  }

  function aprovarProjeto(slug) {
    alert("Aprovando: " + slug);
  }

  function rejeitarProjeto(slug) {
    alert("Rejeitando: " + slug);
  }

  function abrirPainel8767() {
    window.open("http://127.0.0.1:8767", "_blank");
  }

  /* ---------- renderização ---------- */
  function render() {
    if (S.fase === "carregando") {
      app.innerHTML = tmplCarregando();
    } else if (S.fase === "vazio") {
      app.innerHTML = tmplVazio();
    } else if (S.fase === "erro") {
      app.innerHTML = tmplErro();
    } else {
      app.innerHTML = tmplPrincipal();
    }
    instalarHandlers();
  }

  function instalarHandlers() {
    // Tema
    var btTema = document.querySelector("#tema");
    if (btTema) {
      btTema.addEventListener("click", function () {
        GH.tema(KT).alternar();
        render();
      });
    }

    // Filtros
    var btFiltro = document.querySelectorAll(".cli-filtro");
    btFiltro.forEach(function (b) {
      b.addEventListener("click", function () {
        S.filtro = this.dataset.filtro;
        salvarFiltro();
        render();
      });
    });

    var btNovoP = document.querySelector(".cli-novo");
    if (btNovoP) {
      btNovoP.addEventListener("click", modalNovoProject);
    }

    var btPainel = document.querySelector(".cli-painel");
    if (btPainel) {
      btPainel.addEventListener("click", abrirPainel8767);
    }

    var buscaInput = document.querySelector(".cli-busca");
    if (buscaInput) {
      buscaInput.addEventListener("input", render);
    }

    var projetoLin = document.querySelectorAll(".cli-cartao");
    projetoLin.forEach(function (lin) {
      lin.addEventListener("click", function () {
        S.selecionado = this.dataset.slug;
        try { localStorage.setItem(KS, S.selecionado); } catch (e) {}
        render();
      });
    });

    var btAprovar = document.querySelectorAll(".cli-aprovar");
    btAprovar.forEach(function (b) {
      b.addEventListener("click", function (evt) {
        evt.stopPropagation();
        aprovarProjeto(this.dataset.slug);
      });
    });

    var btRejeitar = document.querySelectorAll(".cli-rejeitar");
    btRejeitar.forEach(function (b) {
      b.addEventListener("click", function (evt) {
        evt.stopPropagation();
        rejeitarProjeto(this.dataset.slug);
      });
    });
  }

  function tmplCarregando() {
    return '<div class="papel">' +
      '<div class="cli-cab"><h1 class="pag">🎬 Clipes</h1><p class="sub">Carregando projetos...</p></div>' +
      '<div class="cli-esq">Carregando...</div>' +
      '</div>';
  }

  function tmplVazio() {
    return '<div class="papel">' +
      '<div class="cli-cab"><h1 class="pag">🎬 Clipes</h1><p class="sub">Nenhum projeto iniciado</p></div>' +
      '<div class="toque"><p>Você ainda não iniciou nenhum projeto de clipes</p>' +
      '<button class="cli-novo" style="padding: 8px 16px; background: var(--sinal); color: #0E1A24; border: 0; border-radius: 8px; font-weight: 600; cursor: pointer;">+ Novo Projeto</button>' +
      '</div></div>';
  }

  function tmplErro() {
    return '<div class="papel">' +
      '<div class="cli-cab"><h1 class="pag">🎬 Clipes</h1><p class="sub">Erro ao carregar</p></div>' +
      '<div class="toque"><p><strong>⚠ Erro:</strong> ' + esc(S.motivo) + '</p>' +
      '<p style="font-size: 13px; color: var(--mut);">Verifique se <code>python -m clipes painel</code> está rodando em <code>http://127.0.0.1:8767</code></p>' +
      '</div></div>';
  }

  function tmplIlha() {
    var escuro = document.documentElement.dataset.tema === "escuro";
    var nav = B.menu.map(function (m, i) { return '<a class="aba" href="#' + m.id + '"' + (S.area === m.id ? ' aria-current="page"' : "") + '>' + B.icon(m.ic, 18) + "<span>" + esc(m.nome) + "</span></a>"; }).join("");
    return '<header class="ilha"><div class="i-in"><div class="i-top"><div class="marca">' + '<span>Clipes</span></div>' +
      '<div class="i-ferr"><button class="bt-i ic1" type="button" id="tema" aria-label="Alternar tema">' + B.icon(escuro ? "sun" : "moon", 20) + "</button></div></div>" +
      '<nav class="i-nav" aria-label="Grupos">' + nav + "</nav>" +
      "</div></header>";
  }

  function tmplPrincipal() {
    var visíveis = projetosFiltrados();
    var fazendo = S.projetos.filter(function (p) { return p.status === "fazendo"; }).length;
    var espera = S.projetos.filter(function (p) { return p.status === "esperando_voce"; }).length;
    var erros = S.projetos.filter(function (p) { return p.status === "erro"; }).length;

    var html = tmplIlha() + '<div class="papel">' +
      '<div class="cli-cab">' +
      '<h1 class="pag">🎬 Clipes (Pelé)</h1>' +
      '<p class="sub">📊 ' + fazendo + ' fazendo | ⏱ ' + espera + ' espera você' + (erros > 0 ? ' | ⚠ ' + erros + ' erro' : '') + '</p>' +
      '</div>' +
      '<div class="cli-acoes">' +
      '<button class="cli-novo">+ Novo projeto</button>' +
      '<button class="cli-painel">📊 Abrir painel 8767</button>' +
      '<button>⬇ Downloads</button>' +
      '<button>📋 Baixar ZIP</button>' +
      '</div>' +
      '<div class="chips-f">';

    FILTROS.forEach(function (filt) {
      var label = { "todas": "Todas", "fazendo": "Fazendo", "esperando_voce": "Esperando você", "prontos": "Prontos", "erro": "Erro" }[filt] || filt;
      html += '<button class="cf cli-filtro" data-filtro="' + filt + '" aria-pressed="' + (S.filtro === filt ? 'true' : 'false') + '">' + label + '</button>';
    });
    html += '</div>' +
      '<input type="text" class="cli-busca" placeholder="Buscar projeto (Ctrl K)..." style="width: 100%; min-height: 40px; padding: 8px 12px; border: 1px solid var(--linha); border-radius: 8px; margin-bottom: 12px;">' +
      '<div class="lista">';

    if (visíveis.length === 0) {
      html += '<div style="padding: 24px; text-align: center; color: var(--mut);">Nenhum projeto neste filtro</div>';
    } else {
      visíveis.forEach(function (proj, i) {
        html += tmplCartao(proj, i === 0);
      });
    }

    html += '</div></div>';
    return html;
  }

  function tmplCartao(proj, selecionado) {
    var status = CORES_STATUS[proj.status] || { cor: "--c-backlog", label: "?", class: "e-backlog" };
    var duracao = proj.tempo_inicio ? calcularDuracao(proj.tempo_inicio) : "";
    var temBloqueio = proj.status === "esperando_voce";

    var html = '<button class="lin cli-cartao" data-slug="' + esc(proj.slug) + '" style="cursor: pointer; border-bottom: 2px solid ' + (selecionado ? 'var(--sinal)' : 'var(--linha)') + ';">' +
      '<div style="display: flex; justify-content: space-between; align-items: start; width: 100%;">' +
      '<div style="flex: 1; min-width: 0;">' +
      '<div style="display: flex; gap: 10px; align-items: center;">' +
      '<strong>[' + esc(proj.slug) + ']</strong> <span>' + esc(proj.titulo || "Sem título") + '</span>' +
      '<span class="est ' + status.class + '"><span>' + status.label + '</span></span>' +
      '</div>' +
      '<div style="font-size: 13px; color: var(--mut); margin-top: 4px;">' +
      'Fonte: ' + esc(proj.fonte.criador || "?") + ' | Rivaldo: ' + (proj.notas.rivaldo || "-") + ' | Tempo: ' + duracao +
      '</div>';

    if (temBloqueio && proj.agente_nome) {
      html += '<div style="font-size: 13px; margin-top: 6px; padding: 6px 8px; background: rgba(255, 0, 0, 0.1); border-radius: 4px; border-left: 3px solid var(--c-erro);">' +
        '<strong style="color: var(--c-erro);">🔴 BLOQUEIO:</strong> Você precisa aprovar (via ' + esc(proj.agente_nome) + ')' +
        '</div>';
    }

    html += '</div></div>';

    if (temBloqueio) {
      html += '<div style="margin-top: 8px; display: flex; gap: 4px;">' +
        '<button class="cli-aprovar" data-slug="' + esc(proj.slug) + '" style="padding: 4px 8px; background: var(--c-ok); color: #fff; border: 0; border-radius: 4px; font-size: 12px; cursor: pointer;">✓ Aprovar [A]</button>' +
        '<button class="cli-rejeitar" data-slug="' + esc(proj.slug) + '" style="padding: 4px 8px; background: var(--c-erro); color: #fff; border: 0; border-radius: 4px; font-size: 12px; cursor: pointer;">✗ Rejeitar</button>' +
        '</div>';
    }

    html += '</button>';
    return html;
  }

  function tmplModalNovoProject() {
    return '<div class="modal-bg" style="position: fixed; inset: 0; background: rgba(0, 0, 0, 0.5); z-index: 100; display: flex; align-items: center; justify-content: center;">' +
      '<div class="modal-box" style="background: var(--card); border-radius: 12px; padding: 0; width: min(480px, calc(100vw - 32px)); box-shadow: 0 12px 48px rgba(0, 0, 0, 0.3); display: flex; flex-direction: column;">' +
      '<div class="modal-cabecalho" style="display: flex; justify-content: space-between; align-items: center; padding: 16px 20px; border-bottom: 1px solid var(--linha); flex-shrink: 0;">' +
      '<h2 style="margin: 0; font: 600 18px var(--num); flex: 1;">Novo Projeto de Clipes</h2>' +
      '<button class="modal-fechar" type="button" aria-label="Fechar" style="width: 40px; height: 40px; min-height: 0; padding: 0; background: transparent; border: 0; cursor: pointer; display: flex; align-items: center; justify-content: center; color: var(--mut);">' + B.icon("close", 20) + '</button>' +
      '</div>' +
      '<form class="modal-form" style="padding: 20px; overflow-y: auto; flex: 1;">' +
      '<div class="modal-erro" style="display: none; padding: 12px; background: color-mix(in srgb, var(--c-erro) 15%, var(--card)); color: var(--c-erro); border: 1px solid var(--c-erro); border-radius: 8px; margin-bottom: 16px; font-size: 14px; font-weight: 600;"></div>' +
      '<div class="modal-field" style="margin-bottom: 16px;">' +
      '<label style="display: block; font: 600 14px var(--txt); margin-bottom: 6px;">URL do vídeo*</label>' +
      '<input type="text" class="modal-url" placeholder="https://youtube.com/watch?v=..." style="width: 100%; min-height: 40px; padding: 10px 12px; border: 1px solid var(--linha-f); background: var(--papel); color: var(--tx); border-radius: 8px; font: inherit;">' +
      '<span style="display: block; margin-top: 4px; font-size: 12px; color: var(--mut);">YouTube, Twitch ou similar</span>' +
      '</div>' +
      '<div class="modal-field" style="margin-bottom: 16px;">' +
      '<label style="display: block; font: 600 14px var(--txt); margin-bottom: 6px;">Autor (criador)*</label>' +
      '<input type="text" class="modal-autor" placeholder="Nome do criador" style="width: 100%; min-height: 40px; padding: 10px 12px; border: 1px solid var(--linha-f); background: var(--papel); color: var(--tx); border-radius: 8px; font: inherit;">' +
      '</div>' +
      '<div class="modal-field" style="margin-bottom: 16px;">' +
      '<label style="display: block; font: 600 14px var(--txt); margin-bottom: 6px;">Autorização</label>' +
      '<select class="modal-autorizacao" style="width: 100%; min-height: 40px; padding: 10px 12px; border: 1px solid var(--linha-f); background: var(--papel); color: var(--tx); border-radius: 8px; font: inherit;">' +
      '<option value="sem_autorizacao">Sem autorização (Fair use)</option>' +
      '<option value="dominio_publico">Domínio Público</option>' +
      '<option value="licenca">Licença (CC, etc)</option>' +
      '<option value="parceria">Parceria</option>' +
      '<option value="fair_use">Fair Use Confirmado</option>' +
      '</select>' +
      '</div>' +
      '<div class="modal-field" style="margin-bottom: 20px;">' +
      '<label style="display: block; font: 600 14px var(--txt); margin-bottom: 6px;">Perfil</label>' +
      '<select class="modal-perfil" style="width: 100%; min-height: 40px; padding: 10px 12px; border: 1px solid var(--linha-f); background: var(--papel); color: var(--tx); border-radius: 8px; font: inherit;">' +
      '<option value="geral">Geral</option>' +
      '<option value="gta6">GTA 6</option>' +
      '</select>' +
      '</div>' +
      '</form>' +
      '<div class="modal-rodape" style="display: flex; justify-content: flex-end; gap: 8px; padding: 12px 20px; border-top: 1px solid var(--linha); flex-shrink: 0;">' +
      '<button class="modal-cancelar" type="button" style="min-height: 40px; padding: 0 16px; border: 1px solid var(--linha-f); background: var(--card); border-radius: 8px; font-weight: 600; cursor: pointer;">Cancelar</button>' +
      '<button class="modal-iniciar" type="button" style="min-height: 40px; padding: 0 24px; background: var(--sinal); color: #0E1A24; border: 0; border-radius: 8px; font-weight: 600; cursor: pointer; font: 600 14px var(--txt);">Iniciar</button>' +
      '</div>' +
      '</div>' +
      '</div>';
  }

  function calcularDuracao(iso) {
    try {
      var agora = new Date();
      var inicio = new Date(iso);
      var diff = Math.floor((agora - inicio) / 1000); // segundos

      if (diff < 60) return diff + "s";
      if (diff < 3600) return Math.floor(diff / 60) + "m";
      if (diff < 86400) return Math.floor(diff / 3600) + "h " + Math.floor((diff % 3600) / 60) + "m";
      return Math.floor(diff / 86400) + "d";
    } catch (e) {
      return "?";
    }
  }

  /* ---------- inicialização ---------- */
  carregarFiltro();
  try { S.selecionado = localStorage.getItem(KS); } catch (e) {}
  carregarProjetos();
  instalarAtalhos();
})();
