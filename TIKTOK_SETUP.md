# TikTok no fluxo do canal (passo a passo, uma vez só)

O canal agora posta nos dois: YouTube **e** TikTok. O modelo é o mesmo —
**upload automático, publicação manual**. No TikTok o vídeo sobe direto para os
**Rascunhos** da conta; você abre o app, revisa (legenda, som, capa, privacidade)
e publica. Nada vai ao ar sozinho.

Tudo isso você faz **uma vez**. Depois é só `python run.py publish --to tiktok`.

## 1. Conta TikTok do canal
Crie/escolha a conta TikTok do canal ("Contexto Explica"). É manual (verificação
por telefone). Deixe logada no navegador que você vai usar na autorização.

## 2. App de desenvolvedor (credenciais)
1. Entre em https://developers.tiktok.com e faça login com a conta do canal.
2. **Manage apps → Connect an app** (crie um app). Dê um nome, ex.: "Contexto Explica Poster".
3. Em **Products**, adicione **Content Posting API**.
   - Marque o escopo **`video.upload`** (sobe para rascunhos; não exige auditoria).
   - *(Opcional, mais tarde)* `video.publish` permite postar direto em público, mas
     só depois de o TikTok **auditar** o app. Para começar, fique no `video.upload`.
4. Em **Redirect URI**, cadastre exatamente: `https://localhost/callback`
   (precisa bater com `publish.tiktok_redirect_uri` no config).
5. Copie **Client key** e **Client secret**.

## 3. Chaves no .env
Preencha no arquivo `.env` (já tem as linhas prontas, gitignored):
```
TIKTOK_CLIENT_KEY=xxxxxxxx
TIKTOK_CLIENT_SECRET=xxxxxxxx
```

## 4. Primeira autorização
```
.venv/bin/python run.py publish --slug gen-z-frugal --to tiktok
```
Ele imprime um link. Abra no navegador (com a conta do canal logada), autorize.
O TikTok redireciona para `https://localhost/callback?code=...` — o navegador vai
mostrar "não foi possível acessar o site", é esperado. **Copie a URL inteira da
barra de endereço** (ou só o valor de `code=`) e cole no terminal.

Pronto: o token fica em `.tiktok_token.json` (gitignored) e é renovado sozinho.
Das próximas vezes não pede mais nada.

## Uso no dia a dia
```
python run.py publish --slug <pasta> --to youtube   # só YouTube (padrão)
python run.py publish --slug <pasta> --to tiktok     # só TikTok (rascunhos)
python run.py publish --slug <pasta> --to all        # os dois
```
Regra mantida: só publica se `auditoria.md` estiver **APROVADO** (regra do **Vini**).
O vídeo é o mesmo `video.mp4` 9:16 — serve para Shorts e TikTok sem reexportar.

## Observações
- Sem auditoria do app, o vídeo entra como **rascunho privado**. Tornar público é
  seu clique no app do TikTok (igual ao Studio no YouTube).
- Se houver imagens de IA que pareçam reais, ative o aviso de **conteúdo gerado por
  IA** nas opções de postagem do TikTok antes de publicar.
- A legenda sugerida (título + descrição + hashtags das tags) fica em
  `output/<slug>/upload_tiktok.json`.
