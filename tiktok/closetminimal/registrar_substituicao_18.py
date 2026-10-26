from pathlib import Path
import json,shutil,hashlib
from PIL import Image
r=Path(__file__).parent
def read(p):return json.loads((r/p).read_text(encoding='utf-8-sig'))
def save(p,d):(r/p).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
folder=r/'posts/2026-10-18/1800-teste-cta';folder.mkdir(parents=True,exist_ok=True)
src=r/'testes/2026-10-18-novos/casal'
assets=[]
for i,name in enumerate(['01.png','02.png','03-cta.png'],1):
    p=folder/f'{i:03}.png';shutil.copy2(src/name,p)
    assets.append({'path':str(p),'dimensions':list(Image.open(p).size),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
entry={'id':'casal-teste-cta-2026-10-18','slot':'2026-10-18T18:00:00-03:00','status':'agendado','tiktok_id':'7698083157718879506','remote_id':'7698083157718879506','local_dir':'posts/2026-10-18/1800-teste-cta','public_url':'https://www.tiktok.com/@closetminimal/photo/7698083157718879506','media_count':3,'asset_sha256':[a['sha256'] for a in assets],'verified_date':'2026-10-18','provider_status_verified':'TikTok Studio: 18 de out, 18:00; relógio de agendamento; Todos desativado; antigo ausente após exclusão','destination_verified':'menu Perfil @closetminimal imediatamente antes de upload e agendamento','native_ai_label':True,'on_image_ai_disclaimer':False,'visual_cta':['Comenta 1, 2 ou 3','Curtiu? Deixa um coração.','Segue @closetminimal para mais ideias'],'replaces_tiktok_id':'7698029651645435142','publication_route':'TikTok Studio browser'}
save(str((folder/'manifest.json').relative_to(r)),dict(entry,assets=assets,native_feed_preview_reviewed=True,all_files_inspected=True))
q=read('fila.json')
for p in q['posts']:
    if p.get('tiktok_id')=='7698029651645435142':p.update(status='substituido_excluido_recuperavel',replaced_by='7698083157718879506',provider_status_verified='Excluído via Studio; recuperável30dias; não restaurar')
q['posts']=[p for p in q['posts'] if p.get('tiktok_id')!=entry['tiktok_id']]+[entry];save('fila.json',q)
s=read('estado.json');s['scheduled_posts']=[entry['tiktok_id']];s['last_schedule_replacement']={'date':'2026-10-18','old':'7698029651645435142','new':entry['tiktok_id'],'slot':entry['slot']};save('estado.json',s)
c=read('config.json');c['visual_cta_required']={'comments':'pergunta contextual clara dentro da imagem','follow':'benefício e @closetminimal visíveis no slide','like':'chamada curta visível','safe_margins_required':True};save('config.json',c)
m=read('testes/2026-10-18-novos/casal/manifest.json');m.update(status='versao_cta_agendada',publication_authorized_now=True,tiktok_id=entry['tiktok_id'],scheduled_at=entry['slot'],final_manifest=str(folder/'manifest.json'));save('testes/2026-10-18-novos/casal/manifest.json',m)
print('Substituição registrada: 7698083157718879506 às18h; antigo removido')
