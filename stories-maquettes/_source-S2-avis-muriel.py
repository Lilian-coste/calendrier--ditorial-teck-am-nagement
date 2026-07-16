"""Story avis client — Muriel Baccigalupo, jeudi 16 juillet.

Reprend le design bento/Apple fourni par Lilian : carte blanche arrondie sur
fond #F5F5F7, image en haut, 5 étoiles bleues, titre, citation en italique,
avatar à initiales + nom.

Deux écarts assumés par rapport au code de référence :
- Helvetica Neue au lieu d'Inter : c'est la police de la charte Teck validée le
  13/07, et les deux sont quasi identiques à l'œil.
- pas de ville sous le nom : elle n'est pas dans l'avis Google, donc on ne
  l'invente pas.
"""
import base64
import subprocess

S = "/private/tmp/claude-501/-Users-lilia-Claude-for-VS-Code/ec823ae8-6e57-4c15-9d07-6f559b3cbea3/scratchpad/muriel"
PHOTO = "/Users/lilia/Downloads/TECK AMENAGEMENT - Google Maps_files/unnamed_003_6pcK.jpg"
OUT = "/Users/lilia/mes-clients/teck-amenagement/livrables/instagram/stories-maquettes/S2-avis-muriel.jpg"

b64 = base64.b64encode(open(PHOTO, "rb").read()).decode()

# Texte de l'avis, découpé en accroche + suite. Aucun mot n'est réécrit.
TITRE = "Une superbe pergola, très design… à la hauteur de nos espérances."
SUITE = ("Une vraie plus value pour la maison. Une entreprise sérieuse et réactive "
         "qui a respecté tous ses engagements.")

HTML = f"""<!doctype html><html><head><meta charset="utf-8"><style>
  *{{box-sizing:border-box;margin:0;padding:0}}
  html,body{{width:1080px;height:1920px;background:#F5F5F7;
    font-family:"Helvetica Neue",Inter,-apple-system,sans-serif;
    -webkit-font-smoothing:antialiased}}
  .wrap{{padding:64px 56px;height:100%;display:flex;flex-direction:column;justify-content:center}}

  .head{{text-align:center;margin-bottom:52px}}
  .kicker{{color:#0653A8;font-weight:500;letter-spacing:0.05em;text-transform:uppercase;
    font-size:34px;display:block;margin-bottom:6px}}
  .head h2{{color:#1D1D1F;font-size:76px;font-weight:300;letter-spacing:-0.02em;line-height:1.05}}

  /* Une image fixe n'a pas de survol : on fige l'état :hover du design de
     référence (bordure bleue + ombre renforcée), c'est ce que Lilian veut voir. */
  .card{{background:#FFFFFF;border:2px solid #0653A8;border-radius:56px;overflow:hidden;
    box-shadow:0 20px 40px rgba(0,0,0,0.08);display:flex;flex-direction:column;
    text-align:center;flex:none}}
  .img{{width:100%;height:830px;overflow:hidden;flex:none}}
  .img img{{width:100%;height:100%;object-fit:cover;object-position:center 58%}}

  .body{{padding:54px 52px 46px;display:flex;flex-direction:column}}
  .stars{{color:#0653A8;font-size:30px;letter-spacing:0.32em;margin-bottom:30px;padding-left:0.32em}}
  h3{{color:#1D1D1F;font-size:44px;font-weight:500;line-height:1.24;margin-bottom:26px}}
  .quote{{color:#424245;font-size:33px;font-weight:300;line-height:1.5;font-style:italic}}

  .who{{display:flex;align-items:center;justify-content:center;gap:18px;padding-top:42px}}
  .av{{width:74px;height:74px;border-radius:50%;background:#F5F5F7;border:1px solid #D2D2D7;
    display:flex;align-items:center;justify-content:center;color:#0653A8;
    font-size:24px;font-weight:700;flex:none}}
  .who .n{{text-align:left;color:#1D1D1F;font-size:31px;font-weight:500}}
</style></head><body>
  <div class="wrap">
    <div class="head">
      <span class="kicker">Nos clients</span>
      <h2>Parlent de nous</h2>
    </div>
    <div class="card">
      <div class="img"><img src="data:image/jpeg;base64,{b64}" alt=""></div>
      <div class="body">
        <div class="stars">★★★★★</div>
        <h3>« {TITRE} »</h3>
        <p class="quote">« {SUITE} »</p>
        <div class="who">
          <div class="av">MB</div>
          <div class="n">Muriel Baccigalupo</div>
        </div>
      </div>
    </div>
  </div>
</body></html>"""

open(f"{S}/story.html", "w", encoding="utf-8").write(HTML)
subprocess.run(["/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
                "--headless=new", "--disable-gpu", "--force-device-scale-factor=1",
                "--window-size=1080,1920", f"--screenshot={OUT}",
                f"file://{S}/story.html"], capture_output=True)
print("✓", OUT)
