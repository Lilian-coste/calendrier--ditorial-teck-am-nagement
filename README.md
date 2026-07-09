# Calendrier éditorial Instagram — Teck Aménagement

Calendrier interactif des publications Instagram : planning glisse-dépose, légendes prêtes à copier, statuts et horaires par post.

## Contenu

- **`index.html`** — le calendrier interactif (page servie à la racine sur Vercel).
- **`calendrier-editorial.md`** — version texte des légendes (secours / lecture rapide).
- **`assets/`** — visuels des posts.

## Déploiement Vercel

Site 100 % statique. Sur Vercel : importer ce dépôt, aucun build (framework « Other »), la racine sert `index.html`. Le lien obtenu est partageable au client.

Les statuts, dates et heures modifiés dans l'interface sont stockés dans le navigateur du visiteur (localStorage) ; le planning par défaut est intégré au fichier.
