# Radiant — Maquette QC couverture des gènes

## Contexte

Ce repo contient une **maquette HTML statique** pour une nouvelle section QC à intégrer dans l'application Radiant (`~/src/radiant-portal`). L'intention est de l'ajouter comme **onglet dans la page « Case »**, à côté des onglets existants (Détails, Variants, Fichiers).

Radiant est utilisé par des généticiens du CHU Sainte-Justine pour établir des diagnostics moléculaires (WES/WGS trios germinaux, panels ciblés).

## Fichiers

- `qc_gene_coverage.html` — maquette principale (autonome, données inlinées). C'est le fichier de travail.
- `build_mockup.py` — script qui a généré la première version de la maquette à partir de `test_gene_coverage.csv`. N'a pas été re-exécuté depuis l'ajout du modal exon et des autres features — le HTML est édité directement.
- `test_gene_coverage.csv` — données de couverture par gène qui ont servi à alimenter la maquette initiale.
- `QC_demo_multiqc_report.html` — rapport MultiQC de référence (inspiration/comparaison).
- `41267.qc-coverage-region-2_cov_report.bed` — rapport Dragen pour l'échantillon 41267 : **la source cible** pour brancher les vraies données par exon du modal drill-down (voir « Notes techniques » plus bas).

## État de la maquette

### Sections en place
- **Sélecteur d'échantillon (trio)** — dropdown `<select>` reproduisant le format du composant Radiant `SequencingVariantFiltersSelectItem` (relation · ID Séq. · Échantillon · Statut affecté). Données mère/père = données proband dégradées pour la démo.
- **Filtres** : recherche par gène, panel prédéfini, liste custom téléversée.
- **Critères QC** : profondeur minimale (seuil clinique) + complétude requise, avec dialogue d'aide « i ».
- **5 cartes de synthèse cliquables** (Gènes analysés / Conformes / Attention / Échec / Non mappables) — servent aussi de filtre de statut.
- **Tableau principal** avec, de gauche à droite : case à cocher · Actions (SNV / CNV / IGV) · Gène · Taille · Couv. moyenne · %≥Nx (10 seuils) · Statut.
- **Barre au-dessus du tableau** : contrôles de sélection (« N sélectionné(s) », « Sélectionner tous les résultats », « Effacer la sélection ») + bouton **Exporter**.
- **Couv. moyenne** affichée dans l'en-tête de la carte, pondérée par taille des gènes, sur la sélection si présente sinon sur tout le filtre.
- **Modal « Détail par exon »** — accessible en cliquant un nom de gène (souligné en pointillé). Contient : bouton d'aide « i », résumé pondéré du gène, schéma horizontal (pilules arrondies, largeur ∝ taille, couleur = statut à la profondeur active), tableau détaillé (n° · coord. · taille · couv. moyenne · min. couv. · %≥Nx · statut), bouton **Copier les régions sous-couvertes (BED)**.
- **Export CSV filtré** (bouton Exporter).

### Journal des changements
- **2026-07-08** — retrait de la colonne « Bases <Nx » du tableau principal.
- **2026-07-09** — session étoffée : ajout du modal drill-down par exon (donnée simulée pour 6 gènes), colonnes case-à-cocher + Actions à gauche, sélection multi-gènes avec couv. moyenne dynamique, remplacement des pastilles échantillon par un dropdown au format Radiant, ajouts UI mineurs, commit du fichier Dragen source.

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

### Compteurs SNV/CNV
`mockCount(gene, kind)` produit un compteur déterministe par hash du nom de gène. Distribution SNV : ~40 % à 0, la plupart entre 1 et 8, quelques-uns >10. CNV : ~85 % à 0. À remplacer par un lookup vers l'API variants de Radiant.

### Format du sélecteur d'échantillon
Le format actuel `Proband (ID Séq. 12345) · Échantillon SP-1008-01 · Affecté` est une approximation du composant Radiant. Le vrai `SequencingVariantFiltersSelectItem` (dans `~/src/radiant-portal/frontend/apps/case/src/entity/variants/filters/sequencing-experiment-variant-filters.tsx`) affiche 2 lignes par option + badges séparés à côté (icône `FlaskConical` + `AffectedStatusBadge`). Un `<select>` natif ne peut pas rendre ça — à l'intégration, réutiliser directement ce composant.

## Analyse clinique (généticien / diagnostic moléculaire)

Résumé des questions qu'un généticien se pose devant ce tableau et de la couverture actuelle de l'interface.

| Question clinique | Support actuel |
|---|---|
| Les gènes du panel/phénotype sont-ils couverts ? | **Très bon** — panel + liste custom + recherche |
| Alignement avec les seuils cliniques du labo | **Très bon** — sélecteurs profondeur + complétude |
| Granularité intra-gène (couverture par exon/région) | **Très bon** — modal drill-down avec schéma + tableau + export BED |
| Verdict sample-level global (moyenne, % à 20x, uniformité) | Partiel — moyenne globale affichée mais pas d'uniformité (fold-80) |
| Voir les variants (SNV/CNV) associés à chaque gène | En place (liens vers onglet Variants + IGV, données stub) |
| Comparaison trio en une seule vue | Faible (obligé de basculer via le dropdown) |
| Note de limitation pré-formatée pour le rapport final | **Absent — priorité restante** |
| Annotation des gènes structurellement difficiles (pseudogènes, régions dupliquées) | Absent |
| Aide à la décision (Sanger, retest, méthode alternative) | Absent (hors scope court terme) |

## Prochaines étapes envisagées

- **Brancher les vraies données** : remplacer `EXON_DATA` simulé par un lookup depuis le fichier Dragen `.bed` (avec le mapping gène→exons annexe), remplacer `mockCount()` par l'API variants Radiant, brancher les liens IGV/SNV/CNV vers de vraies navigations.
- **Bloc limitations pour le rapport** — bouton « copier la note de limitation » qui produit un texte pré-formatté (« Les gènes suivants ont une couverture inférieure aux critères… »).
- **Bandeau sample-level** — ajouter fold-80 et % du panel à la profondeur cible dans l'en-tête.
- **Autres sections QC** — d'autres modules (mapping, qualité base par base, contamination, sexe génétique, etc.) viendront s'ajouter comme sections dans ce même onglet.
- **Intégration dans `~/src/radiant-portal`** comme onglet de la page Case.
