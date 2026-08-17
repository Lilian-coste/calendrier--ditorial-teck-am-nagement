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


def F(size, index=REG):
    return ImageFont.truetype(HN, size, index=index)


def load(path):
    """Recadre plein cadre en 9:16 → 1080×1920. On se fie à l'EXIF (pas de
       rotation manuelle, sinon les paysages se couchent)."""
    im = ImageOps.exif_transpose(Image.open(path)).convert("RGB")
    w, h = im.size
    t = 9 / 16
    if w / h > t:
        nw = int(h * t)
        im = im.crop(((w - nw) // 2, 0, (w - nw) // 2 + nw, h))
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


def story(image_path, titre, info, fname, highlight=None, descente=DESCENTE):
    im = load(image_path)
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
        y += 84
    y += 30
    d.line([(90, y), (200, y)], fill=CLAIR, width=3)
    y += 44
    for line in wrap(info, fi, 880):
        d.text((90, y), line, font=fi, fill=(238, 244, 252))
        y += 48
    im.save(os.path.join(OUT, fname), quality=92)
    print("✓", fname)


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
    im.save(os.path.join(OUT, fname), quality=92)
    print("✓", fname)


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
            story(*args)
    for args in LISTES:
        if args[4] in voulus:
            liste(*args)
