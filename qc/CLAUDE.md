# Section QC — couverture des gènes & qualité de séquençage

Maquette de l'**onglet QC** de la page Case de Radiant. Fichier de travail : `qc_radiant.html`. Les conventions transversales (HTML autonome, vérif headless, terminologie, en-tête, partage) sont dans le `CLAUDE.md` **racine**.

## Contexte

Calquée sur l'onglet QC de l'app sœur **clin** (`~/src/clin-portal-ui`, `src/views/Prescriptions/Entity/Tabs/QC`) qui possède déjà deux sections (`General` niveau échantillon + `CouvertureGenique`). La maquette a donc **deux sous-sections** (sous-nav `.seg`) : **« Qualité de séquençage »** (niveau échantillon) et **« Couverture des gènes »**. Objectif secondaire : prototyper une meilleure présentation du niveau échantillon que celle de clin (aujourd'hui un dump brut de paires clé/valeur) pour guider l'amélioration de clin.

## Fichiers

- `qc_radiant.html` — maquette principale (autonome, données inlinées). C'est le fichier de travail.
- `build_mockup.py` — script qui a généré la première version de la maquette à partir de `test_gene_coverage.csv`. N'a pas été re-exécuté depuis l'ajout du modal exon et des autres features — le HTML est édité directement.
- `test_gene_coverage.csv` — données de couverture par gène qui ont servi à alimenter la maquette initiale.
- `QC_demo_multiqc_report.html` — rapport MultiQC (agrégé, 1 par famille). **Lié depuis la maquette** : bouton « Rapport MultiQC » de la vue d'ensemble (ouvert dans un nouvel onglet). Doit rester dans le même dossier que `qc_radiant.html` pour que le lien fonctionne.
- `41267.qc-coverage-region-2_cov_report.bed` — rapport Dragen pour l'échantillon 41267 : **la source cible** pour brancher les vraies données par exon du modal drill-down (voir « Notes techniques » plus bas).
- `47674.QC_report.json` — rapport JSON Dragen (niveau échantillon) pour l'échantillon 47674 : **source des données de la Vue d'ensemble**. Structure : `SamplesQC[0]` (groupes `DRAGEN_capture_coverage_metrics`, `DRAGEN_mapping_metrics`, `DRAGEN_cnv_metrics`, `DRAGEN_gvcf_metrics`, `DRAGEN_ploidy_estimation_metrics`, `Picard_CollectHsMetrics`) + `SequencingQC` (run/flowcell/kit). Les valeurs du proband sont inlinées telles quelles (`QC_RAW`/`SEQ_QC`).

## État de la maquette

### Sous-navigation
- **`.seg` `#qcNav`** — bascule entre **« Qualité de séquençage »** (`#secOverview`, niveau échantillon) et **« Couverture des gènes »** (`#secGenes`). Défaut : Qualité de séquençage. Câblage + `renderOverview()` dans `initControls()`.

### Vue d'ensemble (niveau échantillon) — `renderOverview()`
- **Tableau trio** (les 3 membres) : **exactement les 6 indicateurs mis en évidence par clin** (`QualityControlSummary`), dans son ordre — Sexe/ploïdie · Contamination · Couv. moyenne · Région ≥15x · Uniformité (>0,4×moy) · CNV passants. × 3 membres, pastilles colorées + badge de verdict global par colonne. En-tête de colonne = **sample submitter ID (`sid`, forme `DMxxxxxx`)**, pas l'ID séquençage interne (`id`). Seuils repris tels quels de clin (`QualityControlSummary/utils.tsx`). Un **bouton « i »** (`#ovInfoBtn`) ouvre un dialogue (`#ovInfoDlg`, corps `#ovInfoBody` rempli depuis les champs `help` de `HEAD_IND` + `SEX_HELP`) expliquant le seuil de chaque indicateur. Titre de section = **« Indicateurs »**, suivi d'un **badge de verdict global** (`globalV`) = pire statut sur tous les indicateurs × tous les échantillons (dans la démo : Attention). *(Le fold-80 avait été ajouté aux indicateurs le 2026-07-10 puis retiré le 2026-07-13 ; il reste en valeur brute dans le panneau de détail « Enrichissement ».)*
- **Pédigrée / parenté (Somalier, données simulées `PEDIGREE`)** — **section autonome** sous le tableau d'indicateurs (pas un indicateur par échantillon — décision 2026-07-13 pour éviter le doublon de verdict). Un **verdict familial unique** (badge Conforme/Échec) à côté du titre de section, puis la **table par paire** (`.ped-table`) : parenté mesurée vs attendue (0,50 = 1er degré / « non apparentés »), IBS0, IBS2, Statut. `pedPass()` = 1er degré si rel ≥ 0,35, non apparentés si rel < 0,20. Vocabulaire unifié Conforme/Échec. But clinique : détection d'inversion/mélange d'échantillon.
- **Deux rapports téléchargeables, à deux niveaux** : (a) **MultiQC** (agrégé, 1 par famille) — lien `.btn` dans l'en-tête de la section « Indicateurs », ouvre `QC_demo_multiqc_report.html` dans un nouvel onglet (comme le `window.open` de clin) ; (b) **Dragen JSON** (1 par échantillon) — bouton « Rapport Dragen (JSON) » dans la rangée des onglets de membre, reconstruit et télécharge le JSON du membre actif (`downloadReport()` / `memberReportJSON()` → `{SamplesQC:[…], SequencingQC}`, nom `${sid}.QC_report.json`).
- **Section « Principales métriques par échantillon » avec sélecteur de membre** (`.ov-memrow` sous le titre, à gauche : **menu déroulant** `#ovMemberSel`, libellés « relation (submitter ID) », variable `OV_MEMBER`) : la section détail reflète le membre choisi. Le tableau d'indicateurs (trio) n'a **pas** de sélecteur — il montre les 3 membres (la sélection n'y a pas de sens). Ordre des panneaux : **Alignement · Couverture · Enrichissement · Sexe · Variants · CNV · Séquençage (run)**. Métriques formatées ; verdicts inline uniquement pour les seuils définis par clin (duplication/fold-80 en valeur brute). Catalogue `OV_PANELS` (+ carte « Séquençage (run) » depuis `SEQ_QC`). Pas de `BAIT_SET` (doublon du kit). **La section « Toutes les métriques (format brut) » a été retirée** (2026-07-13) — le rapport complet s'obtient via le bouton de téléchargement.
- **Modèle de données `memberQC(key)`** : proband = `QC_RAW` réel ; mère/père = copie dégradée par facteur (`MEMBER_DEG`, coverage ↓, contamination ↑, fold-80 ↑, uniformité ↓, duplication ↑, lectures ↓, CNV fixés). Le tableau trio **et** le détail lisent cette même source → valeurs cohérentes entre le haut et le bas. À l'intégration, chaque membre aura son propre `QC_report.json`.

### Couverture des gènes — `#secGenes`
- **Sélecteur d'échantillon (trio)** — menu déroulant `<select>` `#sampleSel`, libellés « relation (submitter ID) » (ex. `Cas-index (DM189234)`). Données mère/père = données cas-index dégradées pour la démo.
- **Filtres** : recherche par gène, panel prédéfini, liste custom téléversée.
- **Critères QC** : profondeur minimale (seuil clinique) + complétude requise, avec dialogue d'aide « i ».
- **5 cartes de synthèse cliquables** (Gènes analysés / Conformes / Attention / Échec / Non mappables) — servent aussi de filtre de statut. Affordances : carte active teintée par catégorie + ✓, cartes non retenues estompées, et **indice sous les cartes** (`#statsHint`) qui invite à filtrer (« Cliquez une catégorie… ») ou affiche l'état actif (« Liste filtrée : X ✕ Tout afficher », réinitialisation en un clic).
- **Tableau principal** avec, de gauche à droite : case à cocher · Actions (SNV / CNV / IGV) · Gène · Taille · Couv. moyenne · **Exons hors crit.** · **Statut** · %≥Nx (10 seuils). Les deux colonnes de synthèse (exons, statut) sont placées **avant** le bloc %≥Nx pour rester visibles sans défilement horizontal (le tableau reste le plus étroit possible ; seul le détail par profondeur est à droite).
- **Colonne « Exons hors crit. »** (`exonFailStats()` / `exonFailCell()`) — nombre d'exons dont `cov[depthIdx] < cutoff` (même dégradation par échantillon que le modal / l'export BED) sur le total, ex. `1/5` (le % est dans l'infobulle, pas affiché, pour garder la valeur courte). Rouge si > 0, vert si 0, `—` si le gène n'a pas de données exon (`EXON_DATA` = 6 gènes seulement dans la maquette). Réagit aux critères actifs (profondeur + complétude) et à l'échantillon. **Cellule cliquable (icône loupe `.exon-cell`) qui ouvre le modal « Détail par exon »** — même action que le clic sur le nom de gène. Ajouté suite à un retour de relecture.
- **Barre au-dessus du tableau** : contrôles de sélection (« N sélectionné(s) », « Sélectionner tous les résultats », « Effacer la sélection ») + bouton **Exporter**.
- **Couv. moyenne** affichée dans l'en-tête de la carte, pondérée par taille des gènes, sur la sélection si présente sinon sur tout le filtre.
- **Modal « Détail par exon »** — accessible en cliquant un nom de gène (souligné en pointillé + **icône loupe** `.exon-ic` sur les gènes ayant un détail exon ; **indice** dans la légende sous le tableau : « Cliquez un nom de gène souligné pour la couverture par exon »). Contient : bouton d'aide « i », résumé pondéré du gène, schéma horizontal (pilules arrondies, largeur ∝ taille, couleur = statut à la profondeur active), tableau détaillé (n° · coord. · taille · couv. moyenne · min. couv. · %≥Nx · statut), **légende de couleur en bas** (mêmes bandes `band()` que la page des gènes), bouton **Copier les régions sous-couvertes (BED)**. Ouvrable aussi depuis la colonne « Exons hors crit. » (loupe).
- **Export CSV filtré** (bouton Exporter).
- **Note de limitation pour le rapport** — bouton « Note de limitation… » dans la barre au-dessus du tableau (à côté d'Exporter). Ouvre un dialogue (`#limitDlg`) avec un texte pré-formaté, éditable, listant les gènes sous les critères actifs groupés par statut (Échec / Attention / Non mappable), + bouton **Copier**. Portée = sélection si présente, sinon le filtre courant (recherche/panel/liste) ; le filtre de statut des cartes est volontairement ignoré. S'ouvre au début du texte. Voir `buildLimitationNote()`.

### Journal des changements
- **2026-07-08** — retrait de la colonne « Bases <Nx » du tableau principal.
- **2026-07-09** — session étoffée : ajout du modal drill-down par exon (donnée simulée pour 6 gènes), colonnes case-à-cocher + Actions à gauche, sélection multi-gènes avec couv. moyenne dynamique, remplacement des pastilles échantillon par un dropdown au format Radiant, ajouts UI mineurs, commit du fichier Dragen source.
- **2026-07-10** — deux ajouts : (1) **note de limitation pour le rapport** (`buildLimitationNote()` + `#limitDlg`) : texte pré-formaté, éditable, copiable, groupant les gènes sous les critères par statut ; pourcentage planché à 1 décimale. (2) **section Vue d'ensemble (niveau échantillon)** + sous-navigation `.seg`, alimentée par `47674.QC_report.json` : tableau trio à verdicts colorés, section détail groupée avec sélecteur de membre, dump brut repliable. *(Une bannière d'alerte « verdict global au premier coup d'œil » et un bandeau sample-level fold-80 côté couverture génique ont été prototypés puis retirés — le vrai fold-80 vit dans la vue d'ensemble, `FOLD_80_BASE_PENALTY` de Picard.)*
- **2026-07-13** — nombreux affinages de la Vue d'ensemble : panneaux réordonnés (Alignement · Couverture · Enrichissement · Sexe · Variants · CNV) ; submitter ID `DMxxxxxx` partout ; dialogue d'aide des seuils (`#ovInfoDlg`) ; retrait du fold-80 des indicateurs (retour aux 6 de clin) ; carte « Séquençage (run) » (contexte run retiré du titre) ; colonnes membres alignées à gauche ; sexe déclaré en clair. **En-tête de page** refait pour reproduire le `PageHeader` de Radiant (voir racine). Titres : h2 « Indicateurs », détail « Principales métriques par échantillon ». « proband » → « cas-index ». **Choix d'échantillon harmonisé** en menu déroulant dans les deux sections (per-section, non synchronisé, sans statut affecté). Deux rapports (MultiQC / Dragen JSON). Retrait de « Toutes les métriques (format brut) ». Terminologie « gènes analysés » (retrait de « périmètre »/« évalués »). Affordances de découvrabilité (filtre des cartes + clic gène → exon).
- **2026-07-13 (retours de relecture)** — ajout de la colonne **« Exons hors crit. »** au tableau par gène (cliquable/loupe, rouge si > 0) + légende de couleur dans le modal exon. Puis section **Pédigrée/parenté** (Somalier, données simulées) sous le tableau d'indicateurs : verdict familial unique + table par paire (d'abord prototypée aussi comme indicateur par membre, puis simplifiée pour éviter le doublon de verdict).

## Notes techniques

### Données simulées pour le drill-down
Les données par exon sont inlinées dans `qc_radiant.html` (constante `EXON_DATA`) pour 6 gènes en tête du tableau alphabétique : **AANAT, ABRAXAS2, ACKR4, ACTR3, AKR1B15, AKR1C2**.

**AKR1B15 est le cas vedette de la démo** : marqué « Attention » (~85 % à 15x) au niveau du gène, mais le modal révèle que 4 exons sur 5 sont à 100 % et **un exon (150 pb) est totalement à 0**. C'est précisément le scénario qui justifie la vue drill-down.

### Format des données Dragen
Le fichier `41267.qc-coverage-region-2_cov_report.bed` contient une ligne par région/exon avec les colonnes :
```
chrom  start  end  total_cvg  mean_cvg  Q1_cvg  median_cvg  Q3_cvg  min_cvg  max_cvg
pct_above_5  pct_above_15  pct_above_20  pct_above_30  pct_above_50
pct_above_100  pct_above_200  pct_above_300  pct_above_400  pct_above_500  pct_above_1000
```
Le mapping **gène → exons** n'est pas dans ce fichier (source annexe). Quand on branchera les vraies données, il faudra faire ce lookup côté backend et remplacer `EXON_DATA` par une fonction qui va chercher les régions d'un gène donné.

### Couverture moyenne pondérée
Le calcul dans `renderSelBar()` utilise `sum(gene.avg × gene.size) / sum(gene.size)` — c'est la moyenne pondérée par la taille des gènes, cliniquement plus significative qu'une moyenne arithmétique simple.

### Vue d'ensemble — seuils et données de démo
Les seuils de verdict des indicateurs de tête sont **repris tels quels de clin** (`clin-portal-ui/src/views/Prescriptions/Entity/QualityControlSummary/utils.tsx`) : sexe via couv. chrY/chrX vs sexe déclaré ; contamination > 2 % (orange) / > 5 % (rouge) ; couv. moyenne < 100x (rouge) ; région ≥15x < 95 % (rouge) ; uniformité (>0,4×moy) < 93,91 % (orange) ; CNV > 504 (orange). Principe : ne mettre en évidence que ces indicateurs-là. Le fold-80 avait été ajouté puis retiré ; comme la duplication, il reste en détail sans verdict. Le trio mère/père est **dérivé du proband** par `memberQC(key)` (facteurs `MEMBER_DEG`), de sorte que le tableau trio et le détail par membre restent cohérents ; à l'intégration, chaque membre a son propre `QC_report.json`.

### Compteurs SNV/CNV
`mockCount(gene, kind)` produit un compteur déterministe par hash du nom de gène. Distribution SNV : ~40 % à 0, la plupart entre 1 et 8, quelques-uns >10. CNV : ~85 % à 0. À remplacer par un lookup vers l'API variants de Radiant.

### Choix d'échantillon — harmonisé (décision 2026-07-13)
Les deux endroits où l'on choisit un échantillon utilisent **le même widget** : un **menu déroulant** `<select>` (`#sampleSel` pour la Couverture des gènes ; `#ovMemberSel` pour le détail « Principales métriques par échantillon »). Format des options = **« relation (submitter ID `DMxxxxxx`) »**, ex. `Cas-index (DM189234)`. Décisions retenues avec l'utilisateur :
- **Pas de sélecteur remonté/partagé** entre les deux sections ; chacune garde le sien. Ne pas synchroniser (`OV_MEMBER` ≠ `state.sample`) — c'est acceptable, car la sélection d'un seul échantillon n'a pas de sens pour le tableau d'indicateurs (qui montre les 3).
- **Pas de statut Affecté/non-affecté** dans le libellé (non pertinent pour le QC), ni ID séquençage ni ID d'échantillon SP-… : seulement relation + submitter ID.
- Style commun via la règle CSS `.samples select, #ovMemberSel`.
À l'intégration, le vrai composant Radiant est `SequencingVariantFiltersSelectItem` (`~/src/radiant-portal/frontend/apps/case/src/entity/variants/filters/sequencing-experiment-variant-filters.tsx`).

## Analyse clinique (généticien / diagnostic moléculaire)

Résumé des questions qu'un généticien se pose devant ce tableau et de la couverture actuelle de l'interface.

| Question clinique | Support actuel |
|---|---|
| Les gènes du panel/phénotype sont-ils couverts ? | **Très bon** — panel + liste custom + recherche |
| Alignement avec les seuils cliniques du labo | **Très bon** — sélecteurs profondeur + complétude |
| Granularité intra-gène (couverture par exon/région) | **Très bon** — modal drill-down avec schéma + tableau + export BED |
| Verdict sample-level global (moyenne, % à 20x, uniformité, contamination, sexe) | **En place** — Vue d'ensemble : tableau trio à verdicts + panneaux de détail |
| Voir les variants (SNV/CNV) associés à chaque gène | En place (liens vers onglet Variants + IGV, données stub) |
| Comparaison trio en une seule vue | **Partiel** — le tableau trio compare les 3 membres au niveau échantillon ; pas encore au niveau gène/exon |
| Note de limitation pré-formatée pour le rapport final | **En place** — bouton « Note de limitation… » → texte éditable/copiable groupé par statut |
| Annotation des gènes structurellement difficiles (pseudogènes, régions dupliquées) | Absent |
| Aide à la décision (Sanger, retest, méthode alternative) | Absent (hors scope court terme) |

## Prochaines étapes envisagées

- **Brancher les vraies données** : remplacer `EXON_DATA` simulé par un lookup depuis le fichier Dragen `.bed` (avec le mapping gène→exons annexe), remplacer `mockCount()` par l'API variants Radiant, brancher les liens IGV/SNV/CNV vers de vraies navigations.
- **Améliorer la Vue d'ensemble puis clin** — itérer sur la présentation (regroupements, seuils, ce qu'on met en avant vs en repli) pour ensuite améliorer la section `General` de clin, aujourd'hui un dump brut. Pistes : brancher les vraies données trio (chaque membre a son propre `QC_report.json`), déplacer les seuils « proposés » vers des seuils validés labo, lien depuis « Région ≥15x » vers la couverture génique (comme clin le fait déjà).
- **Autres modules QC** — qualité base par base, index de contamination inter-échantillons (`SequencingQC.index_contamination_stats`), etc.
- **Intégration dans `~/src/radiant-portal`** comme onglet de la page Case (et report des améliorations dans `~/src/clin-portal-ui`).
