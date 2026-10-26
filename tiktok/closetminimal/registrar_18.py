from pathlib import Path
import json, shutil, hashlib
from PIL import Image
root=Path(__file__).parent
gen=Path('C:/Users/Guilherme/.codex/generated_images/01a135a9-4cf2-7680-9cba-11052c7ea282')
items=[('agora','casal-selfie','7698028494801898768','12:22','publicado',['1279473e-09ad-416e-8141-cd1843792b10','335b7b9f-a472-416e-b9d0-09cb1c05cbda']),('1400','sozinha-escada','7698029145527192840','14:00','agendado',['44326d34-a123-449e-8434-916863c9fa56','e2610995-42fb-4d8d-aacf-6a46c83933da']),('1800','casal-looks','7698029651645435142','18:00','agendado',['5f1cfb9c-813f-4414-93b8-ca8b99214d44','ed959d9f-fc45-4614-b03f-c65d8ee1a2ab'])]
def read(name): return json.loads((root/name).read_text(encoding='utf-8-sig'))
def save(name,data): (root/name).write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
queue=read('fila.json')
for slot,name,tid,hour,status,uuids in items:
    folder=root/'posts'/'2026-10-18'/slot
    folder.mkdir(parents=True,exist_ok=True)
    assets=[]
    for i,u in enumerate(uuids,1):
        p=folder/f'{i:03}.png'; shutil.copy2(gen/f'exec-{u}.png',p)
        assets.append({'path':str(p),'dimensions':list(Image.open(p).size),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
    entry={'id':name+'-2026-10-18','local_dir':str(folder.relative_to(root)).replace('\\','/'),'slot':f'2026-10-18T{hour}:00-03:00','status':status,'tiktok_id':tid,'remote_id':tid,'public_url':f'https://www.tiktok.com/@closetminimal/photo/{tid}','media_count':2,'asset_sha256':[a['sha256'] for a in assets],'verified_date':'2026-10-18','provider_status_verified':f'TikTok Studio: 18 de out, {hour}; '+('Todos; 1 visualização' if status=='publicado' else 'relógio de agendamento; Todos desativado'),'destination_verified':'@closetminimal via menu Perfil antes de upload e ação final','publication_route':'TikTok Studio browser','layout_revision':'2026-10-18-square-safe','native_ai_label':True}
    save(str(folder.relative_to(root)/'manifest.json'),dict(entry,assets=assets,qa={'each_file_visually_reviewed':True,'central_3_4_crop_and_ui_review':'conteúdo importante dentro do recorte central; rostos, mãos e texto livres de sobreposições na prévia nativa','native_feed_preview_reviewed':True,'original_fictional_ai_images':True,'sound':'Som original; catálogo nativo retornou Nenhum resultado'}))
    queue['posts']=[p for p in queue['posts'] if p['id']!=entry['id']]+[entry]
for p in queue['posts']:
    if p.get('tiktok_id') in ['7697476467810159890','7697477269769522440']:
        p.update(status='publicado',verified_date='2026-10-18',provider_status_verified='TikTok Studio: 17 de out; Todos; visualizações confirmadas')
save('fila.json',queue)
config=read('config.json');config.setdefault('date_overrides',{})['2026-10-18']=['12:22','14:00','18:00'];save('config.json',config)
state=read('estado.json');state.update(last_cycle_date='2026-10-18',last_reconciliation_date='2026-10-18',scheduled_posts=[x[2] for x in items[1:]],next_slots=['2026-10-18T14:00:00-03:00','2026-10-18T18:00:00-03:00'],next_day_posts_already_scheduled=False,last_native_publication_verified=items[0][2]);state['published_posts']=list(dict.fromkeys(state.get('published_posts',[])+['7697476467810159890','7697477269769522440',items[0][2]]));save('estado.json',state)
print('Três posts registrados; dimensões:',[Image.open(root/'posts'/'2026-10-18'/x[0]/'001.png').size for x in items])
