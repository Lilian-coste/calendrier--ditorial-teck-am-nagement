"""Générateur des maquettes de stories « valeur / info » — Teck Aménagement.

⭐ POINT D'ENTRÉE de toute nouvelle story standard (les cartes témoignage ont
   leur propre script : _source-S2-avis-muriel.py).

Encode la DA validée par Lilian, pour des stories identiques d'une fois sur
l'autre : titre Helvetica Neue Light EN MAJUSCULES + interlettrage ; texte
Regular en écriture normale ; scrim sombre en haut pour la lisibilité ;
surlignage possible d'un mot du titre en bleu Teck #0653A8 ; sortie 1080×1920.
Un « \\n » dans le texte force un retour à la ligne. Aucune légende : le texte
vit dans l'image. Réf : ../../DA-teck-amenagement.md et ../scripts-stories.md.

17/08/2026 — DESCENTE. Le texte partait trop haut : sur un téléphone, la barre
de progression et la ligne de compte d'Instagram mordaient sur le titre. Tout
le bloc descend donc de 130 px, et le scrim s'étire d'autant, sinon les
dernières lignes se retrouveraient sur la photo en clair. Les stories #11 à #14
ont été régénérées à cette hauteur ; toute nouvelle story la reprend.
"""
import os
from PIL import Image, ImageDraw, ImageFont, ImageOps

OUT = os.path.dirname(os.path.abspath(__file__))
FRANCK = os.path.expanduser("~/Franck")
HN = "/System/Library/Fonts/HelveticaNeue.ttc"
LIGHT, REG, MEDIUM = 7, 0, 10
BLEU, CLAIR = (6, 83, 168), (150, 196, 240)
BLANC, INFO = (255, 255, 255), (238, 244, 252)
DESCENTE = 130
# Chaque story produite est aussi déposée ici, prête à envoyer à Franck.
# Demandé par Lilian le 21/09/2026. Si le dossier n'existe pas, on ne dépose rien
# et on le dit, plutôt que de le recréer en douce ailleurs.
ENVOI = os.path.expanduser("~/Downloads/Envoyer à Franck")


def enregistrer(im, fname):
    im.save(os.path.join(OUT, fname), quality=92)
    if os.path.isdir(ENVOI):
        im.save(os.path.join(ENVOI, fname), quality=92)
        print("\u2713", fname, "(+ Envoyer \u00e0 Franck)")
    else:
        print("\u2713", fname, "(dossier d'envoi introuvable :", ENVOI, ")")


def F(size, index=REG):
    return ImageFont.truetype(HN, size, index=index)


def load(path, cadrage=0.5):
    """Recadre plein cadre en 9:16 → 1080×1920. On se fie à l'EXIF (pas de
       rotation manuelle, sinon les paysages se couchent).
       cadrage : position horizontale de la découpe dans une photo paysage, de 0
       (bord gauche) à 1 (bord droit). 0.5 = centre, la valeur par défaut."""
    im = ImageOps.exif_transpose(Image.open(path)).convert("RGB")
    w, h = im.size
    t = 9 / 16
    if w / h > t:
        nw = int(h * t)
        x = int((w - nw) * cadrage)
        im = im.crop((x, 0, x + nw, h))
    else:
        nh = int(w / t)
        im = im.crop((0, (h - nh) // 2, w, (h - nh) // 2 + nh))
    return im.resize((1080, 1920), Image.LANCZOS)


def track(d, x, y, txt, font, fill, sp=3):
    """Interlettrage manuel (Pillow n'expose pas le letter-spacing)."""
    for ch in txt:
        d.text((x, y), ch, font=font, fill=fill)
        x += d.textlength(ch, font=font) + sp
    return x


def story(image_path, titre, info, fname, highlight=None, descente=DESCENTE,
          sombre=0, cadrage=0.5, lt=84, li=48, g1=30, g2=44):
    """sombre : voile noir uniforme posé AVANT le scrim, de 0 à 255. Sert quand la
       photo est trop lumineuse pour que le texte tienne dessus, typiquement un
       plein ciel. 70 assombrit sans éteindre les couleurs.
       cadrage : voir load().
       lt, li : interligne du titre et du texte ; g1, g2 : écarts avant et après le filet."""
    im = load(image_path, cadrage)
    if sombre:
        im = Image.alpha_composite(
            im.convert("RGBA"), Image.new("RGBA", (1080, 1920), (0, 0, 0, sombre))
        ).convert("RGB")
    haut = 900 + descente                 # le scrim descend avec le texte
    ov = Image.new("RGBA", (1080, 1920), (0, 0, 0, 0))
    od = ImageDraw.Draw(ov)
    for y in range(0, haut):
        od.line([(0, y), (1080, y)], fill=(8, 20, 45, int(230 * (1 - y / haut) ** 1.05)))
    for y in range(1680, 1920):
        od.line([(0, y), (1080, y)], fill=(8, 20, 45, int(85 * ((y - 1680) / 240) ** 1.6)))
    im = Image.alpha_composite(im.convert("RGBA"), ov).convert("RGB")
    d = ImageDraw.Draw(im)
    ft, fi = F(66, LIGHT), F(34, REG)

    def wrap(txt, f, mw, sp=0):
        out = []
        for para in txt.split("\n"):          # retours voulus respectés
            c = ""
            for w_ in para.split():
                s = (c + " " + w_).strip()
                if d.textlength(s, font=f) + sp * len(s) <= mw:
                    c = s
                else:
                    out.append(c); c = w_
            out.append(c)
        return out

    y = 175 + descente
    for line in wrap(titre.upper(), ft, 900, 3):
        if highlight and highlight.upper() in line:
            pre = line.split(highlight.upper())[0]
            x0 = 90 + sum(d.textlength(c, font=ft) + 3 for c in pre)
            wd = sum(d.textlength(c, font=ft) + 3 for c in highlight.upper())
            d.rounded_rectangle([x0 - 14, y - 4, x0 + wd + 6, y + 74], 8, fill=BLEU)
        track(d, 90, y, line, ft, (255, 255, 255), 3)
        y += lt
    y += g1
    d.line([(90, y), (200, y)], fill=CLAIR, width=3)
    y += g2
    for line in wrap(info, fi, 880):
        d.text((90, y), line, font=fi, fill=(238, 244, 252))
        y += li
    enregistrer(im, fname)


def liste(image_path, titre, sous_titre, items, fname, descente=DESCENTE):
    """Variante « liste » (4 équipements) : voile bleu uni sur toute la hauteur
       au lieu du scrim, titre + sous-titre, filet pleine largeur, puis une
       entrée par équipement avec sa pastille. Intitulés en Medium 38
       interlettré à 2, descriptions en Regular 31."""
    im = load(image_path)
    im = Image.alpha_composite(
        im.convert("RGBA"), Image.new("RGBA", (1080, 1920), (10, 30, 67, 150))
    ).convert("RGB")
    d = ImageDraw.Draw(im)
    ft, fs, fit, fid = F(66, LIGHT), F(34, REG), F(38, MEDIUM), F(31, REG)

    def wrap(txt, f, mw, sp=0):
        out = []
        for para in txt.split("\n"):
            c = ""
            for w_ in para.split():
                s = (c + " " + w_).strip()
                if d.textlength(s, font=f) + sp * len(s) <= mw:
                    c = s
                else:
                    out.append(c); c = w_
            out.append(c)
        return out

    y = 170 + descente
    for line in wrap(titre.upper(), ft, 900, 3):
        track(d, 90, y, line, ft, BLANC, 3)
        y += 84
    track(d, 90, y + 21, sous_titre.upper(), fs, CLAIR, 3)
    d.rectangle([90, 432 + descente, 990, 433 + descente], fill=BLANC)

    # (y de l'intitulé, y de la 1re ligne de description, y du filet séparateur)
    for (yt, yd, ysep), (nom, desc) in zip(
            [(509, 562, 665), (695, 748, 811), (841, 896, 957), (987, 1040, None)],
            items):
        yt, yd = yt + descente, yd + descente
        d.ellipse([89, yt + 23 - 29, 147, yt + 23 + 29], outline=CLAIR, width=3)
        track(d, 180, yt, nom.upper(), fit, BLANC, 2)
        for i, line in enumerate(wrap(desc, fid, 780)):
            d.text((180, yd + i * 42), line, font=fid, fill=INFO)
        if ysep:
            d.rectangle([180, ysep + descente, 990, ysep + descente], fill=BLANC)
    enregistrer(im, fname)


# (chemin image sous ~/Franck, TITRE, texte, sortie, [mot à surligner]).
# ⛔ Vérifier chaque photo : AUCUN voile de coco (cf. DA).
D = os.path.join(FRANCK, "New projet/Dansou BD")
V = os.path.join(FRANCK, "Lilian Vila impian copie")
G = os.path.join(FRANCK, "Galerie Teck Aménagement/Photos réalisation 7 12 2025")
STORIES = [
    (os.path.join(V, "_LVM1721.jpg"), "Le détail qu'on ne voit qu'au soleil",
     "La finition de nos structures est un sable texturé.\nAu soleil, de fines "
     "paillettes d'aluminium l'illuminent et lui donnent toute sa profondeur.",
     "S3-detail-au-soleil.jpg"),
    # Stories #11, #12 et #14, régénérées le 17/08/2026 pour la descente.
    (os.path.join(G, "Goguet Vinet/Selection Gabrielle/stcannat_gvt (41).jpg"),
     "Teck Aménagement, ce n'est pas que la pergola",
     "Ici, nous avons aussi construit la terrasse. Un extérieur se pense dans "
     "son ensemble : la plage de piscine, les espaces cosy et partout le charme du bois.",
     "S5-amenagement-densemble.jpg"),
    (os.path.join(G, "Bongiovanni/Sélection franck/1 bongiov_gvoinot_31.JPG"),
     "Elle ne s'ajoute pas à la maison, elle la prolonge",
     "Chaque pergola est dessinée pour une façade, une orientation, un jardin. "
     "C'est ce qui fait qu'elle semble avoir toujours été là.",
     "S7-prolonge-la-maison.jpg"),
    (os.path.join(G, "RIERA/Selection Franck/riera_teck_gvt_31.jpg"),
     "Nos pergolas n'ont pas de limite de longueur",
     "La structure se dessine à la dimension de votre projet, aussi longue "
     "qu'il le faut. Ici, elle protège toute une cuisine d'été du soleil et de "
     "la chaleur des Bouches-du-Rhône.",
     "S-SANS-LIMITE.jpg"),
]

# 21/09/2026 — Série de huit stories, retouchée trois fois sur les retours de
# Lilian. Photos : Mickaël pour Ansart et pour la villa impian, Gabrielle
# Voinot pour Gruter et Ramirez.
A = os.path.join(FRANCK, "projet Ansart/Selection Franck Ansart Eliot")
STORIES += [
    (os.path.join(A, "_ECD7994.jpg"), "L'air ne reste pas bloqué dessous",
     "Nos pergolas s'inspirent des pergolas méditerranéennes, où la "
     "circulation d'air fait partie de la conception.\nL'air circule entre les "
     "carrelets au lieu de rester bloqué sous un toit plein.",
     "S-AIR-CIRCULE.jpg"),
    (os.path.join(A, "_ECD7870.jpg"), "L'ombre ne s'arrête pas à la table",
     "La structure se dessine à la longueur de votre terrasse, et ici elle "
     "court sur toute la façade.\nVous n'avez pas un coin à l'ombre et le reste "
     "au soleil, vous avez toute la terrasse.",
     "S-OMBRE-SE-DEPLACE.jpg"),
    (os.path.join(A, "_ECD8029.jpg"), "Ce que la pergola seule n'arrête pas",
     "En fin d'après-midi, le soleil passe sous la couverture et vient vous "
     "chercher de côté.\nC'est là que le claustra sert : il filtre ce soleil "
     "rasant et le vis-à-vis, sans jamais enfermer l'espace.",
     "S-SOLEIL-RASANT.jpg"),
    (os.path.join(A, "_ECD7873.jpg"), "Le vis-à-vis, sans vous enfermer",
     "Le claustra bois se pose en lames verticales ou horizontales, et nous "
     "dessinons leur espacement selon ce que vous voulez cacher.\nIl vous met à "
     "l'abri des regards sans fermer l'espace, donc vous gardez la lumière et "
     "la vue sur votre jardin.",
     "S-BOIS-DUR.jpg"),
    # Photo choisie par Lilian le 21/09 : les montants fins devant la piscine.
    (os.path.join(FRANCK, "New projet/Gruter Selection Franck/stmarc_gvt (114).jpg"),
     "Pourquoi nos lignes sont aussi fines",
     "L'acier est 3 à 5 fois plus rigide que l'aluminium massif, donc la "
     "structure porte loin sans s'épaissir.\nC'est ce qui donne ces traits "
     "nets, et une pergola qui ne s'impose pas devant la maison.",
     "S-LIGNES-FINES.jpg"),
    (os.path.join(G, "RAMIREZ/Selection Franck/_serign_gvoinot (17).jpg"),
     "Adossée à la maison, ou posée dans le jardin",
     "Adossée, elle prolonge votre pièce de vie et l'ombre commence dès que "
     "vous ouvrez la baie.\nAutoportée, elle crée un lieu supplémentaire, "
     "ailleurs dans le jardin, là où vous avez envie de vous asseoir.",
     "S-ADOSSEE-AUTOPORTEE.jpg"),
    (os.path.join(G, "Gruter/Gruter Selection Franck/stmarc_gvt (130).jpg"),
     "Vous avez déjà un pool house",
     "Un local en dur, souvent à toit plat et ouvert sur un ou deux côtés, mais "
     "pourtant le soleil entre quand même sous le pool house, et vous avez trop "
     "chaud.\n\nNous adossons la pergola au bâti existant, donc la surface à l'abri "
     "du soleil et de la chaleur s'étend sur toute la terrasse.",
     "S-POOL-HOUSE.jpg"),
    (os.path.join(V, "_LVM1653.jpg"), "Un puits de lumière",
     "Une partie du toit de la pergola reste ouverte, sans carrelets en bois "
     "exotique, et la lumière éclaire votre maison.\nVous gardez l'ombre sur la "
     "table, et la lumière d'éclairer votre maison (très utile pour les pergolas "
     "XL comme celle-ci).",
     "S-PUITS-DE-LUMIERE.jpg"),
]

# 06/10/2026 — Remplace « Un puits de lumière » (retirée : Franck ne veut pas en parler sur
# les réseaux). Aucune photo des pergolas exposées chez Maison St Sa ou Espi n'existe : on
# prend une vue assise sous la pergola de la villa Impian (Mickaël), sans l'ouverture du toit.
STORIES += [
    (os.path.join(V, "_LVM1651.jpg"), "Voir une pergola\nTeck Aménagement\navant de signer",
     "Nos pergolas sont exposées chez Maison St Sa, à Aix-en-Provence, et chez "
     "Meubles Espi, à Salon-de-Provence.\nVous pouvez vous asseoir dessous, toucher "
     "le bois et voir la finesse de la structure avant de vous décider.",
     "S-VOIR-AVANT-DE-SIGNER.jpg"),
]

# 19/10/2026 — Série du 26/10 au 28/12 (commande /stories-teck), 14 stories photo + texte,
# refaite le même jour sur les deux retours vidéo de Lilian (textes, photos et mise en page).
# Photos de Gabrielle Voinot (Parra, Spencer, Riera, Dansou, Daddi), de Mickaël (villa impian,
# Ansart) et un visuel 3D du projet Dansou. Chaque photo a été comparée aux 250 visuels déjà
# produits (stories, posts, pubs, pages, emails) : aucune n'y figure.
# ⚠️ Le projet Ansart n'est PAS celui de Romy (Lilian, 19/10/2026) : sa vidéo est seulement
# rangée dans le même dossier.
# ⚠️ On n'écrit jamais l'espacement des carrelets en centimètres (Lilian, 19/10/2026).
P = os.path.join(G, "PARRA/Selection Franck")
SP = os.path.join(G, "SPENCER/Selection Franck")
RI = os.path.join(G, "RIERA/Selection Franck")
STORIES += [
    (os.path.join(P, "karine_gvt  (18).jpg"), "Rester dehors quand tout le monde rentre",
     "Cet été, nous avons mesuré 42 °C au soleil sur la terrasse, et 32 °C à l'ombre de "
     "l'une de nos pergolas, thermomètre en main.\nCes 10 °C d'écart vous permettent de "
     "rester à table quand la chaleur fait rentrer tout le monde.",
     "S-RESTER-DEHORS.jpg"),
    (os.path.join(V, "_LVM1636.jpg"), "Vous avez déjà un store banne",
     # 20/10/2026, annotation de Franck relayée par Lilian : « mais ne vous protège pas de la chaleur ».
     "Sa toile vous donne de l'ombre, mais ne vous protège pas de la chaleur."
     "\n\nAdossée à votre maison, notre pergola place au-dessus de vous un bois "
     "exotique dense, que la chaleur ne traverse pas comme une toile.",
     "S-STORE-BANNE.jpg"),
    (os.path.join(SP, "annema_teck_voinot (511).jpg"), "Combien serez-vous à table ?",
     "Nous calculons la surface de votre pergola sur le nombre de personnes que vous voulez "
     "voir à l'ombre en même temps.\nC'est ce chiffre qui commande la portée de la structure, "
     "et non la taille de votre terrasse.",
     "S-COMBIEN-A-TABLE.jpg"),
    (os.path.join(P, "karine_gvt  (24).jpg"), "Aucune pergola sur catalogue",
     "Chaque projet est dessiné pour un extérieur précis, avec sa surface, son orientation "
     "et sa façade.\nC'est pour ça que nous ne donnons aucun tarif sans connaître les "
     "caractéristiques de votre terrasse.",  # Franck, 20/10/2026 (sens exact : question 25)
     "S-SANS-CATALOGUE.jpg"),
    # Texte de la hauteur posé dans le ciel, lignes resserrées (Lilian, 19/10/2026).
    (os.path.join(A, "_ECD7875.jpg"), "Au moins 2,50 m sous pergola",  # « la » retiré par Franck, 20/10/2026
     "Nous n'avons jamais posé de pergola à moins de 2,50 m de haut.\nAucune norme ne "
     "l'impose : c'est une question de confort et d'esthétisme.",
     "S-HAUTEUR.jpg"),
    (os.path.join(FRANCK, "3D/Visuels 3D/Projet Dansou/TECK Dansou visuel 4.jpg"),
     "Visiter votre pergola avant qu'elle existe",
     "Cette image est le visuel 3D de l'un de nos projets, dessiné avant sa pose.\nVous "
     "recevez le vôtre sous plusieurs angles, avec ou sans claustras, et nous l'ajustons "
     "autant de fois qu'il le faut.",
     "S-VISUEL-3D.jpg"),
    (os.path.join(V, "_LVM1623.jpg"), "Pour concevoir votre pergola, nous regardons d'abord un élément",
     "Cet élément, c'est l'orientation de votre terrasse.\n\nDe là, nous décidons la profondeur, "
     "la largeur et la position de votre pergola, pour que l'ombre tombe là où vous vous "
     "installez.",
     "S-ORIENTATION.jpg"),
    (os.path.join(A, "_ECD7859.jpg"), "Ne gâchez jamais votre vue pour une pergola",
     "Nos conceptions gardent votre vue sur la nature intacte.\nLa finesse de nos structures "
     "permet des projets très épurés, où la pergola reste discrète devant le paysage.",
     "S-VUE-INTACTE.jpg"),
    (os.path.join(RI, "riera_teck_gvt_43.jpg"), "Quelques centimètres",
     "Chaque trait de lumière au sol passe par l'espace laissé entre deux carrelets de bois.\n"
     "Nous choisissons la dimension des carrelets en fonction de l'ombre dont vous avez besoin.",
     "S-ESPACEMENT.jpg"),
    (os.path.join(V, "_LVM1644.jpg"), "Jusque sur vos murets en pierre",
     "Nos claustras en bois vous cachent du vis-à-vis, et ils s'installent aussi sur vos "
     "murets en pierre.\nLe bois et la pierre restent dans l'esprit des maisons "
     "méditerranéennes, faites de matériaux naturels.",
     "S-CLAUSTRA-MURET.jpg"),
    (os.path.join(G, "Dansou/Selection Franck/beausset_gvt (163).jpg"),
     "Combien de temps dure la pose ?",
     "Sur place, la pose de votre pergola dure une dizaine de jours.\nElle s'allonge s'il "
     "pleut, ou s'il faut d'abord couler une dalle ou réaliser votre terrasse.",
     "S-DUREE-DE-POSE.jpg"),
    (os.path.join(G, "Daddi/le_rove_teckamenagement_g_voinot_2_bd/bd_rove_teck_gvoinot_7.jpg"),
     # 20/10/2026, Franck : « Les matières sont différentes du coup très compliqué d'avoir les
     # mêmes coloris que la maison ». Donc « s'accorde », jamais « la même couleur ».
     # Puis sa consigne, le même jour : « le coloris de nos structures [est] choisi en fonction
     # des matières et des couleurs de leurs maisons », « nous privilégions des coloris en
     # harmonie avec les éléments autour de la pergola ».
     "Une teinte choisie pour votre maison",
     "Ici, le blanc de la structure s'accorde aux murs.\n\nNous choisissons le coloris de votre "
     "pergola selon les matières et les couleurs de votre maison, pour qu'il reste en harmonie "
     "avec tout ce qui l'entoure.",
     "S-COULEUR-FACADE.jpg"),
    # Le déjeuner, pas le dîner, et pas un mot sur la pluie (Lilian, 19/10/2026).
    (os.path.join(RI, "riera_teck_gvt_33.jpg"), "Un déjeuner qui dure tout l'après-midi",
     "Le repas est posé sur la table, et vous déjeunez à l'ombre, à l'abri de la chaleur, "
     "entre deux éclats de rire.\nPuis, tellement vous êtes bien installé sur le canapé et au "
     "frais, que vous décidez de rester là toute l'après-midi.",
     "S-TABLE-ET-CANAPE.jpg"),
    (os.path.join(V, "_LVM1659.jpg"), "L'été prochain se prépare cet hiver",
     "En concevant votre projet cet hiver, vous arrivez au printemps avec une pergola déjà "
     "dessinée, validée et installée.\n\nVous profitez de votre terrasse dès les premières "
     "chaleurs.",
     "S-ETE-PROCHAIN.jpg"),
]

# Photos à assombrir avant le scrim (fichier de sortie → force du voile).
SOMBRE = {"S-PUITS-DE-LUMIERE.jpg": 70, "S-POOL-HOUSE.jpg": 45, "S-VOIR-AVANT-DE-SIGNER.jpg": 60,
          # 19/10/2026, série d'octobre à décembre
          "S-RESTER-DEHORS.jpg": 70, "S-STORE-BANNE.jpg": 50, "S-COMBIEN-A-TABLE.jpg": 45,
          "S-SANS-CATALOGUE.jpg": 70, "S-HAUTEUR.jpg": 40, "S-ORIENTATION.jpg": 70,
          "S-VUE-INTACTE.jpg": 50, "S-ESPACEMENT.jpg": 60, "S-CLAUSTRA-MURET.jpg": 65,
          "S-DUREE-DE-POSE.jpg": 60, "S-COULEUR-FACADE.jpg": 60, "S-TABLE-ET-CANAPE.jpg": 45,
          "S-ETE-PROCHAIN.jpg": 70}

# Position de la découpe dans une photo paysage (fichier de sortie → 0 à 1, centre = 0.5).
CADRAGE = {"S-COULEUR-FACADE.jpg": 0.0}

# Mise en page resserrée, story par story : descente du bloc, interlignes du titre et du texte.
# S-HAUTEUR : le texte tient dans le ciel, au-dessus de la pergola (Lilian, 19/10/2026).
MISE_EN_PAGE = {"S-HAUTEUR.jpg": dict(descente=40, lt=74, li=40, g1=20, g2=34)}

# Story #13, la seule en mise en page « liste ».
LISTES = [
    (os.path.join(D, "dans_teck_gvoinot_w_3.jpg"),
     "Habiller votre pergola", "dans chaque détail.",
     [("Les voilages",
       "En lin ou en coton, noués aux poteaux, à déplier quand le soleil tourne."),
      ("La guirlande",
       "Accrochée aux carrelets, pour les soirées qui s'étirent."),
      ("Le claustra",
       "Il filtre le regard sans jamais enfermer l'espace."),
      ("L'éclairage",
       "Pensé et réglé avec vous, jusqu'à la tombée de la nuit.")],
     "S-LISTE-habiller-votre-pergola.jpg"),
]

if __name__ == "__main__":
    # Sans argument on n'écrase rien : les stories déjà publiées ont été
    # produites avant la descente du 17/08 et n'ont pas à bouger. On passe
    # les fichiers à (re)générer, ex. :
    #   python3 _generateur-stories.py S5-amenagement-densemble.jpg
    import sys

    voulus = set(sys.argv[1:])
    if not voulus:
        print("Rien à faire. Fichiers connus :")
        for a in STORIES:
            print("   ", a[3])
        for a in LISTES:
            print("   ", a[4])
    for args in STORIES:
        if args[3] in voulus:
            story(*args, sombre=SOMBRE.get(args[3], 0), cadrage=CADRAGE.get(args[3], 0.5),
                  **MISE_EN_PAGE.get(args[3], {}))
    for args in LISTES:
        if args[4] in voulus:
            liste(*args)
