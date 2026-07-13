# Radiant — Maquette QC couverture des gènes

## Contexte

Ce repo contient une **maquette HTML statique** pour une nouvelle section QC à intégrer dans l'application Radiant (`~/src/radiant-portal`). L'intention est de l'ajouter comme **onglet dans la page « Case »**, à côté des onglets existants (Détails, Variants, Fichiers).

Radiant est utilisé par des généticiens du CHU Sainte-Justine pour établir des diagnostics moléculaires (WES/WGS trios germinaux, panels ciblés).

La maquette couvre désormais **deux sections QC**, calquées sur l'onglet QC de l'app sœur **clin** (`~/src/clin-portal-ui`, `src/views/Prescriptions/Entity/Tabs/QC`) qui possède déjà deux sections (`General` niveau échantillon + `CouvertureGenique`) : une **Vue d'ensemble (niveau échantillon)** et la **Couverture des gènes**. Objectif secondaire : prototyper une meilleure présentation du niveau échantillon que celle de clin (aujourd'hui un dump brut de paires clé/valeur) pour guider l'amélioration de clin.

## Fichiers

- `qc_gene_coverage.html` — maquette principale (autonome, données inlinées). C'est le fichier de travail.
- `build_mockup.py` — script qui a généré la première version de la maquette à partir de `test_gene_coverage.csv`. N'a pas été re-exécuté depuis l'ajout du modal exon et des autres features — le HTML est édité directement.
- `test_gene_coverage.csv` — données de couverture par gène qui ont servi à alimenter la maquette initiale.
- `QC_demo_multiqc_report.html` — rapport MultiQC (agrégé, 1 par famille). **Lié depuis la maquette** : bouton « Rapport MultiQC » de la vue d'ensemble (ouvert dans un nouvel onglet). Doit rester dans le même dossier que `qc_gene_coverage.html` pour que le lien fonctionne.
- `41267.qc-coverage-region-2_cov_report.bed` — rapport Dragen pour l'échantillon 41267 : **la source cible** pour brancher les vraies données par exon du modal drill-down (voir « Notes techniques » plus bas).
- `47674.QC_report.json` — rapport JSON Dragen (niveau échantillon) pour l'échantillon 47674 : **source des données de la Vue d'ensemble**. Structure : `SamplesQC[0]` (groupes `DRAGEN_capture_coverage_metrics`, `DRAGEN_mapping_metrics`, `DRAGEN_cnv_metrics`, `DRAGEN_gvcf_metrics`, `DRAGEN_ploidy_estimation_metrics`, `Picard_CollectHsMetrics`) + `SequencingQC` (run/flowcell/kit). Les valeurs du proband sont inlinées telles quelles (`QC_RAW`/`SEQ_QC`).

## État de la maquette

### Sous-navigation
- **`.seg` `#qcNav`** — bascule entre **« Qualité de séquençage »** (`#secOverview`, niveau échantillon) et **« Couverture des gènes »** (`#secGenes`). Défaut : Qualité de séquençage. Câblage + `renderOverview()` dans `initControls()`.

### Vue d'ensemble (niveau échantillon) — `renderOverview()`
- **Tableau trio** (les 3 membres) : **exactement les 6 indicateurs mis en évidence par clin** (`QualityControlSummary`), dans son ordre — Sexe/ploïdie · Contamination · Couv. moyenne · Région ≥15x · Uniformité (>0,4×moy) · CNV passants. × 3 membres, pastilles colorées + badge de verdict global par colonne. En-tête de colonne = **sample submitter ID (`sid`, forme `DMxxxxxx`)**, pas l'ID séquençage interne (`id`). Seuils repris tels quels de clin (`QualityControlSummary/utils.tsx`). Un **bouton « i »** (`#ovInfoBtn`) ouvre un dialogue (`#ovInfoDlg`, corps `#ovInfoBody` rempli depuis les champs `help` de `HEAD_IND` + `SEX_HELP`) expliquant le seuil de chaque indicateur. *(Le fold-80 avait été ajouté aux indicateurs le 2026-07-10 puis retiré le 2026-07-13 ; il reste en valeur brute dans le panneau de détail « Enrichissement ».)*
- **Deux rapports téléchargeables, à deux niveaux** : (a) **MultiQC** (agrégé, 1 par famille) — lien `.btn` dans l'en-tête de la section « Indicateurs - famille », ouvre `QC_demo_multiqc_report.html` dans un nouvel onglet (comme le `window.open` de clin) ; (b) **Dragen JSON** (1 par échantillon) — bouton « Rapport Dragen (JSON) » dans la rangée des onglets de membre, reconstruit et télécharge le JSON du membre actif (`downloadReport()` / `memberReportJSON()` → `{SamplesQC:[…], SequencingQC}`, nom `${sid}.QC_report.json`).
- **Section « Principales métriques par échantillon » avec sélecteur de membre** (`.ov-memrow` sous le titre, à gauche : **menu déroulant** `#ovMemberSel`, libellés « relation (submitter ID) », variable `OV_MEMBER`) : la section détail reflète le membre choisi. Le tableau d'indicateurs (trio) n'a **pas** de sélecteur — il montre les 3 membres (la sélection n'y a pas de sens). Ordre des panneaux : **Alignement · Couverture · Enrichissement · Sexe · Variants · CNV · Séquençage (run)**. Métriques formatées ; verdicts inline uniquement pour les seuils définis par clin (duplication/fold-80 en valeur brute). Catalogue `OV_PANELS` (+ carte « Séquençage (run) » depuis `SEQ_QC`). Pas de `BAIT_SET` (doublon du kit). **La section « Toutes les métriques (format brut) » a été retirée** (2026-07-13) — le rapport complet s'obtient via le bouton de téléchargement.
- **Modèle de données `memberQC(key)`** : proband = `QC_RAW` réel ; mère/père = copie dégradée par facteur (`MEMBER_DEG`, coverage ↓, contamination ↑, fold-80 ↑, uniformité ↓, duplication ↑, lectures ↓, CNV fixés). Le tableau trio **et** le détail lisent cette même source → valeurs cohérentes entre le haut et le bas. À l'intégration, chaque membre aura son propre `QC_report.json`.
- **Dump brut repliable** (`<details>`) des 3 groupes (capture / mapping / Picard) = reproduction de l'affichage actuel de clin, pour le contraste avant/après.
- Données : proband = réelles (`QC_RAW`) ; mère/père = indicateurs dérivés du proband par facteur pour la démo trio (`trio()`).

### Couverture des gènes — `#secGenes`
- **Sélecteur d'échantillon (trio)** — menu déroulant `<select>` `#sampleSel`, libellés « relation (submitter ID) » (ex. `Cas-index (DM189234)`). Données mère/père = données cas-index dégradées pour la démo.
- **Filtres** : recherche par gène, panel prédéfini, liste custom téléversée.
- **Critères QC** : profondeur minimale (seuil clinique) + complétude requise, avec dialogue d'aide « i ».
- **5 cartes de synthèse cliquables** (Gènes analysés / Conformes / Attention / Échec / Non mappables) — servent aussi de filtre de statut.
- **Tableau principal** avec, de gauche à droite : case à cocher · Actions (SNV / CNV / IGV) · Gène · Taille · Couv. moyenne · %≥Nx (10 seuils) · Statut.
- **Barre au-dessus du tableau** : contrôles de sélection (« N sélectionné(s) », « Sélectionner tous les résultats », « Effacer la sélection ») + bouton **Exporter**.
- **Couv. moyenne** affichée dans l'en-tête de la carte, pondérée par taille des gènes, sur la sélection si présente sinon sur tout le filtre.
- **Modal « Détail par exon »** — accessible en cliquant un nom de gène (souligné en pointillé). Contient : bouton d'aide « i », résumé pondéré du gène, schéma horizontal (pilules arrondies, largeur ∝ taille, couleur = statut à la profondeur active), tableau détaillé (n° · coord. · taille · couv. moyenne · min. couv. · %≥Nx · statut), bouton **Copier les régions sous-couvertes (BED)**.
- **Export CSV filtré** (bouton Exporter).
- **Note de limitation pour le rapport** — bouton « Note de limitation… » dans la barre au-dessus du tableau (à côté d'Exporter). Ouvre un dialogue (`#limitDlg`) avec un texte pré-formaté, éditable, listant les gènes sous les critères actifs groupés par statut (Échec / Attention / Non mappable), + bouton **Copier**. Périmètre = sélection si présente, sinon le filtre courant (recherche/panel/liste) ; le filtre de statut des cartes est volontairement ignoré. Voir `buildLimitationNote()`.

### Journal des changements
- **2026-07-08** — retrait de la colonne « Bases <Nx » du tableau principal.
- **2026-07-09** — session étoffée : ajout du modal drill-down par exon (donnée simulée pour 6 gènes), colonnes case-à-cocher + Actions à gauche, sélection multi-gènes avec couv. moyenne dynamique, remplacement des pastilles échantillon par un dropdown au format Radiant, ajouts UI mineurs, commit du fichier Dragen source.
- **2026-07-10** — deux ajouts : (1) **note de limitation pour le rapport** (`buildLimitationNote()` + `#limitDlg`) : texte pré-formaté, éditable, copiable, groupant les gènes sous les critères par statut ; pourcentage planché à 1 décimale (un gène à 99,96 % ne doit pas s'afficher « 100,0 % » à côté de « partielle »). (2) **section Vue d'ensemble (niveau échantillon)** + sous-navigation `.seg`, alimentée par `47674.QC_report.json` : tableau trio à verdicts colorés (6 indicateurs de clin + fold-80), section détail groupée **avec sélecteur de membre** (Proband/Mère/Père via `memberQC()`), dump brut repliable. Métadonnées du run dédoublonnées (en-tête uniquement). *(Une bannière d'alerte « verdict global au premier coup d'œil » a été prototypée puis retirée à la demande de l'utilisateur — à reprendre plus tard.)* (Un bandeau sample-level fold-80 côté couverture génique avait été prototypé puis retiré le même jour — le vrai fold-80 vit désormais dans la vue d'ensemble, `FOLD_80_BASE_PENALTY` de Picard.)
- **2026-07-13** — affinages de la Vue d'ensemble : panneaux réordonnés (Alignement · Couverture · Enrichissement · Sexe · Variants · CNV) ; en-têtes/titres affichent le **sample submitter ID** (`sid`, `DMxxxxxx`) au lieu de l'ID séquençage ; suppression du sous-titre explicatif (page Notion à venir) ; ajout d'un **dialogue d'aide** (`#ovInfoDlg`) détaillant le seuil de chaque indicateur (champs `help` sur `HEAD_IND` + `SEX_HELP`). Puis **retrait du fold-80 des indicateurs** (retour aux 6 indicateurs de clin) — le fold-80 reste en valeur brute dans le détail « Enrichissement ». Enfin, la ligne de contexte du run (run/flowcell/date/kit) est **remise dans une carte « Séquençage (run) »** de la grille et retirée du titre. Petits ajustements du tableau trio : colonnes membres alignées à gauche (les pastilles de statut forment une colonne nette au lieu de zigzaguer) ; sexe déclaré affiché en clair (« déclaré : masculin/féminin ») au lieu du symbole ♂/♀.
- **2026-07-13 (suite)** — **en-tête de page refait pour reproduire le `PageHeader` de Radiant** (`radiant-portal/frontend/apps/case/src/entity/layout/header.tsx` + `components/base/page/page-header.tsx`) : titre « Cas {id} », badge de type de cas (icône + libellé), badge du code de catalogue d'analyse (infobulle = nom), et à droite priorité + statut ; onglets en dessous. Le fil d'Ariane factice est retiré (Radiant n'en a pas ici). **Le type de cas différencie déjà famille vs solo** : `germline_family` → « Germinal familial » (cas actuel), `germline` → « Germinal » (solo), `somatic` → « Somatique » (icône biohazard). Libellés/couleurs des badges statut (`StatusBadge`) et priorité (`PriorityIndicator`) repris de `common/fr.json`. Valeurs du header (code EXM, statut « En cours », priorité « Routine ») = placeholders de démo.
- **2026-07-13 (suite)** — titres de la vue d'ensemble : h2 → « Indicateurs - famille », titre section détail → « Principales métriques par échantillon ». Onglets de membre déplacés **sous** ce titre (à gauche), libellés « relation (submitter ID) ». Ajout d'un bouton **« Télécharger le rapport »** (JSON reconstruit par membre). Retrait de la section « Toutes les métriques (format brut) ». Puis **deux rapports distincts** : **MultiQC** (1 par famille, lien vers `QC_demo_multiqc_report.html` dans l'en-tête « Indicateurs - famille », ouvert en nouvel onglet) et **Dragen JSON** (1 par échantillon, bouton « Rapport Dragen (JSON) »). Titres « Indicateurs - famille » et « Principales métriques par échantillon » alignés à la même taille (18px). Remplacement du mot **« proband » → « cas-index »** dans tous les libellés visibles. **Harmonisation du choix d'échantillon** : le sélecteur du détail passe de pastilles à **menu déroulant** identique à celui de la couverture des gènes ; format « relation (DMxxxxxx) », sans statut affecté ; per-section, non synchronisé (voir note « Choix d'échantillon »). Onglet de sous-navigation « Vue d'ensemble (échantillon) » renommé **« Qualité de séquençage »**.

## Notes techniques

### Données simulées pour le drill-down
Les données par exon sont inlinées dans `qc_gene_coverage.html` (constante `EXON_DATA`) pour 6 gènes en tête du tableau alphabétique : **AANAT, ABRAXAS2, ACKR4, ACTR3, AKR1B15, AKR1C2**.

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
Les seuils de verdict des indicateurs de tête sont **repris tels quels de clin** (`clin-portal-ui/src/views/Prescriptions/Entity/QualityControlSummary/utils.tsx`) : sexe via couv. chrY/chrX vs sexe déclaré ; contamination > 2 % (orange) / > 5 % (rouge) ; couv. moyenne < 100x (rouge) ; région ≥15x < 95 % (rouge) ; uniformité (>0,4×moy) < 93,91 % (orange) ; CNV > 504 (orange). Principe : ne mettre en évidence que ces indicateurs-là (fixé avec l'utilisateur le 2026-07-10). Le fold-80 avait été ajouté puis retiré (2026-07-13) ; comme la duplication, il reste en détail sans verdict. Le trio mère/père est **dérivé du proband** par `memberQC(key)` (facteurs `MEMBER_DEG`) uniquement pour la démo, de sorte que le tableau trio et le détail par membre restent cohérents ; à l'intégration, chaque membre a son propre `QC_report.json`.

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
| Verdict sample-level global (moyenne, % à 20x, uniformité, contamination, sexe) | **En place** — Vue d'ensemble : tableau trio à verdicts + fold-80 réel (Picard) + panneaux de détail |
| Voir les variants (SNV/CNV) associés à chaque gène | En place (liens vers onglet Variants + IGV, données stub) |
| Comparaison trio en une seule vue | **Partiel** — le tableau trio de la Vue d'ensemble compare les 3 membres au niveau échantillon ; pas encore de comparaison trio au niveau gène/exon |
| Note de limitation pré-formatée pour le rapport final | **En place** — bouton « Note de limitation… » → texte éditable/copiable groupé par statut |
| Annotation des gènes structurellement difficiles (pseudogènes, régions dupliquées) | Absent |
| Aide à la décision (Sanger, retest, méthode alternative) | Absent (hors scope court terme) |

## Prochaines étapes envisagées

- **Brancher les vraies données** : remplacer `EXON_DATA` simulé par un lookup depuis le fichier Dragen `.bed` (avec le mapping gène→exons annexe), remplacer `mockCount()` par l'API variants Radiant, brancher les liens IGV/SNV/CNV vers de vraies navigations.
- **Améliorer la Vue d'ensemble puis clin** — c'est l'objet de la section : itérer sur la présentation (regroupements, seuils, ce qu'on met en avant vs en repli) pour ensuite améliorer la section `General` de clin, aujourd'hui un dump brut. Pistes : brancher les vraies données trio (chaque membre a son propre `QC_report.json`), déplacer les seuils « proposés » vers des seuils validés labo, lien depuis « Région ≥15x » vers la couverture génique (comme clin le fait déjà).
- **Autres sections QC** — d'autres modules (qualité base par base, index de contamination inter-échantillons `SequencingQC.index_contamination_stats`, etc.) pourront s'ajouter.
- **Intégration dans `~/src/radiant-portal`** comme onglet de la page Case (et report des améliorations dans `~/src/clin-portal-ui`).
