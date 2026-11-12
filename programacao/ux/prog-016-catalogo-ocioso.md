# PROG-016 · Catálogo com selo de estado · Desenho (Iniesta)

Para o **Endrick**. Base: `prog-003-aba-agentes.md` (alternativa A) e nota do **Thiago Silva** (`tecnico/PROG-016.md`). Só tela; nada de API nova.

## Onde fica o selo
Cada `.ag-item` do Catálogo (lista à esquerda) tem duas linhas:

```
[Nome do agente]                    [◐ Trabalhando]
 função curta (como hoje)
 vídeo-slug · etapa · há 2 min            <- só se trabalhando / na fila / falhou
```

- Selo na linha do nome, alinhado à direita (componente `seloEstado`: ícone + texto, nunca só cor).
- Linha de detalhe embaixo da função, só quando há job. Texto pequeno, uma linha, quebra se faltar espaço.
- Selo "Desativado" (já existe) fica ao lado do selo de estado, à esquerda dele. Os dois juntos são válidos.

## Os estados (ícone + texto)
| Estado | Ícone + texto | Linha de detalhe |
|---|---|---|
| ocioso | ○ Ocioso (cinza, discreto) | nenhuma. Sem vídeo, etapa ou tempo |
| trabalhando | ◐ Trabalhando | `<vídeo> · <etapa> · há N min` (tempo avança sozinho) |
| na fila | ⏳ Na fila | `<vídeo> · <etapa>`; sem tempo |
| falhou | ✕ Falhou | `<vídeo> · falhou em <etapa>` |
| espera você | ❚❚ Espera você | `<vídeo> · <etapa>` (quinto estado herdado da Ao vivo, para não divergir) |

Regras:
- Agente sem job e sem histórico = Ocioso puro. Nunca "Falhou" nem tempo.
- Vários jobs: mostra o primeiro e, se houver mais, acrescenta " · +2".
- Ordem da lista: não muda (alfabética/atual). Não reordenar por estado: o item pularia debaixo do dedo a cada 4 s. Quem quer ver só os ativos usa a aba Ao vivo.
- Linha com vídeo é clicável? Não. O item inteiro continua abrindo a ficha do agente. Quem quer ir ao vídeo usa a Ao vivo (nota no rodapé, abaixo).

## Estados da tela
- **Carregando** (antes da primeira resposta do Ao vivo): selo "… Verificando" cinza claro, nunca "Ocioso". A lista e a busca já funcionam.
- **Vazio** (catálogo sem agentes, ou busca sem resultado): "Nenhum agente encontrado. Limpe a busca para ver todos." Se o catálogo estiver vazio de verdade: "Nenhum agente cadastrado ainda."
- **Todos ociosos**: lista normal com todos "○ Ocioso" e, no rodapé da lista, a frase "Ninguém trabalhando agora. Para acompanhar quem estiver em ação, use a aba Ao vivo."
- **Erro na consulta de estado**: mantém os últimos selos e mostra no rodapé "(desatualizado) Não consegui atualizar os estados. Tentando de novo a cada poucos segundos." Se nunca houve resposta: todos os selos em "… Verificando" + o mesmo aviso, sem inventar "Ocioso".
- **Erro ao carregar a lista**: "Não consegui carregar os agentes. Recarregue a página; se continuar, veja se o Corte está aberto no computador." com botão "Tentar de novo".

## Atualização
Os selos mudam no lugar a cada ciclo, sem refazer a lista: busca digitada, rolagem, item selecionado e edição aberta ficam como estão. O selo muda de texto e ícone; sem animação de piscar (só o ícone ◐ pode girar devagar, desligado se o sistema pedir menos movimento).

## Celular (390 px)
- Uma coluna, sem rolagem lateral (`scrollWidth <= innerWidth`).
- Selo vai para a linha de baixo do nome se não couber ao lado (quebra, não corta). Linha de detalhe quebra em até 2 linhas; slug longo quebra em qualquer ponto.
- Alvo de toque do item: no mínimo 44 px de altura. Texto do selo nunca some no celular (só o ícone não basta).
- Rodapé de estado e avisos ocupam a largura toda.

## Acessibilidade
Selo com texto visível; o ícone fica `aria-hidden`. O item lê, por exemplo, "Neymar, Trabalhando, vídeo X, etapa Y".
