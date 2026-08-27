# `prescription/` — Création de cas

Maquette du **parcours de création d'un cas** dans Radiant : liste des cas → bouton
« Créer un cas » → formulaire. Le squelette est celui de **Radiant**
(`~/src/radiant-portal`), le déroulé s'inspire du formulaire de prescription de
**clin-prescription-ui** (`~/src/clin-prescription-ui`, `src/components/Prescription/`).

| Fichier | Rôle |
|---|---|
| **`create_case_radiant.html`** | **la maquette de référence** |
| `analysis_catalog_qlin.csv` | le catalogue d'analyses — **source des données de la maquette** |
| `create_case_radiant_detaille.html` | ancienne variante « lourde », **figée** (voir plus bas) |
| `CHANGEMENTS_MODELE.md` | registre des changements de modèle |

> On construit **par étape**, une section — parfois un seul champ — à la fois.
> Ne pas anticiper les sections suivantes.

## Ligne de conduite : le temps du clinicien

**Le critère de conception est le temps qu'un clinicien met à remplir le formulaire.**
Tout ce qui s'ajoute à l'écran se paie en temps de lecture. Conséquences pratiques :

- **Pas de texte explicatif** dans l'interface. Une étiquette de champ suffit ; si un champ a
  besoin d'être expliqué, c'est le champ qu'il faut revoir.
- **Les notes de conception restent dans le CSV et dans ce dépôt**, jamais à l'écran.
- **Compter les gestes.** Un clic supprimable doit l'être — le chemin nominal du choix
  d'analyse en demande **zéro** ; le clavier doit suffire de bout en bout.
- **Le boilerplate se replie** sous un `<details>` fermé : poids visuel nul, rien de perdu.
- **Densité plutôt que confort.** Une analyse = une ligne.

## Ligne de conduite : l'application reste générique

Radiant n'est pas un produit québécois. **Aucune notion propre à une juridiction ne doit
entrer dans le code ni dans l'interface** — elle vit dans les **données**.

Cas d'école, le **code du ministère (MSSS)** : plutôt qu'un champ dédié et une recherche
spéciale, il est mis **en préfixe du `name`** dans le catalogue. La recherche générique sur le
nom le trouve donc « gratuitement » (`55330` → `DYSM`), et un déploiement hors Québec n'a
qu'à ne pas préfixer ses noms — rien à changer dans l'application.

## État d'avancement

| # | Section | État |
|---|---|---|
| 0 | **Liste des cas** + bouton « Créer un cas » | ✅ fait |
| 1 | **Analyse** (choix dans le catalogue) | ✅ fait |
| 2 | Cas-index | à venir |
| 3 | **Signes cliniques** | ✅ maquette autonome dans `hpo/` |
| 4 | Examens paracliniques | à venir |
| 5 | Histoire et hypothèse diagnostique | à venir |
| 6 | Parents · 7 Projet · 8 Soumission | à venir |

## Structure — deux vues dans un seul fichier

### Vue 1 — Liste des cas (page d'accueil)

Reprise de `frontend/apps/case/src/exploration/case-exploration.tsx` :

- **`HeaderNavigation`** avec pour titre le total : « 8 Cas »
  (`case_exploration.case.title` = `{{total}} Cas`).
- **Carte** contenant une barre d'outils puis le tableau. Barre d'outils : champ de recherche
  (placeholder réel de Radiant, « Cas, séquençage, patient ou MRN »), quelques filtres, et
  à droite le bouton **« Créer un cas »** — le seul élément ajouté par rapport à Radiant.
- **Colonnes** = celles visibles par défaut d'après `cypress/pom/pages/CasesTable.ts` :
  Cas · Dossier · Priorité · Statut · **Type** · Analyse · Req. par · Dernière modification ·
  actions. Libellés français de `frontend/translations/common/fr.json`.
- La colonne **Type** reprend `AnalysisTypeCodeCell` : un badge **à icône seule** —
  `Biohazard` (somatique), `User` (germinal seul), `Users` (lignée germinale familiale).
- 8 rangées de démonstration, inventées, mais dont le code d'analyse existe au catalogue.

### Vue 2 — Création d'un cas

Le bouton bascule la vue (même page, la liste est masquée). Le fil d'Ariane **« ‹ Cas »**
ramène à la liste. **Pas de rail d'étapes** : le formulaire n'a qu'un champ.

**Deux options de UI empilées, pour arbitrage.** La carte « Analyse » apparaît en double :

- **Option 1** (en haut) — la liste ne s'ouvre **qu'à la frappe** (champ vidé, elle se
  referme), et un bouton lien **« Explorer le répertoire »** (au-dessus du champ, à droite)
  ouvre une **fenêtre modale** : la remarque RQDM de clin (algorithme clinique, prescripteurs
  autorisés, approbation du labo), puis la liste complète avec une **case à cocher** par
  analyse (une seule cochée à la fois), boutons Annuler / Sélectionner.
- **Option 2** (en dessous) — la liste complète tombe au focus : le comportement décrit
  ci-dessous. Elle est en dernier pour que sa liste déroulante ne recouvre pas l'autre carte.

Le JS est instancié (`INST[1]` / `INST[2]`) : les fonctions du combobox prennent le n°
d'option en premier argument — `choose(1,'DYSM')`, `openInline(2)`…

**Le champ *est* la recherche, et c'est la seule surface de choix.** On arrive, le curseur est
déjà dedans (`openForm()` donne le focus), on tape, `↵`. Au focus sans rien taper, les 37
analyses tombent en dessous — parcourir et chercher sont le même geste. Le postulat est que
**le clinicien sait ce qu'il veut** : le chemin nominal ne demande aucun clic.

```
Analyse demandée *
[🔍 Rechercher une analyse…                                              ]
   ┌────────────────────────────────────────────────────────────────────┐
   │ MMG    55340 - Maladies musculaires globales           Germinal    │
   │ DYSM   55330 - Dystrophies musculaires                 Germinal    │
   └────────────────────────────────────────────────────────────────────┘
```

- **Une analyse = une ligne** : `code` (largeur fixe, les noms s'alignent) · `name` · et à
  droite le tag `Germinal` / `Somatique` (`analysis_type_code`).
- **Ordre** = celui du CSV (= celui de la semence `qlin`).
- **Clavier de bout en bout** : `↑` `↓` parcourent, `↵` choisit, `esc` referme. Un clic hors
  du champ referme aussi.
- Les options réagissent au **`mousedown`** et non au `click`, sinon le `blur` du champ
  referme la liste avant que le clic n'arrive.

**La recherche porte sur le `code` et le `name`, rien d'autre.** Pas d'index sur la condition
(elle n'est plus affichée nulle part : chercher sur un champ invisible donne des résultats
inexplicables) ni de traitement particulier du code MSSS — voir la ligne de conduite sur la
généricité.

Une fois choisie, l'analyse tient en **une ligne**, et le « ✕ » à droite revient au champ,
vidé et focalisé :

```
[DYSM]  55330 - Dystrophies musculaires                                ✕
```

**Rien d'autre n'est affiché.** Ni la condition principale, ni le type : ce dernier apparaît
déjà dans le **badge de l'en-tête de page** (`👤 Germinal`), à côté du code. Le formulaire ne
répète pas ce que l'en-tête dit déjà.

La maquette n'embarque donc que `code`, `name` et `analysis_type_code` (ce dernier pour le tag
de la liste et le badge d'en-tête). `primary_condition` et `condition_code_system` ne sont ni
affichées ni cherchées ; elles restent dans le CSV, qui suit le modèle.

## Le catalogue — `analysis_catalog_qlin.csv`

**Le CSV est la source ; la maquette embarque une copie injectée de ses colonnes utiles.**
Après toute modification du CSV, régénérer le tableau `ANALYSES` du HTML.

Colonnes = modèle Notion « Radiant Prescription » §5 (`analysis_catalog`) :
`id, code, name, description, primary_condition, condition_code_system, analysis_type_code,
tenant_code`. Plus de `panel_id` (remplacée par `analysis_has_panels`).

**37 analyses**, tenant `qlin`. Provenance de chaque colonne :

| Colonne | Source |
|---|---|
| `id` | ordre de `radiant-portal/.../qlin/analysis_catalog.sql` — **préserve les `cases.analysis_catalog_id` existants** |
| `code`, `name` | `clin-fhir/.../CodeSystem-analysis-request-code.json` (`designation` fr) |
| préfixe de `name` | **code du ministère (MSSS)**, voir ci-dessous |
| `description` | vidée sur demande ; la colonne est conservée (`text NULL` au modèle) |
| `primary_condition`, `condition_code_system` | dérivés, codes **vérifiés contre l'API OLS4 de l'EBI** |
| `analysis_type_code` | `germline` / `somatic`, dérivé du tissu séquencé |

### Le code du ministère (MSSS)

Système `https://www.msss.gouv.qc.ca/repertoires/biomed`. Il **n'est pas** dans le CodeSystem
FHIR : il vit dans `clin-localstack/utils/fhir-operations/src/scripts/addMSSSCode.ts`
(backfill CLIN-4415, appliqué en QA/staging/prod) → 32 codes. Un 33ᵉ récupéré :
**`CONCO` = 55374**, d'après CLIN-5831 dans `clin-localstack/project-tasks/add-analysis-code/`,
recoupé par son HPO par défaut `HP:0032317` qui correspond à `ValueSet-conco-default-hpo.json`.

⚠️ **La source à jour est ailleurs** : `ListMSSSCodesService.java` dans **`clin-qlin-me-hybrid`**,
dépôt **non cloné sur cette machine**. C'est aussi là que vivent `soloAnalysisCodes`
(`Config.java`, solo/trio) et `SomaticAnalysisCode` (`Analysis.java`, le type). Si le dépôt est
cloné, reprendre ces trois listes de là plutôt que de les dériver.

**Quatre analyses sans code MSSS** — `RAPIDE`, `RETINO`, `SURD`, `NEUTP` : leur `name` est sans
préfixe. Soit elles n'en ont pas, soit il a été ajouté après le backfill (comme CONCO).

**`HLH` et `HLEB` partagent le code 55412.** Ce n'est pas une erreur de transcription :
`addMSSSCode.ts` détecte lui-même le cas et journalise un avertissement.

### Germinal / somatique

La ligne de partage est **le tissu séquencé**, pas le domaine clinique :

- **somatique** (tissu tumoral) : `EXTUM`, `TRATU`, `SHEMA`, `STMO` ;
- **germinal** — tout le reste, **y compris les trois panels de prédisposition au cancer**
  `TUHEM`, `TUPED`, `CONCO`, faits sur tissu normal.

**Les codes MSSS le confirment** : le bloc **65xxx contient exactement ces quatre analyses
somatiques**, les prédispositions sont dans le bloc germinal 55xxx, et `GENOR` a son propre
bloc 75xxx. Ce recoupement tranche le cas `STMO`, qui était resté douteux.

### Conditions principales

Codes **vérifiés contre l'API OLS4 de l'EBI** (`ebi.ac.uk/ols4/api/search`), aucun inventé.
`GENOR` et `RAPIDE` n'ont pas de condition (non spécifiques). `RHAB` est le seul en **HPO**
(`HP:0003201`) : la rhabdomyolyse est un phénotype, pas une maladie.

Sept codes restent **à valider avec le labo** — MONDO n'offre pas de terme satisfaisant, ou la
correspondance est une déduction. Ils ne sont **pas signalés à l'écran** (question pour le
labo, pas pour le prescripteur) :

| Code | Pourquoi |
|---|---|
| `HYPM` | seuls les sous-types `susceptibility to 1..5` existent ; le type 1 est retenu |
| `RHAB` | phénotype → **HPO**. Vérifier que le frontend résout un `HP:` comme un `MONDO:` |
| `DPSO` | « défaut de production de superoxyde » = défaut NADPH oxydase = **granulomatose septique chronique** — déduit du libellé |
| `HDIP` | pas de terme pour « hypogammaglobulinémie » seule → déficit immunitaire commun variable |
| `HLEB` | deux entités dans un panel ; seule l'hémophagocytose est codée |
| `EIII` | MONDO ne distingue pas l'immunité *intrinsèque* → code du parent |
| `MSMD` | MONDO ne code le MSMD que par sous-type génique → code du parent |

**Doublon `NPC` / `NEUTP`** : même libellé « Neutropénie congénitale » dans le CodeSystem, dans
la semence Radiant **et** même code MSSS absent des deux. À trancher avec le labo.

## Écarts assumés avec clin

- **Les mentions RQDM ont été retirées** — l'algorithme clinique du RQDM comme le texte sur
  les prescripteurs autorisés et l'approbation du labo. Dans clin, elles s'affichent à l'étape
  du choix d'analyse (`prescription.analysis.choici.modal.*`). Décision assumée : ce sont des
  textes qu'on lit une fois et qu'on ne relit jamais, et ils sont propres au réseau québécois.
  Si le labo y tient, l'endroit qui coûte le moins est la page du cas après soumission, pas le
  formulaire.
- **Il n'y a plus de fenêtre modale.** La liste déroulante sous le champ est la seule surface :
  elle montre tout, filtre à la frappe, et supprime une surface entière d'interface.
- **Le réflexe MMG a été retiré.** Dans clin, cocher « analyser en réflexe le panel global »
  est possible depuis les 5 panels musculaires spécialisés (`isMuscularAnalysisAndNotGlobal`).
  **Le modèle Notion ne prévoit aucune colonne pour ça** et le CSV n'en porte pas la trace :
  la case à cocher a donc disparu de la maquette. À réintroduire dès que le modèle le prévoit —
  c'est noté dans `CHANGEMENTS_MODELE.md`.
- **Familles de conditions supprimées** de la fenêtre de choix (volet gauche et en-têtes de
  groupe). Le regroupement logique n'existe plus qu'à travers l'ordre du CSV.

## La variante détaillée, figée

`create_case_radiant_detaille.html` est la première version, conservée pour arbitrage sur le
poids (46 ko contre 30, 4 analyses visibles d'un coup contre 18). Elle porte **l'ancien
catalogue et l'ancien modèle** et n'a pas la liste des cas : elle ne doit plus être modifiée,
c'est un point de comparaison historique. À supprimer une fois l'arbitrage acté.

## Vérification

```sh
google-chrome --headless=new --disable-gpu --window-size=1400,620 \
  --screenshot=out.png "file://$PWD/create_case_radiant.html"
```

Pour photographier un état interactif, injecter un appel avant `</body>` sur une copie
temporaire — `openForm()`, `openModal()`, `choose(1,'DYSM')`.
