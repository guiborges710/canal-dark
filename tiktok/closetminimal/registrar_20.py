from pathlib import Path
import json,hashlib
from PIL import Image
r=Path(__file__).parent
def read(p):return json.loads((r/p).read_text(encoding='utf-8-sig'))
def save(p,d):(r/p).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
plan=read('plano-2026-10-20.json');queue=read('fila.json')
data=[('1000','7698574727127878930','Fotos de casal sem beijo: conexão nos detalhes 🤍','Olhando juntos ou rindo: qual combina com vocês? Comenta 🤍 Aproximem os ombros, olhem para o mesmo lado ou conversem até a risada aparecer. Adaptem as ideias ao conforto dos dois. Não precisa roupa igual: uma cor em comum já conecta os looks. Curtiu? Deixa um coração e segue @closetminimal para mais fotos e looks fáceis. #fotodecasal #posesdecasal #ideiasdefotos #lookdecasal #closetminimal','Until I Found You — Ana Luise Fernandes Lima Miranda'),('1500','7698576377791925512','Poses sentada sem ficar travada 📸','De lado ou inclinada: qual pose você testaria? Comenta 📸 Vire um pouco o corpo, solte os ombros e procure um apoio confortável. Incline só de leve se fizer sentido para você. Uma roupa de que você já gosta basta para começar. Curtiu? Deixa um coração e segue @closetminimal para mais fotos e looks fáceis. #fotosozinha #posesparafotos #posesentada #lookfeminino #closetminimal','So Easy (To Fall In Love) — Olivia Dean')]
for index,(slot,tid,title,caption,sound) in enumerate(data):
    folder=r/'posts/2026-10-20'/slot
    assets=[]
    for p in sorted(folder.glob('*.png')):
        assets.append({'path':str(p),'dimensions':list(Image.open(p).size),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
    assert len(assets)==3 and len({tuple(a['dimensions']) for a in assets})==1
    entry={'id':plan['slots'][index]['id'],'slot':plan['slots'][index]['time'],'status':'agendado','tiktok_id':tid,'remote_id':tid,'public_url':f'https://www.tiktok.com/@closetminimal/photo/{tid}','local_dir':f'posts/2026-10-20/{slot}','media_count':3,'asset_sha256':[a['sha256'] for a in assets],'verified_date':'2026-10-19','provider_status_verified':f'TikTok Studio:20 de out,{slot[:2]}:00;ícone relógio;Todos desativado','destination_verified':'menu Perfil aponta @closetminimal imediatamente antes de cada upload e agendamento','native_ai_label':True,'on_image_ai_disclaimer':False,'visual_cta':['pergunta de comentário contextual','curtir','seguir @closetminimal'],'reference_url':plan['slots'][index]['reference'],'publication_route':'TikTok Studio browser','qa':{'all_final_files_visually_inspected':True,'central_3_4_crop_reviewed':True,'top_right_bottom_ui_overlap_reviewed':True,'native_feed_preview_reviewed':True,'anatomy_reviewed':True,'uniform_square_dimensions':True}}
    save(f'posts/2026-10-20/{slot}/manifest.json',dict(entry,assets=assets,title=title,caption=caption,sound=sound,hypothesis=plan['slots'][index]['hypothesis'],rights='Imagens originais geradas por IA de adultos fictícios; música selecionada no catálogo nativo TikTok',tool='imagegen integrado',prompt='Fotografia natural de adultos brasileiros fictícios; uma cena por slide; fonte branca sans-serif; área central com margens desfocadas; anatomia realista e mãos separadas; sem aviso de IA na imagem. Casal:lado a lado,olhando juntos,rindo. Sozinha:sentada de lado,inclinada de leve,apoio no café. CTAvisual contextual de comentário,curtir,seguir. Revisão dos finais CTA:zoom-out e reposicionamento do texto inferior.'))
    (folder/'legenda.txt').write_text(title+'\n\n'+caption,encoding='utf-8')
    queue['posts']=[p for p in queue['posts'] if p.get('tiktok_id')!=tid]+[entry]
for p in queue['posts']:
    if p.get('tiktok_id') in ['7698333806880656658','7698334950075960583']:
        views=128 if p['tiktok_id']=='7698333806880656658' else 88
        p.update(status='publicado',verified_date='2026-10-19',provider_status_verified=f'TikTok Studio:19 de out;Todos;{views}views,0curtidas,0comentários',latest_metrics={'views':views,'likes':0,'comments':0,'observed_date':'2026-10-19'})
save('fila.json',queue)
s=read('estado.json');s.update(scheduled_posts=[d[1] for d in data],next_slots=[p['time'] for p in plan['slots']],next_day_posts_already_scheduled=True,next_day_scheduled_date='2026-10-20',last_reconciliation_date='2026-10-19',last_cycle_date='2026-10-19',blockers=[]);s['published_posts']=list(dict.fromkeys(s.get('published_posts',[])+['7698333806880656658','7698334950075960583']));save('estado.json',s)
plan.update(status='agendado_confirmado',tiktok_ids=[d[1] for d in data]);save('plano-2026-10-20.json',plan)
print('20/10 confirmado:10h7698574727127878930 e15h7698576377791925512;6slides uniformes e hashes registrados')
