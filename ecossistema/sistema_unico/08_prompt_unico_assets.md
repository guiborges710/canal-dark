# 08. Prompts dos assets (estilo H) para colar no ChatGPT

Os prompts prontos estão em `prompts_chatgpt/` como arquivos .txt (texto puro, sem markdown). Abra, Ctrl+A, Ctrl+C, cole no ChatGPT e mande. Nenhum pede imagem de referência, anexo, aprovação ou confirmação.

- `lote_1.txt` a `lote_8.txt`: 66 imagens divididas em 8 lotes (9, 11, 8, 6, 8, 8, 7 e 9 imagens). Cada lote é completo e independente: já traz o bloco de estilo inteiro.
- `00_tudo_66_imagens.txt`: o prompt com as 66 imagens de uma vez (pode ser grande demais para o ChatGPT; se travar, use os lotes).

Recomendação: use os lotes, um depois do outro, na MESMA conversa (assim o ChatGPT vê as imagens anteriores e mantém o estilo sozinho, sem você anexar nada).

Depois de baixar as imagens, organizar e validar: `.venv\Scripts\python -I ecossistema\sistema_unico\ferramentas_assets\organizar_e_validar.py <pasta> --saida <pasta_saida> --prio P0,P1,P2`.

O arquivo `08_prompt_unico_assets_ANTIGO_quebrado.md` é a versão anterior (o bloco de estilo estava corrompido e os lotes 2 a 8 pediam imagens âncora). Não use.

Atualização de 2026-11-11 (pedido do Guilherme): os avatares agora citam o jogador real pelo nome e a fase (campo "Jogador" em cada ficha), para o cartoon sair parecido. O avatar "voce" continua genérico. Fases vindas de `05_pesquisa_jogadores_valverde.md`. Os arquivos 06 e 07 ainda trazem a regra antiga ("sem semelhança"); valem os .txt desta pasta.
