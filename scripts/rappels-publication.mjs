#!/usr/bin/env node
/**
 * Rappels de publication Instagram — Teck Aménagement
 * ===================================================
 *
 * Envoie à Lilian un email 1 heure puis 10 minutes avant chaque publication
 * (post photo, reel, story). Les emails partent de Resend, donc ils arrivent
 * même quand le Mac est éteint.
 *
 * POURQUOI CE DÉCOUPAGE
 * ---------------------
 * La clé Resend disponible est restreinte à l'envoi : elle ne peut ni lister,
 * ni annuler, ni modifier un email déjà programmé. On ne peut donc pas
 * programmer les 27 publications d'un coup, sinon le moindre décalage du
 * planning enverrait des rappels devenus faux, sans moyen de les rattraper.
 *
 * D'où le fonctionnement : un cron tourne chaque jour et ne programme que les
 * rappels des prochaines 24 heures. Resend se charge de l'horodatage exact, ce
 * qui rend la latence du cron sans importance. Et comme on ne programme qu'à
 * 24 heures d'avance, un changement de planning n'a presque aucune chance
 * d'avoir déjà été figé chez Resend.
 *
 * PAS DE DOUBLON, SANS FICHIER D'ÉTAT
 * -----------------------------------
 * La fenêtre n'est pas calculée à partir de « maintenant » mais à partir de
 * l'heure de cron théorique du jour (CRON_HOUR_UTC). Deux exécutions
 * consécutives couvrent donc deux fenêtres contiguës qui ne se recouvrent
 * jamais, même si GitHub Actions démarre le job avec du retard.
 *
 * USAGE
 * -----
 *   node scripts/rappels-publication.mjs                 # programme la fenêtre du jour
 *   node scripts/rappels-publication.mjs --dry-run       # affiche sans rien envoyer
 *   node scripts/rappels-publication.mjs --hours=48      # élargit la fenêtre (rattrapage)
 *   node scripts/rappels-publication.mjs --from-now      # fenêtre à partir de maintenant
 *
 * La clé API est lue dans RESEND_API_KEY (secret GitHub en CI, fichier
 * ~/.veille-keys/ en local). Elle n'est jamais écrite dans le dépôt.
 */

import fs from "node:fs";
import path from "node:path";
import os from "node:os";
import { fileURLToPath } from "node:url";

const RACINE = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");

/** Destinataire des rappels. */
const DESTINATAIRE = "lilian.coste@gmail.com";

/** Expéditeur. onboarding@resend.dev n'écrit qu'au propriétaire du compte Resend, ce qui suffit ici. */
const EXPEDITEUR = "Planning Instagram <onboarding@resend.dev>";

/** Combien de temps avant la publication chaque rappel part. */
const RAPPELS = [
  { minutes: 60, libelle: "dans 1h" },
  { minutes: 10, libelle: "dans 10 min" },
];

/** Heure de cron théorique, en UTC. Doit rester identique à celle du workflow. */
const CRON_HOUR_UTC = 3;

/** Le planning est saisi en heure de Paris. */
const FUSEAU = "Europe/Paris";

const ETIQUETTES = {
  post: { nom: "Post photo", icone: "📷", couleur: "#2f6f9f" },
  reel: { nom: "Reel", icone: "🎬", couleur: "#7c5cbf" },
  story: { nom: "Story", icone: "⚡", couleur: "#2f7d4f" },
};

// ---------------------------------------------------------------------------
// Lecture du planning
// ---------------------------------------------------------------------------

/**
 * Extrait le tableau POSTS de index.html, qui reste la source de vérité unique
 * du planning : le calendrier que Lilian et Franck consultent et ces rappels ne
 * peuvent donc pas diverger.
 */
function lirePlanning() {
  const fichier = path.join(RACINE, "index.html");
  const html = fs.readFileSync(fichier, "utf8");

  const bloc = html.match(/const POSTS = \[[\s\S]*?\n\];/);
  if (!bloc) {
    throw new Error(
      "Le tableau POSTS est introuvable dans index.html. " +
        "Sa structure a du changer : il faut mettre a jour ce script."
    );
  }

  // Les légendes interpolent ces constantes, déclarées plus haut dans index.html.
  const SIG = lireConstante(html, "SIG");
  const CREDIT = lireConstante(html, "CREDIT");
  const CREDIT_M = lireConstante(html, "CREDIT_M");

  const source = bloc[0].replace("const POSTS =", "").replace(/;\s*$/, "");
  const evaluer = new Function("SIG", "CREDIT", "CREDIT_M", `return (${source});`);
  const posts = evaluer(SIG, CREDIT, CREDIT_M);

  if (!Array.isArray(posts) || posts.length === 0) {
    throw new Error("Le planning lu dans index.html est vide.");
  }
  return posts;
}

function lireConstante(html, nom) {
  const m = html.match(new RegExp(`const ${nom}\\s*=\\s*"((?:[^"\\\\]|\\\\.)*)"`));
  return m ? m[1].replace(/\\"/g, '"') : "";
}

// ---------------------------------------------------------------------------
// Fuseau horaire
// ---------------------------------------------------------------------------

/** Décalage d'Europe/Paris par rapport à UTC, en minutes, à un instant donné. */
function decalageParis(instantMs) {
  const format = new Intl.DateTimeFormat("en-US", {
    timeZone: FUSEAU,
    hour12: false,
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
  });
  const p = Object.fromEntries(
    format.formatToParts(new Date(instantMs)).map((x) => [x.type, x.value])
  );
  const commeUtc = Date.UTC(+p.year, +p.month - 1, +p.day, +p.hour % 24, +p.minute, +p.second);
  return (commeUtc - instantMs) / 60000;
}

/**
 * Convertit une date « 2026-08-04 » et une heure « 18h00 » exprimées à Paris en
 * instant absolu. L'itération fait converger le calcul même sur les jours de
 * changement d'heure.
 */
function instantDepuisParis(dateIso, heure) {
  const [annee, mois, jour] = dateIso.split("-").map(Number);
  const m = /^(\d{1,2})\s*h\s*(\d{0,2})$/i.exec(heure.trim());
  if (!m) throw new Error(`Heure illisible : « ${heure} »`);
  const heures = Number(m[1]);
  const minutes = m[2] ? Number(m[2]) : 0;

  const naif = Date.UTC(annee, mois - 1, jour, heures, minutes);
  let instant = naif;
  for (let i = 0; i < 3; i++) instant = naif - decalageParis(instant) * 60000;
  return instant;
}

/** Formate un instant pour l'affichage, en heure de Paris. */
function afficherParis(instantMs, options) {
  return new Intl.DateTimeFormat("fr-FR", { timeZone: FUSEAU, ...options }).format(
    new Date(instantMs)
  );
}

// ---------------------------------------------------------------------------
// Construction des rappels
// ---------------------------------------------------------------------------

/**
 * Liste tous les rappels à envoyer dans la fenêtre demandée.
 * Un rappel déjà dépassé au moment du calcul est ignoré : Resend refuse une
 * date d'envoi passée.
 */
function rappelsDeLaFenetre(posts, debutFenetre, finFenetre, maintenant) {
  const rappels = [];

  for (const post of posts) {
    if (!post.date || !post.heure) continue; // contenu non planifié
    if (post.status === "publie") continue; // déjà publié

    const publication = instantDepuisParis(post.date, post.heure);

    for (const rappel of RAPPELS) {
      const envoi = publication - rappel.minutes * 60000;
      if (envoi < debutFenetre || envoi >= finFenetre) continue;
      if (envoi <= maintenant) continue;
      rappels.push({ post, publication, envoi, libelle: rappel.libelle });
    }
  }

  return rappels.sort((a, b) => a.envoi - b.envoi);
}

// ---------------------------------------------------------------------------
// Contenu de l'email
// ---------------------------------------------------------------------------

function sujet({ post, libelle }) {
  const e = ETIQUETTES[post.type];
  // Volontairement court : les objets d'email restent sous 32 caractères.
  return `${e.icone} ${e.nom.split(" ")[0]} #${post.num} ${libelle}`;
}

function corpsTexte({ post, publication, libelle }) {
  const e = ETIQUETTES[post.type];
  const quand = afficherParis(publication, {
    weekday: "long",
    day: "numeric",
    month: "long",
    hour: "2-digit",
    minute: "2-digit",
  });

  const lignes = [
    `${e.nom} #${post.num} ${libelle}`,
    "",
    post.angle,
    `Publication ${quand}`,
    "",
  ];

  if (post.cap) {
    lignes.push("--- Légende à copier ---", "", post.cap, "");
  }
  if (post.phLabel) {
    lignes.push(`Visuel : ${post.phLabel}`, "");
  }

  lignes.push("Calendrier : https://calendrier-ditorial-teck-am-nagemen.vercel.app/");
  return lignes.join("\n");
}

function corpsHtml({ post, publication, libelle }) {
  const e = ETIQUETTES[post.type];
  const quand = afficherParis(publication, {
    weekday: "long",
    day: "numeric",
    month: "long",
    hour: "2-digit",
    minute: "2-digit",
  });

  const legende = post.cap
    ? `<p style="margin:0 0 8px;font-size:12px;letter-spacing:.08em;text-transform:uppercase;color:#8a8a8a">Légende à copier</p>
       <pre style="margin:0;padding:16px;background:#f6f7f9;border-radius:10px;border:1px solid #e6e8ec;font:14px/1.6 -apple-system,Segoe UI,Roboto,sans-serif;white-space:pre-wrap;color:#1c1c1e">${echapper(
         post.cap
       )}</pre>`
    : "";

  const visuel = post.phLabel
    ? `<p style="margin:16px 0 0;font-size:14px;color:#6b6b6b">Visuel : ${echapper(post.phLabel)}</p>`
    : "";

  return `<!doctype html>
<html lang="fr"><body style="margin:0;padding:24px;background:#f0f1f4;font-family:-apple-system,Segoe UI,Roboto,sans-serif;color:#1c1c1e">
  <div style="max-width:560px;margin:0 auto;background:#fff;border-radius:14px;overflow:hidden;border:1px solid #e2e4e9">
    <div style="padding:20px 24px;background:${e.couleur};color:#fff">
      <p style="margin:0;font-size:13px;opacity:.85">${e.icone} ${echapper(e.nom)} #${post.num}</p>
      <p style="margin:4px 0 0;font-size:21px;font-weight:600">Publication ${echapper(libelle)}</p>
    </div>
    <div style="padding:24px">
      <p style="margin:0 0 6px;font-size:17px;font-weight:600">${echapper(post.angle)}</p>
      <p style="margin:0 0 22px;font-size:14px;color:#6b6b6b">${echapper(quand)}</p>
      ${legende}
      ${visuel}
      <p style="margin:24px 0 0">
        <a href="https://calendrier-ditorial-teck-am-nagemen.vercel.app/"
           style="display:inline-block;padding:11px 18px;background:#1c1c1e;color:#fff;border-radius:8px;text-decoration:none;font-size:14px">
          Ouvrir le calendrier
        </a>
      </p>
    </div>
  </div>
</body></html>`;
}

function echapper(texte) {
  return String(texte)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

// ---------------------------------------------------------------------------
// Envoi
// ---------------------------------------------------------------------------

/**
 * Nettoie une clé API brute.
 *
 * Les backslashes sont retirés : la clé est stockée dans un fichier `.md` où
 * les underscores sont échappés par la syntaxe markdown (`re\_Hf…`). Copier ce
 * fichier tel quel donne donc une clé que Resend refuse avec « API key is
 * invalid ». C'est exactement ce qui a fait échouer le cron du 4 août 2026 :
 * la valeur collée dans le secret GitHub contenait les deux backslashes.
 * Aucune clé Resend n'en contient, les retirer est donc sans risque.
 */
function nettoyerCle(brut) {
  return String(brut).replace(/\\/g, "").trim();
}

/** Récupère la clé API : variable d'environnement en CI, fichier local sinon. */
function cleResend() {
  if (process.env.RESEND_API_KEY) return nettoyerCle(process.env.RESEND_API_KEY);

  const local = path.join(os.homedir(), ".veille-keys", "Clé API Resend pour taskboard lilian.md");
  if (fs.existsSync(local)) {
    return nettoyerCle(fs.readFileSync(local, "utf8"));
  }
  throw new Error(
    "Cle Resend introuvable. Renseigne RESEND_API_KEY " +
      "(secret GitHub en CI, ~/.veille-keys/ en local)."
  );
}

async function programmer(rappel, cle) {
  const reponse = await fetch("https://api.resend.com/emails", {
    method: "POST",
    headers: { Authorization: `Bearer ${cle}`, "Content-Type": "application/json" },
    body: JSON.stringify({
      from: EXPEDITEUR,
      to: [DESTINATAIRE],
      subject: sujet(rappel),
      text: corpsTexte(rappel),
      html: corpsHtml(rappel),
      scheduled_at: new Date(rappel.envoi).toISOString(),
    }),
  });

  const corps = await reponse.json().catch(() => ({}));
  if (!reponse.ok) {
    throw new Error(`Resend a repondu ${reponse.status} : ${JSON.stringify(corps)}`);
  }
  return corps.id;
}

// ---------------------------------------------------------------------------
// Point d'entrée
// ---------------------------------------------------------------------------

/** Sur GitHub Actions, ce préfixe transforme la ligne en annotation d'échec. */
function prefixeErreur() {
  return process.env.GITHUB_ACTIONS === "true" ? "::error::" : "";
}

/**
 * Vérifie que la clé est acceptée par Resend, sans envoyer le moindre email.
 *
 * Utile en simulation : jusqu'ici le mode `--dry-run` n'appelait jamais Resend,
 * il ne pouvait donc pas détecter une clé invalide. C'est ce qui a permis au
 * secret mal collé de passer inaperçu jusqu'au premier vrai cron.
 *
 * Réponses attendues :
 *   200 — clé complète ;
 *   401 « restricted to only send emails » — clé d'envoi valide, le cas normal ;
 *   400 « API key is invalid » — clé fausse, tronquée ou mal collée.
 */
async function verifierCle() {
  let cle;
  try {
    cle = cleResend();
  } catch (erreur) {
    console.error(`${prefixeErreur()}${erreur.message}`);
    return false;
  }

  const reponse = await fetch("https://api.resend.com/domains", {
    headers: { Authorization: `Bearer ${cle}` },
  });
  const corps = await reponse.json().catch(() => ({}));
  const message = corps.message || "";

  if (reponse.status === 200 || /restricted/i.test(message)) {
    console.log(`Cle Resend valide (${cle.length} caracteres).`);
    return true;
  }

  console.error(
    `${prefixeErreur()}Cle Resend refusee : ${reponse.status} ${message}. ` +
      "Verifie la valeur du secret RESEND_API_KEY : elle ne doit contenir " +
      "ni backslash, ni espace, ni retour a la ligne."
  );
  return false;
}

async function main() {
  const args = process.argv.slice(2);
  const simulation = args.includes("--dry-run");
  const depuisMaintenant = args.includes("--from-now");
  const heures = Number((args.find((a) => a.startsWith("--hours=")) || "").split("=")[1]) || 24;

  const maintenant = Date.now();

  // Fenêtre ancrée sur l'heure de cron théorique du jour, pour que deux
  // exécutions successives ne se recouvrent jamais malgré la latence du cron.
  let debut;
  if (depuisMaintenant) {
    debut = maintenant;
  } else {
    const aujourdhui = new Date(maintenant);
    debut = Date.UTC(
      aujourdhui.getUTCFullYear(),
      aujourdhui.getUTCMonth(),
      aujourdhui.getUTCDate(),
      CRON_HOUR_UTC
    );
    if (debut > maintenant) debut -= 24 * 3600_000; // cron pas encore passé aujourd'hui
  }
  const fin = debut + heures * 3600_000;

  const posts = lirePlanning();
  const rappels = rappelsDeLaFenetre(posts, debut, fin, maintenant);

  const fmt = { day: "2-digit", month: "2-digit", hour: "2-digit", minute: "2-digit" };
  console.log(`Planning lu : ${posts.length} contenus.`);
  console.log(
    `Fenetre : ${afficherParis(debut, fmt)} -> ${afficherParis(fin, fmt)} (heure de Paris).`
  );

  // En simulation, on contrôle la clé même quand la fenêtre est vide : c'est ce
  // qui rend le « Run workflow » en mode simulation réellement probant, sans
  // envoyer ni programmer quoi que ce soit.
  if (simulation && !(await verifierCle())) {
    process.exitCode = 1;
  }

  if (rappels.length === 0) {
    console.log("Aucun rappel a programmer sur cette fenetre.");
    return;
  }

  let envoyes = 0;
  const echecs = [];

  for (const rappel of rappels) {
    const ligne =
      `${afficherParis(rappel.envoi, fmt)} -> ${sujet(rappel)} ` +
      `(publication ${afficherParis(rappel.publication, fmt)})`;

    if (simulation) {
      console.log(`[simulation] ${ligne}`);
      continue;
    }

    try {
      const id = await programmer(rappel, cleResend());
      console.log(`OK ${ligne} — Resend ${id}`);
      envoyes++;
    } catch (erreur) {
      // Le préfixe `::error::` fait remonter la cause dans les annotations du
      // job. Sans lui, l'échec du 4 août 2026 n'affichait que « exit code 1 »
      // et il fallait ouvrir les logs pour comprendre.
      console.error(`${prefixeErreur()}ECHEC ${ligne} — ${erreur.message}`);
      echecs.push(erreur.message);
    }
  }

  if (simulation) {
    console.log(`\n${rappels.length} rappel(s) seraient programmes.`);
    return;
  }

  console.log(`\n${envoyes} rappel(s) programmes, ${echecs.length} echec(s).`);
  if (echecs.length > 0) process.exit(1);
}

main().catch((erreur) => {
  console.error(`${prefixeErreur()}Echec : ${erreur.message}`);
  process.exit(1);
});
