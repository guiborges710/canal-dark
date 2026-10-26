from pathlib import Path
import json,shutil,hashlib
from PIL import Image
r=Path(__file__).parent
g=Path('C:/Users/Guilherme/.codex/generated_images/01a135a9-4cf2-7680-9cba-11052c7ea282')
def read(p):return json.loads((r/p).read_text(encoding='utf-8-sig'))
def save(p,d):(r/p).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
q=read('fila.json')
for slot,name,tid,ids,ref in [('1000','casal-janela','7698333806880656658',['52e888e6-edbb-4857-bfd8-c32f5438d173','752f5c11-e887-4336-a6c3-6421b63abbfa'],'https://www.tiktok.com/@closetminimal/photo/7583928005593025813'),('1500','sozinha-look-inteiro','7698334950075960583',['fad6ecea-5d4e-4e4a-ad11-01dd7842fd35','c72d1605-04c4-423b-bf7d-c964e35d14c8'],'https://www.tiktok.com/@closetminimal/photo/7583616310253276436')]:
    folder=r/'posts/2026-10-19'/slot;folder.mkdir(parents=True,exist_ok=True)
    assets=[]
    for i,id in enumerate(ids,1):
        p=folder/f'{i:03}.png';shutil.copy2(g/f'exec-{id}.png',p);assets.append({'path':str(p),'dimensions':list(Image.open(p).size),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
    e={'id':name+'-2026-10-19','slot':f'2026-10-19T{slot[:2]}:00:00-03:00','status':'agendado','tiktok_id':tid,'remote_id':tid,'public_url':f'https://www.tiktok.com/@closetminimal/photo/{tid}','local_dir':str(folder.relative_to(r)).replace('\\','/'),'media_count':2,'asset_sha256':[a['sha256'] for a in assets],'verified_date':'2026-10-19','provider_status_verified':f'TikTok Studio:19 de out,{slot[:2]}:00;relógio de agendamento;Todos desativado','destination_verified':'Perfil do menu da sessão @closetminimal antes de upload e ação final','native_ai_label':True,'on_image_ai_disclaimer':False,'visual_cta':['comentário contextual','curtir','seguir @closetminimal'],'reference_url':ref,'qa':{'all_files_inspected':True,'central_3_4_crop_reviewed':True,'native_feed_preview_reviewed':True,'anatomy_reviewed':True,'uniform_square_dimensions':True},'publication_route':'TikTok Studio browser'}
    save(str((folder/'manifest.json').relative_to(r)),dict(e,assets=assets,rights='Imagens originais de adultos fictícios geradas por IA',prompt='Foto única natural, fonte branca sans-serif, área central com margens desfocadas generosas, anatomia realista e CTAs visuais. Revisão:zoom-out conjunto de foto e texto.'))
    q['posts']=[p for p in q['posts'] if p.get('tiktok_id')!=tid]+[e]
for p in q['posts']:
    if p.get('tiktok_id')=='7698083157718879506':p.update(status='publicado',verified_date='2026-10-19',provider_status_verified='TikTok Studio:18/10 18h;Todos;106views,0curtidas,0comentários',latest_metrics={'views':106,'likes':0,'comments':0,'observed_date':'2026-10-19'})
save('fila.json',q)
s=read('estado.json');s.update(last_cycle_date='2026-10-19',last_reconciliation_date='2026-10-19',scheduled_posts=['7698333806880656658','7698334950075960583'],next_slots=['2026-10-19T10:00:00-03:00','2026-10-19T15:00:00-03:00'],last_native_publication_verified='7698083157718879506');s['published_posts']=list(dict.fromkeys(s.get('published_posts',[])+['7698083157718879506']));save('estado.json',s)
a=read('analytics.json');a.setdefault('observations',[]).append({'date':'2026-10-19','post_id':'7698083157718879506','views':106,'likes':0,'comments':0,'note':'menos de24h; sem inferência sobre eficácia de CTA'});save('analytics.json',a)
save('execucao-2026-10-19.json',{'result':'dois_agendamentos_confirmados','slots':s['next_slots'],'runtime_note':'A primeira tentativa10h sofreu rejeição automática por leitura equivocada de UTC como horário local. Clock confirmou11:07UTC=08:07Brasília; retry aprovado no mesmo fluxo. Nenhuma ação bloqueada pendente.','unapproved_solo_test':'preservado local; não utilizado','notify':False})
print('19/10:dois agendados; post18h anterior publicado confirmado')
