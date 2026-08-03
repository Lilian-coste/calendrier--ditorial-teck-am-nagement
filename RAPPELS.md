# Rappels de publication par email

Un email part **1 heure avant** puis **10 minutes avant** chaque publication
(post photo, reel, story), vers **lilian.coste@gmail.com**.

Tout tourne sur GitHub et Resend : les rappels arrivent **même Mac éteint**.

## Ce que contient l'email

L'objet dit l'essentiel en un coup d'œil : `⚡ Story #6 dans 1h`, `📷 Post #4 dans 10 min`.
Le corps reprend l'angle, l'heure exacte de publication, **la légende complète prête à copier**
et un lien vers le calendrier.

## Comment ça marche

| | |
|---|---|
| Source du planning | `index.html`, le tableau `POSTS`. Aucune date à saisir deux fois. |
| Programmation | `scripts/rappels-publication.mjs` |
| Déclencheur | GitHub Actions, tous les jours à 03:00 UTC (05:00 à Paris) |
| Envoi | Resend, avec `scheduled_at` à la minute près |

Le cron ne programme que les rappels des **prochaines 24 heures**. C'est voulu :
la clé Resend est restreinte à l'envoi, elle ne peut **pas annuler** un email déjà
programmé. En ne prenant que 24 heures d'avance, un décalage du planning ne peut
presque jamais laisser passer un rappel devenu faux. Et comme Resend gère
l'horodatage exact, le retard habituel de GitHub Actions n'a aucun effet sur
l'heure de réception.

La fenêtre est calculée à partir de l'heure de cron théorique du jour, pas de
l'heure réelle de démarrage. Deux exécutions se suivent donc sans jamais se
recouvrir, ce qui évite les doublons sans avoir à stocker d'état.

## ⚠️ Si tu décales à nouveau le planning

Change les dates dans `index.html`, commit, et c'est tout : le cron du lendemain
lit le nouveau planning.

**Le seul cas à surveiller** : décaler un contenu qui doit être publié dans les
24 heures. Ses rappels sont peut-être déjà partis chez Resend et ne peuvent plus
être annulés. Tu recevrais un rappel à l'ancienne heure. Sans conséquence, mais
autant le savoir.

> Pour supprimer cette limite, il suffirait d'une clé Resend **Full access**
> (Resend → API Keys → permission « Full access »). Le script pourrait alors
> annuler et reprogrammer, et on programmerait tout le mois d'un coup.

## Lancer à la main

Depuis l'onglet **Actions** du dépôt → « Rappels de publication » → *Run workflow*.
Options : simulation, largeur de fenêtre, départ immédiat.

En local :

```bash
node scripts/rappels-publication.mjs --dry-run --from-now --hours=800   # tout voir
node scripts/rappels-publication.mjs --from-now --hours=12              # programmer aujourd'hui
```

La clé API vient de `RESEND_API_KEY`, sinon du fichier
`~/.veille-keys/Clé API Resend pour taskboard lilian.md`. **Elle n'est jamais
écrite dans le dépôt.**

## Installation (une seule action manuelle)

Ajouter le secret sur GitHub, sinon le cron échoue :

1. `https://github.com/Lilian-coste/calendrier--ditorial-teck-am-nagement/settings/secrets/actions`
2. **New repository secret**
3. Nom : `RESEND_API_KEY`
4. Valeur : la clé de `~/.veille-keys/Clé API Resend pour taskboard lilian.md`

Puis vérifier avec un *Run workflow* en mode simulation.
