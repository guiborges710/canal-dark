// Tokens do motor: cores, formato e fonte. Tudo é função do número do frame (determinístico).
// Os nomes em português são os usados no cenas.json; os valores são o estilo do canal.
const COR = {
  azul: '#2563EB',
  'azul-claro': '#38BDF8',
  amarelo: '#FACC15',
  laranja: '#FB923C',
  branco: '#FFFFFF',
  grafite: '#1F2937',
};
const FUNDO = '#F8FAFC';
const LISTRA = '#E0F2FE';

const FPS = 30;
const W = 1080;
const H = 1920;
const FONT = "'Arial Black', 'Segoe UI Black', Arial, sans-serif";

// Cor pelo nome do cenas.json; nome desconhecido vira erro explícito (não cai em cor aleatória).
function cor(nome) {
  if (!(nome in COR)) throw new Error(`cor desconhecida no cenas.json: "${nome}" (use ${Object.keys(COR).join(', ')})`);
  return COR[nome];
}
