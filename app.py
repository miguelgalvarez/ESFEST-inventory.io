from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os, smtplib, ssl, logging, json
from email.message import EmailMessage
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__, static_folder='.')
CORS(app)

# --- Config via env (never hardcode secrets) ---
SMTP_HOST = os.getenv('SMTP_HOST', 'smtp.gmail.com')
SMTP_PORT = int(os.getenv('SMTP_PORT', '587'))
SMTP_USER = os.getenv('SMTP_USER', '')
SMTP_PASS = os.getenv('SMTP_PASS', '')
MAIL_TO   = os.getenv('MAIL_TO', '')   # comma-separated list
MAIL_FROM = os.getenv('MAIL_FROM', SMTP_USER)

# Materials live in one place (source of truth)
MATERIALS = [
    "Abaisse langue","Boules de coton","Tige pour les oreilles","Verre en plastique","Désinfectant pour les mains","BP cuff","Carnet immunisation",
    "Ruban à mesurer","Thermomètre (parfois au mur)","Neuropen","Marteau réflexe","Diapason","Collants pour enfant","Tip cover pour les oreilles (enfants et adultes)",
    "Boule de coton","Pad 2x2 pour injection","Tampon d’alcool","Ruban adhésif (bandage)","band-aid","Aiguilles","Seringues","Lame à scalpel","Sterile dressing trays",
    "Contenant d’urine","Urine collector pour enfant","Sac plastique","Condoms","Swabs","Collecteur de spécimen","PDI castille soap towelettes / tampon d’alcool","Pad bleu",
    "Pad blanc","Pad turquoise","Serviettes sanitaires","Brosse à prélèvement cervicale","Lubrifiant","Swab pour échantillon","Thin prep PAP test collector","Speculum (S)",
    "Rouleaux","Jaquette jetable","Ear Covers (enfants + adultes)","Q-tips","Flexible finger cast","Tasse en plastique jetables","Strep A specimen collector","Speculum (M)",
    "Swab échantillons (gros Q-tip)","PDI soap towelettes","Prélèvements","Swab pour prélèvement","Contenant à prélèvement","Collecteurs d’urine","Bandages Alliance","Speculum (L)",
    "Bandages Alliance (2x2)","Bandages divers","Alliance alcohol wipes","Jaquettes bleu jetables","Gants (S)","Gants (M)","Gants (L)","Désinfectant","Tip pour oreilles (adultes et enfants)",
    "Kleenex","Bandages Alliance (4x4)","Papier pour échantillon","Gants stériles","Visières plastiques","Spéculum individuel","Taies d’oreiller jetables","Masques","Couches pour bébés",
    "Couvre-souliers jetables","Eau stérile","Lames de scalpels","Baxedin","Fil à chirurgie","Chlorure de sodium","Kit pour enlever des agrafes","Crèmes (polysporin)",
    "Contenant pour prélèvement (biopsie)","Xylocaine","Rasoires","Autre contenants à prélèvement"
]

# --- Logging ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')

@app.get('/')
def root_get():
    return send_from_directory('.', 'index.html')

@app.get('/materials')
def get_materials():
    return jsonify(MATERIALS)

@app.get('/healthz')
def health():
    return jsonify({'status': 'ok'})

@app.get('/favicon.ico')
def favicon():
    # Avoid noisy 404s
    return ('', 204)

@app.post('/')
def notify():
    # Accept JSON or form-encoded
    if request.is_json:
        data = request.get_json(silent=True) or {}
    else:
        data = request.form.to_dict()

    room = (data.get('room') or '').strip()
    material = (data.get('material') or '').strip()
    if not room or not material:
        return jsonify({'ok': False, 'error': 'room and material are required'}), 400

    try:
        send_email(room, material)
        logging.info(f"Sent notification: room={room}, material={material}")
        return jsonify({'ok': True})
    except Exception as e:
        logging.exception("Email send failed")
        return jsonify({'ok': False, 'error': str(e)}), 500

def send_email(room: str, material: str):
    if not (SMTP_USER and (SMTP_PASS or SMTP_PORT == 25) and MAIL_TO):
        raise RuntimeError('Variables SMTP non définies (SMTP_USER/SMTP_PASS/MAIL_TO)')

    recipients = [x.strip() for x in MAIL_TO.split(',') if x.strip()]
    msg = EmailMessage()
    msg['Subject'] = f"Stock faible : {material} ({room})"
    msg['From'] = MAIL_FROM
    msg['To'] = ', '.join(recipients)
    msg.set_content(f"L'article suivant est en rupture imminente dans {room} :\n\n  • {material}\n\nMerci de procéder au réapprovisionnement dès que possible.\n")

    context = ssl.create_default_context()
    with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=15) as server:
        if SMTP_PORT != 25:
            server.starttls(context=context)
        if SMTP_USER:
            server.login(SMTP_USER, SMTP_PASS)
        server.send_message(msg)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)