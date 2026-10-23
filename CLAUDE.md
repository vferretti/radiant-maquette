# Radiant — Maquettes de sections

Ce dépôt contient des **maquettes HTML statiques** de différentes sections de l'application **Radiant** (`~/src/radiant-portal`), destinées à être intégrées comme onglets/sections de la page « Case » et à recueillir des commentaires avant intégration. Radiant est utilisé par des généticiens du CHU Sainte-Justine (diagnostics moléculaires : WES/WGS trios germinaux, panels ciblés). Plusieurs maquettes s'inspirent aussi de l'app sœur **clin** (`~/src/clin-portal-ui`).

## Organisation — un sous-répertoire par section

Chaque section vit dans son propre sous-répertoire, avec son propre `CLAUDE.md` (détails spécifiques) :

- **`qc/`** — QC : couverture des gènes + qualité de séquençage (niveau échantillon). Voir `qc/CLAUDE.md`.
- **`dashboard/`** — Aperçu : vue d'ensemble du cas (onglet « Aperçu », premier onglet, à gauche de « Détails »). Voir `dashboard/CLAUDE.md`.
- **`prescription/`** — Création de cas : parcours de saisie d'un nouveau cas, inspiré du formulaire de prescription de **clin-prescription-ui** (`~/src/clin-prescription-ui`). Liste des cas → bouton « Créer un cas » → formulaire. Catalogue d'analyses dans `prescription/analysis_catalog_qlin.csv`. Voir `prescription/CLAUDE.md` — et `prescription/CHANGEMENTS_MODELE.md` pour le registre des changements de modèle proposés.
- **`hpo/`** — Signes cliniques : sélection des phénotypes HPO (étape 3 du formulaire de
  prescription), portée du POC `~/src/poc_hpo`. L'arbre HPO complet (18 689 termes, FR/EN)
  est inliné — d'où le poids inhabituel du fichier. Voir `hpo/CLAUDE.md`.
- **`exploration/`** — Exploration des variants : section de premier niveau (hors cas) qui permet
  d'atteindre un variant par son **locus** (format gnomAD, `1-55051215-G-GA`) ou de lister les
  variants d'un **gène**. Comble le trou actuel : on ne peut atteindre un variant que par un cas.
  SNV et CNV (`GAIN:chr1:début-fin`). Voir `exploration/CLAUDE.md`.
- **`cnv/`** — CNV : analyse de la figure DRAGEN copy ratio / BAF / ROH du CQGC et de ses
  sources de données, en vue d'une version interactive. Pas encore de maquette ; les
  fichiers d'échantillon ne sont **pas versionnés**. Voir `cnv/CLAUDE.md`.
- *(à venir : autres sections — ex. `variants/`, `files/`… — chacune avec son `CLAUDE.md`.)*

Claude charge automatiquement ce `CLAUDE.md` racine **plus** celui du sous-répertoire où l'on travaille : garder ici ce qui est **transversal**, mettre le **spécifique** dans le sous-répertoire de la section.

## Conventions communes (toutes les maquettes)

- **HTML autonome, édité directement** : chaque maquette est un fichier `.html` unique, données inlinées, sans dépendance externe (sauf ressources explicitement liées, ex. un rapport MultiQC). Les éventuels scripts de génération (`build_mockup.py`) ne sont plus relancés — on édite le HTML.
- **Vérification en navigateur headless** : `google-chrome --headless=new --dump-dom` (structure) ou `--screenshot` (visuel) sur le fichier `file://…`. Aucun serveur nécessaire.
- **UI en français.** Terminologie transversale : **« cas-index »** (jamais « proband ») ; nom d'échantillon affiché = **submitter ID `DMxxxxxx`**.
- **Fidélité au produit** : reproduire les composants réels de Radiant/clin quand ils existent — p. ex. l'**en-tête de page** reproduit le `PageHeader` de Radiant (`apps/case/src/entity/layout/header.tsx` + `components/base/page/page-header.tsx`) ; le type de cas (`germline` / `germline_family` / `somatic`) porte l'info famille/solo. Ne mettre en évidence (verdicts colorés) **que des seuils validés par le labo** (repris de clin) ; tout seuil ajouté doit être marqué « proposé / à valider ».
- **Partage** : packager une maquette + ses ressources dans un **zip contenant un dossier** (léger pour courriel — le HTML MultiQC compresse à ~17 %). Les `.zip` ne sont pas versionnés (`.gitignore`).

## Sources de référence

- **Radiant** : `~/src/radiant-portal` — page Case dans `frontend/apps/case/src/entity`.
- **clin** (app sœur) : `~/src/clin-portal-ui` — onglet QC dans `src/views/Prescriptions/Entity/Tabs/QC`.
