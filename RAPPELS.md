# Rappels de publication par email

Un email part **1 heure avant** puis **10 minutes avant** chaque publication
(post photo, reel, story), de **rappels@buzznovawave.fr** vers
**lilian.coste@gmail.com**.

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

## Quel compte Resend

Lilian a **deux comptes Resend**. Celui qui compte ici est le **professionnel** :
c'est le seul où le domaine `buzznovawave.fr` est vérifié.

| | |
|---|---|
| Clé à utiliser | `~/.veille-keys/Resend Clé API compte pro.txt` |
| À ne **pas** utiliser | `~/.veille-keys/Clé API Resend pour taskboard lilian.md` (compte perso) |
| En CI | secret GitHub `RESEND_API_KEY`, même valeur |

La clé n'est **jamais écrite dans le dépôt**. Avec la clé du compte perso, chaque
envoi échouerait : le domaine ne lui appartient pas.

> **Un backslash suffit à tout casser.** Le script retire les backslashes de la
> clé, quelle que soit sa source. C'est une protection héritée du cron du
> 4 août 2026 : la clé était alors stockée dans un `.md`, où markdown échappe les
> underscores (`re\_Hf…` au lieu de `re_Hf…`), et Resend la refusait avec
> « API key is invalid ». Le fichier du compte pro est un `.txt`, donc épargné,
> mais la protection reste utile si la clé repasse un jour par du markdown.

## Historique de l'expéditeur

Jusqu'au 7 août 2026 les rappels partaient de `onboarding@resend.dev`, le domaine
de test partagé de Resend. Deux limites, qui ont coûté le rappel de la story #7
du 6 août : Gmail filtre lourdement ce domaine, et Resend n'autorise l'envoi
qu'au propriétaire du compte. Le passage à `rappels@buzznovawave.fr` lève les
deux, et ouvre la possibilité d'ajouter d'autres destinataires que Lilian.

## Installation (une seule action manuelle)

Le secret est déjà posé. S'il faut le refaire un jour :

1. `https://github.com/Lilian-coste/calendrier--ditorial-teck-am-nagement/settings/secrets/actions`
2. **New repository secret**
3. Nom : `RESEND_API_KEY`
4. Valeur : la clé de `~/.veille-keys/Resend Clé API compte pro.txt`

Puis vérifier avec un *Run workflow* en mode simulation.
