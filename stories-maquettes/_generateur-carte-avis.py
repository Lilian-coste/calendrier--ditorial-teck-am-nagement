"""Générateur des cartes « avis client » des stories Teck Aménagement.

⭐ POINT D'ENTRÉE de toute carte avis écrite. Il remplace _source-S2-avis-muriel.py,
   écrit pour la seule carte de Muriel (16/07/2026) et dont les trois chemins sont morts.
   Le design est le même, au pixel près : carte bento façon Apple, fond #F5F5F7, carte
   blanche arrondie, bordure bleue Teck et ombre portée en permanence (l'état « survol »
   du design de référence, figé puisqu'une image n'a pas de survol), 5 étoiles bleues,
   titre, citation en italique, avatar à initiales et nom, en-tête « Nos clients /
   Parlent de nous ».

Écrit le 19/10/2026 pour la série d'octobre à décembre (commande /stories-teck).

Règles qui ne se discutent pas :
- On ne réécrit JAMAIS un avis. Couper avec […] est permis, reformuler non. Le titre de
  la carte est une phrase de l'avis, mot pour mot.
- La photo est celle du chantier de ce client. Si on ne l'a pas, la carte sort sans photo
  (photo=None) plutôt qu'avec la photo d'un autre chantier.
- Aucune ville qui ne soit pas dans l'avis.

Usage (sans argument, rien n'est généré) :
    python3 _generateur-carte-avis.py S-AVIS-GRUTER.jpg S-AVIS-MATHIEU.jpg
Chaque carte sort ici et dans ~/Downloads/Envoyer à Franck.
"""
import base64
import html
import os
import subprocess
import sys
import tempfile

OUT = os.path.dirname(os.path.abspath(__file__))
ENVOI = os.path.expanduser("~/Downloads/Envoyer à Franck")
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
G = os.path.expanduser("~/Franck/Galerie Teck Aménagement/Photos réalisation 7 12 2025")

STYLE = """
  *{box-sizing:border-box;margin:0;padding:0}
  html,body{width:1080px;height:1920px;background:#F5F5F7;
    font-family:"Helvetica Neue",Inter,-apple-system,sans-serif;
    -webkit-font-smoothing:antialiased}
  .wrap{padding:64px 56px;height:100%;display:flex;flex-direction:column;justify-content:center}
  .head{text-align:center;margin-bottom:52px}
  .kicker{color:#0653A8;font-weight:500;letter-spacing:0.05em;text-transform:uppercase;
    font-size:34px;display:block;margin-bottom:6px}
  .head h2{color:#1D1D1F;font-size:76px;font-weight:300;letter-spacing:-0.02em;line-height:1.05}
  .card{background:#FFFFFF;border:2px solid #0653A8;border-radius:56px;overflow:hidden;
    box-shadow:0 20px 40px rgba(0,0,0,0.08);display:flex;flex-direction:column;
    text-align:center;flex:none}
  .img{width:100%;height:830px;overflow:hidden;flex:none}
  .img img{width:100%;height:100%;object-fit:cover}
  .body{padding:54px 52px 46px;display:flex;flex-direction:column}
  .stars{color:#0653A8;font-size:30px;letter-spacing:0.32em;margin-bottom:30px;padding-left:0.32em}
  h3{color:#1D1D1F;font-size:44px;font-weight:500;line-height:1.24;margin-bottom:26px}
  .quote{color:#424245;font-size:33px;font-weight:300;line-height:1.5;font-style:italic}
  .intro{font-style:normal;font-weight:500;color:#1D1D1F}
  .who{display:flex;align-items:center;justify-content:center;gap:18px;padding-top:42px}
  .av{width:74px;height:74px;border-radius:50%;background:#F5F5F7;border:1px solid #D2D2D7;
    display:flex;align-items:center;justify-content:center;color:#0653A8;
    font-size:24px;font-weight:700;flex:none}
  .who .n{text-align:left;color:#1D1D1F;font-size:31px;font-weight:500}
  /* Sans photo : la carte garde sa forme, le texte prend la place libérée. */
  .sans .body{padding:130px 76px 110px}
  .sans .stars{font-size:42px;margin-bottom:56px}
  .sans h3{font-size:64px;line-height:1.2;margin-bottom:44px}
  .sans .quote{font-size:46px}
  .sans .who{padding-top:76px}
  .sans .av{width:92px;height:92px;font-size:30px}
  .sans .who .n{font-size:38px}
"""


def carte(nom, initiales, titre, suite, fichier, photo=None, cadrage="center 58%", intro=None):
    """intro : quelques mots de NOUS, posés avant les guillemets et donc hors de l'avis
       (ex. « Après pose : », demandé par Lilian le 19/10/2026)."""
    if photo:
        ext = os.path.splitext(photo)[1].lower().lstrip(".")
        mime = "png" if ext == "png" else "jpeg"
        b64 = base64.b64encode(open(photo, "rb").read()).decode()
        bloc_img = (f'<div class="img"><img src="data:image/{mime};base64,{b64}" '
                    f'style="object-position:{cadrage}" alt=""></div>')
    else:
        bloc_img = ""
    e = html.escape
    page = f"""<!doctype html><html><head><meta charset="utf-8"><style>{STYLE}</style></head>
<body><div class="wrap{'' if photo else ' sans'}">
  <div class="head"><span class="kicker">Nos clients</span><h2>Parlent de nous</h2></div>
  <div class="card">{bloc_img}
    <div class="body">
      <div class="stars">★★★★★</div>
      <h3>«&nbsp;{e(titre)}&nbsp;»</h3>
      <p class="quote">{('<span class="intro">' + e(intro) + '</span> ') if intro else ''}«&nbsp;{e(suite)}&nbsp;»</p>
      <div class="who"><div class="av">{e(initiales)}</div><div class="n">{e(nom)}</div></div>
    </div>
  </div>
</div></body></html>"""
    with tempfile.TemporaryDirectory() as tmp:
        src = os.path.join(tmp, "carte.html")
        open(src, "w", encoding="utf-8").write(page)
        sortie = os.path.join(OUT, fichier)
        subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars",
                        "--force-device-scale-factor=1", "--window-size=1080,1920",
                        f"--screenshot={sortie}", f"file://{src}"], capture_output=True)
    if not os.path.exists(sortie):
        print("✗", fichier, ": Chrome n'a rien produit")
        return
    if os.path.isdir(ENVOI):
        subprocess.run(["cp", sortie, os.path.join(ENVOI, fichier)])
        print("✓", fichier, "(+ Envoyer à Franck)")
    else:
        print("✓", fichier, "(dossier d'envoi introuvable :", ENVOI, ")")


# (nom affiché, initiales, titre, suite, fichier de sortie, photo du chantier ou None, cadrage)
# Textes recopiés de QG/1-projets/teck-amenagement/sources-brutes/_inventaire/texte/
# avis-google-bruts.txt. Seules corrections : des espaces (tableau montré à Lilian le 19/10).
AVIS = [
    # 22/10/2026. Pas de photo de son chantier : exception validée par Lilian le 19/10.
    ("Mike Blay", "MB",
     "Nous avions une interrogation sur l'ombrage effectif d'une structure ajourée :",
     "l'ombre est efficace et la lumière tamisée très agréable sous la pergola.",
     "S-AVIS-MIKE-BLAY.jpg", None, "center 58%", "Après pose :"),
    # 29/10/2026. Version du soir, choisie par Lilian le 19/10/2026. ⚠️ Le lien entre cet avis et
    # le dossier « Goguet Vinet » de ~/Franck vient du nom du dossier et du salon enterré que
    # l'avis décrit : Franck ne l'a jamais confirmé.
    ("Jean-Luc Vinet", "JV",
     "Nous en avions rêvé, Teck Aménagement l'a fait...!",
     "Pour nous un gros projet, terrasse, salon enterré, pergola, ...et donc un tas de "
     "craintes ... Dès la première visite Franck Joncheray assure, et nous rassure ! […] "
     "Une équipe qui dit ce qu'elle fait, et fait ce qu'elle dit...",
     "S-AVIS-VINET.jpg",
     os.path.join(G, "Goguet Vinet/Selection photos nuit Franck/stcanna_teck2 (236).jpg"),
     "center 60%"),
    # 26/11/2026. Photo de son chantier.
    ("Hélène Gruter", "HG",
     "Vous pouvez foncer les yeux fermés !",
     "Franck et son équipe sont exceptionnels : écoute, conseils, réactivité, travail "
     "impeccable... Un immense merci à eux de nous avoir si bien accompagnés dans notre "
     "projet d'aménagement extérieur autour de notre piscine.",
     # Photo choisie par Lilian le 19/10/2026.
     "S-AVIS-GRUTER.jpg",
     os.path.expanduser("~/Franck/New projet/Gruter Selection Franck/2stmarc_gvt (59).jpg"),
     "center 55%"),
    # 10/12/2026. Photo de son chantier (la 2 bongiov_48 a servi dans la pub de mai 2026).
    ("Fabienne Bongiovanni", "FB",
     "Une merveille, très belle prestation, chantier terminé dans les temps",
     "Nous avons fait appel à la société Teck aménagement pour la rénovation de nos "
     "extérieurs, aménagement d'une terrasse en bois exotique et création d'une pergola sur "
     "toute la longueur de la maison.",
     "S-AVIS-BONGIOVANNI.jpg",
     os.path.join(G, "Bongiovanni/Sélection franck/1 bongiov_gvoinot_44.JPG"), "center 50%"),
    # 24/12/2026. Pas de photo de son chantier.
    ("Mathieu", "M",
     "La luminosité reste la même à l'intérieur de la maison tout en protégeant ma terrasse "
     "du soleil.",
     "Les délais ont été respectés et l'installation a été réalisée rapidement, avec un vrai "
     "souci du détail.",
     "S-AVIS-MATHIEU.jpg", None),
    # 31/12/2026. Photo de son chantier.
    ("David Guillermo", "DG",
     "Très professionnel, disponible, à l'écoute et très efficace",
     "nous recommandons vivement Teck Aménagement et Franck pour la création et "
     "l'installation d'une pergola… qui par son esthétisme et sa personnalisation deviendra "
     "un atout majeur de votre maison!",
     "S-AVIS-GUILLERMO.jpg", os.path.join(G, "Guillermo/Section Franck/aig_viv_gvt (96).jpg"),
     "center 50%"),
]

if __name__ == "__main__":
    voulus = set(sys.argv[1:])
    if not voulus:
        print("Rien à faire. Cartes connues :")
        for a in AVIS:
            print("   ", a[4])
    for a in AVIS:
        if a[4] in voulus:
            carte(*a)
