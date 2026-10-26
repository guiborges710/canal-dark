from pathlib import Path
import json,shutil,hashlib,zipfile,html,statistics
from PIL import Image
root=Path(__file__).parent
gen=Path('C:/Users/Guilherme/.codex/generated_images/01a135a9-4cf2-7680-9cba-11052c7ea282')
out=root/'testes/2026-10-18-novos'
out.mkdir(parents=True,exist_ok=True)
jobs={'casal':['9fa5215f-67a1-4ce3-8714-9dcb4d39cd4b','bf2e9e7f-6391-4c30-8959-5d495bf80ed4','f79ed6c6-d582-46c3-ac41-befb14cb8145'],'sozinha':['fdc35ded-8f7d-404f-96d1-a8d07ab219af','63d0a4f1-bf4d-4188-a706-7e9d59aeb7ea','dd2b9d98-ec93-43dc-b93b-8f46c3b70ed5']}
for theme,ids in jobs.items():
    folder=out/theme;folder.mkdir(exist_ok=True)
    assets=[]
    for i,id in enumerate(ids,1):
        p=folder/f'{i:02}.png';shutil.copy2(gen/f'exec-{id}.png',p)
        assets.append({'path':str(p),'dimensions':list(Image.open(p).size),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
    manifest={'status':'teste_local_nao_publicar_sem_autorizacao','theme':theme,'publication_authorized_now':False,'tool':'imagegen integrado','assets':assets,'qa':{'every_final_inspected':True,'central_3_4_crop':'texto, rostos, mãos e CTA dentro do recorte central','ui_overlap_review':'bordas externas com fundo desfocado; conteúdo principal centralizado','anatomy':'braços e mãos coerentes com posições; sem comparação ambígua de mãos','on_image_ai_text':False,'native_mobile_preview':'não realizada: sem upload neste pedido','native_ai_label_required_if_published':True},'prompt_set':'Fotos originais de adultos fictícios, uma cena por slide, tipografia branca sans-serif, frases curtas em português; casal andando, sentado e de costas; mulher olhando café, vitrine e livro. Revisão imagegen: reduzir fotografia e textos em conjunto para região central de 70%, fundo externo desfocado, CTA acima de 73% da altura, sem aviso textual de IA.'}
    (folder/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
    with zipfile.ZipFile(out/f'{theme}.zip','w',zipfile.ZIP_DEFLATED) as z:
        for p in folder.glob('*.png'):z.write(p,p.name)
gallery='<h1>Dois carrosséis de teste</h1><p>Somente revisão • 18/10/2026 • sem upload ou agendamento</p>'
for theme in jobs:
    gallery+=f'<h2>{"Fotos de casal sem travar" if theme=="casal" else "Foto sozinha sem olhar a câmera"}</h2><div class="slides">'+''.join(f'<a href="{theme}/{i:02}.png"><img src="{theme}/{i:02}.png" alt="{theme} slide {i}"></a>' for i in range(1,4))+'</div>'
(out/'preview.html').write_text('<!doctype html><meta charset="utf-8"><title>Testes Closet Minimal</title><style>body{font:16px system-ui;background:#151515;color:#eee;max-width:1300px;margin:30px auto;padding:20px}h1{font-size:28px}p{color:#bbb}.slides{display:grid;grid-template-columns:repeat(3,1fr);gap:14px}img{width:100%}@media(max-width:650px){.slides{grid-template-columns:1fr}}</style>'+gallery,encoding='utf-8')
def read(name):return json.loads((root/name).read_text(encoding='utf-8-sig'))
def save(name,data):(root/name).write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
config=read('config.json');config['editorial_update_2026_10_18']={'priority':'instrução mais recente do usuário substitui aviso textual obrigatório nos slides em instruções antigas','on_image_ai_disclaimer':False,'native_ai_label_required':True,'realistic_anatomy_required':True,'reject_impossible_hand_or_arm_positions':True,'square_safe_margins_still_required':True};save('config.json',config)
rows=[('13/10 11:56','Casal sem travar','7696166494614342932',575,9),('13/10 14:06','Onde colocar as mãos','7696199868771028225',602,6),('13/10 21:06','Casal no jantar','7696308052927974664',767,4),('14/10 08:00','Casal sem rosto','7696396971141188871',855,30),('14/10 12:00','Sozinha no café','7696397559325134088',485,6),('15/10 10:00','Casal no espelho','7696765073129229574',603,25),('15/10 15:00','Sozinha caminhando','7696765908387187976',440,7),('16/10 09:59','Casal sentado','7697249626709085447',582,3),('17/10 10:00','Casal no parque','7697476467810159890',248,4),('17/10 15:00','Para onde olhar','7697477269769522440',394,9),('18/10 12:22','Selfies de casal','7698028494801898768',19,1),('18/10 14:00','Sozinha na escada','7698029145527192840',3,0)]
totalviews=sum(r[3] for r in rows);totallikes=sum(r[4] for r in rows)
audit={'observed_date':'2026-10-18','studio_snapshot_local_time':'14:10 America/Sao_Paulo','baseline_date':'2026-10-13','baseline_followers':1192,'current_profile_followers':1192,'net_snapshot_change':0,'remaining_to_goal':808,'baseline_likes_displayed':'86.4K','current_likes_displayed':'86.5K','likes_profile_delta':'aproximadamente 100; contadores arredondados, não exato','closed_period':'2026-10-13 a 2026-10-17 conforme seletor do Studio','account_period':{'views_displayed':'6,9 mil','likes':119,'profile_views':27,'shares':8,'comments':None,'net_followers':-1},'new_posts_published':12,'scheduled_remaining':[{'id':'7698029651645435142','time':'2026-10-18T18:00:00-03:00'}],'new_post_views_sum':totalviews,'new_post_likes_sum':totallikes,'new_post_comments_sum':0,'post_rows':[dict(date=r[0],title=r[1],id=r[2],views=r[3],likes=r[4],comments=0) for r in rows],'caveats':['Métricas de conta no período incluem posts antigos; soma de posts novos é outra população e outro intervalo. Não somar os dois.','Seguidores líquidos -1 no período fechado e saldo0 entre snapshots têm cortes temporais diferentes. Ganhos e perdas brutos não disponíveis.','CSV Followers exportado possui datas deslocadas 12–16/10, enquanto seletor mostra13–17/10; preservado sem realinhar.','Não foi possível atribuir seguidores individuais aos posts novos.','Idades de posts diferentes; publicação18/10 ainda muito recente.']}
save('relatorio-dados-2026-10-18.json',audit)
shutil.copy2('C:/Users/Guilherme/Downloads/Followers_closetminimal.zip',root/'Followers-export-13-17-2026-10-18.zip')
queue=read('fila.json')
for p in queue['posts']:
    match=next((r for r in rows if r[2]==p.get('tiktok_id')),None)
    if match:p.update(status='publicado',verified_date='2026-10-18',provider_status_verified=f'TikTok Studio: Todos; {match[3]} views, {match[4]} curtidas',latest_metrics={'views':match[3],'likes':match[4],'comments':0,'observed_date':'2026-10-18'})
save('fila.json',queue)
state=read('estado.json');state.update(last_observation_date='2026-10-18',followers_observed=1192,likes_displayed='86.5K',scheduled_posts=['7698029651645435142'],published_posts=[r[2] for r in rows],next_slots=['2026-10-18T18:00:00-03:00'],last_native_publication_verified='7698029145527192840');save('estado.json',state)
analytics=read('analytics.json');analytics['latest_audit']=audit;save('analytics.json',analytics)
report=Path('C:/Users/Guilherme/Documents/canal-dark/reports/Relatorio Closet Minimal 13 a 18 outubro 2026.md')
md=f'''# Closet Minimal — balanço de 13 a 18/10/2026

O primeiro registro exato do agente é de **13/10/2026**, com **1.192 seguidores e 86,4 mil curtidas acumuladas**. A leitura atual do perfil em 18/10 mostra **1.192 seguidores e 86,5 mil curtidas**. Portanto, o saldo líquido entre esses registros é **zero seguidores**. Faltam **808** para 2.000; atingimos59,6% da meta. Não há evidência de crescimento líquido no período, e ainda não houve novo viral comparável aos dois antigos.

## Resultados medidos

**Conta inteira, período13–17/10 selecionado no TikTok Studio:** 6,9 mil visualizações (arredondadas),119 curtidas,8 compartilhamentos e27 visitas ao perfil. Comentários aparecem como “--”, portanto não foram tratados como zero. O painel de seguidores mostra **−1 líquido** nesse período fechado. A comparação do Studio indica +205,6% de views e +561,1% de curtidas frente ao seu intervalo de comparação; isso não isola o efeito do agente. Hoje18/10 ainda estava desabilitado no seletor de datas, então seus resultados não entram nesses totais consolidados.

**Somente os12 posts publicados pelo agente, acumulado até a leitura de18/10 por volta de14h10:** **{totalviews:,} visualizações**, **{totallikes} curtidas** e0 comentários nos contadores por publicação. A taxa agregada de curtidas/views é {totallikes/totalviews*100:.2f}%. Não são pessoas únicas. Esse conjunto inclui posts de hoje e exclui conteúdos antigos; não deve ser somado nem comparado diretamente com os totais de conta acima.

As curtidas totais do perfil avançaram uma casa de86,4K para86,5K: aproximadamente100, sem precisão para afirmar um ganho exato. O saldo zero entre snapshots e o−1 no painel são medições com cortes diferentes; não são ganhos/perdas brutos. O export de seguidores não fornece o número separado de pessoas que seguiram e deixaram de seguir. Suas linhas vieram datadas12–16/10, diferente do seletor13–17/10; mantivemos o arquivo original e não deslocamos as datas por conta própria.

## Publicações e operação

Foram **13 carrosséis enviados à plataforma:12 publicados e1 ainda agendado**, o de looks de casal em18/10 às18h. Houve posts em todos os dias13–18/10:3,2,2,1,2 e2 publicados respectivamente. O dia16 teve apenas um post confirmado; portanto, a cadência de dois por dia não foi cumprida integralmente. Os dois uploads antigos de14/10 excluídos para correção não contam como publicações adicionais.

''' 
for d,title,tid,v,l in rows:md+=f'- **{d} — {title}:** {v} views, {l} curtidas. [Abrir post](https://www.tiktok.com/@closetminimal/photo/{tid}).\n'
md+='''
## O que funcionou e o que ainda falta

O melhor resultado recente é **casal sem rosto:855 views e30 curtidas**. Depois, jantar tem767views/4curtidas e espelho603views/25curtidas. Espelho tem proporção de curtidas maior que jantar, mas essas diferenças não demonstram conversão em seguidores nem causalidade; os posts têm idades distintas e amostra pequena. O post de hoje às12h22 e o das14h ainda são recentes demais para julgar.

Os dois virais usados como referência **já existiam antes do agente**: publicados em25/11/2025 e15/12/2025, com611,5mil e536,5mil views observadas em13/10. Não são resultados desta operação. Os conteúdos novos ainda estão longe desse alcance.

Executamos análise das referências do próprio perfil, testes de colagens e de fotos individuais, upload e agendamento nativos, conferência de conta antes dos envios, reconciliação da fila e pesquisa de concorrentes com links. Abandonamos o Metricool por pedido do usuário. Após o recorte móvel de14/10, os dois agendados foram refeitos em formato quadrado com margens maiores. Em18/10, entregamos primeiro um teste de3slides; ele foi rejeitado por aviso de IA na imagem e por ambiguidade anatômica. Esse teste não foi publicado.

Agora foram criados **dois novos testes de3slides cada**, sem aviso textual de IA, com revisão de anatomia e fundo desfocado nas margens. Permanecem locais, sem publicação/autorização de envio. O rótulo nativo de IA continua previsto para eventual publicação. A revisão local de corte protege conteúdo no centro; a prévia nativa será necessária antes de qualquer upload final. Não há comprovação por screenshot de celular dos últimos posts; não afirmamos que o recorte foi eliminado em toda interface.

## Próximo teste recomendado

Avaliar os dois carrosséis locais e escolher a linha mais coerente. Se aprovados para publicar, medir views, curtidas, salvamentos, compartilhamentos, visitas ao perfil e seguidores atribuídos nas mesmas janelas de24h e72h. Não aumentar volume só para compensar alcance baixo. O dado prioritário é conversão em seguidores, ainda não demonstrada. Não existe base para prometer data de2.000 seguidores nem viralização.

## Fontes e evidências

- Perfil nativo @closetminimal, conferido18/10/2026; analytics.json de13/10 preservado como baseline.
- TikTok Studio, lista de conteúdo e intervalo personalizado13–17/10; evidências audit-*.txt e audit-*.png em tiktok/closetminimal/.
- Export original Followers-export-13-17-2026-10-18.zip e relatorio-dados-2026-10-18.json.
- fila.json e manifests locais, com IDs e hashes dos ativos.
'''
report.write_text(md,encoding='utf-8')
rowshtml=''.join(f'<tr><td>{d}</td><td><a href="https://www.tiktok.com/@closetminimal/photo/{tid}">{html.escape(title)}</a></td><td>{v}</td><td>{l}</td></tr>' for d,title,tid,v,l in rows)
page=f'''<!doctype html><html lang="pt-BR"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Closet Minimal — balanço</title><style>body{{font:16px/1.6 system-ui;color:#242424;background:#f4f2ed;margin:0}}main{{max-width:1050px;margin:auto;padding:36px}}h1{{font-size:32px;line-height:1.2}}h2{{font-size:23px;margin-top:36px}}.metrics{{display:flex;gap:30px;flex-wrap:wrap;border-block:1px solid #ccc;padding:22px 0}}.metrics strong{{display:block;font-size:28px}}small{{color:#626262}}a{{color:#415f45}}table{{border-collapse:collapse;width:100%;font-size:14px}}td,th{{text-align:left;padding:10px;border-bottom:1px solid #d2d2d2}}details{{margin:20px 0}}summary{{cursor:pointer;font-weight:600}}.note{{border-left:3px solid #8f6749;padding-left:16px}}.gallery{{display:grid;grid-template-columns:repeat(3,1fr);gap:12px}}img{{width:100%}}@media(max-width:650px){{main{{padding:20px}}.gallery{{grid-template-columns:1fr}}h1{{font-size:26px}}}}</style><main><small>@closetminimal · 13 a18 de outubro de2026</small><h1>Publicamos todos os dias.<br>O saldo de seguidores ainda é zero.</h1><div class="metrics"><div><strong>1.192 → 1.192</strong>seguidores entre snapshots</div><div><strong>808</strong>faltam para2.000</div><div><strong>12 +1</strong>publicados + agendado</div></div><h2>Conta inteira · 13–17/10</h2><div class="metrics"><div><strong>6,9mil</strong>views arredondadas</div><div><strong>119</strong>curtidas</div><div><strong>8</strong>compartilhamentos</div><div><strong>27</strong>visitas ao perfil</div></div><p class="note">Seguidores líquidos no painel:−1 no período fechado. Snapshot atual de18/10 voltou a1.192. Hoje ainda não está consolidado no seletor. Ganhos e perdas brutos não foram disponibilizados.</p><h2>Posts do agente · acumulado até18/10 ~14h10</h2><p><b>{totalviews:,} views · {totallikes} curtidas ·0 comentários</b>. Outra população e outro intervalo: não somar com os resultados da conta inteira. A curtida total do perfil mudou de86,4K para86,5K; diferença aproximada, não exata.</p><details open><summary>Ver12 publicações e seus resultados</summary><table><thead><tr><th>Publicação</th><th>Tema</th><th>Views</th><th>Curtidas</th></tr></thead><tbody>{rowshtml}</tbody></table></details><h2>Leitura do resultado</h2><p>Casal sem rosto lidera os posts novos com855views e30curtidas. Os dois virais antigos antecedem o agente:611,5mil e536,5mil views na observação inicial. Ainda não houve novo resultado comparável nem conversão líquida demonstrada.</p><p>Houve posts em todos os dias, porém16/10 teve apenas um confirmado. Corrigimos recortes, migramos para envio nativo e pesquisamos referências. Um post permanece agendado parahoje18h. Os dois testes abaixo não foram enviados.</p><h2>Dois novos carrosséis para revisão</h2><p>Sem texto de IA na imagem; anatomia e área central revisadas. Rótulo nativo de IA e prévia móvel ainda necessários para eventual publicação.</p>'''
for theme in jobs:
    page+=f'<h3>{"Casal sem pose travada" if theme=="casal" else "Sozinha sem olhar para a câmera"}</h3><div class="gallery">'+''.join(f'<a href="../tiktok/closetminimal/testes/2026-10-18-novos/{theme}/{i:02}.png"><img alt="{theme} slide{i}" src="../tiktok/closetminimal/testes/2026-10-18-novos/{theme}/{i:02}.png"></a>' for i in range(1,4))+'</div>'
page+='<h2>Próxima medição</h2><p>Comparar resultados após24h e72h, com foco em seguidores atribuídos e visitas ao perfil. Não há base para prometer viralização ou prazo para2.000 seguidores.</p><details><summary>Limites e evidências</summary><p>Views e curtidas são contadores acumulados, não pessoas únicas. Não há atribuição causal ao agente. O export de seguidores veio com datas12–16/10 apesar do seletor13–17/10: preservado sem realinhamento. Não há comprovação móvel de recorte para todas as publicações.</p><p>Fontes: perfil e TikTok Studio, snapshots audit-*.txt/png, analytics.json inicial, fila.json e manifests. <a href="Relatorio Closet Minimal 13 a 18 outubro 2026.md">Relatório completo</a> · <a href="../tiktok/closetminimal/relatorio-dados-2026-10-18.json">Dados estruturados</a></p></details></main></html>'
report.with_suffix('.html').write_text(page,encoding='utf-8')
print(json.dumps({'views':totalviews,'likes':totallikes,'published':len(rows),'report':str(report),'tests':str(out)},ensure_ascii=False))
