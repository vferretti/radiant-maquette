# Radiant — Maquette QC couverture des gènes

## Contexte

Ce repo contient une **maquette HTML statique** pour une nouvelle section QC à intégrer dans l'application Radiant (`~/src/radiant-portal`). L'intention est de l'ajouter comme **onglet dans la page « Case »**, à côté des onglets existants (Détails, Variants, Fichiers).

Radiant est utilisé par des généticiens du CHU Sainte-Justine pour établir des diagnostics moléculaires (WES/WGS trios germinaux, panels ciblés).

## Fichiers

- `qc_gene_coverage.html` — maquette principale (autonome, données inlinées). C'est le fichier de travail.
- `build_mockup.py` — script qui a généré la maquette à partir de `test_gene_coverage.csv`.
- `test_gene_coverage.csv` — données de couverture par gène qui ont servi à alimenter la maquette.
- `QC_demo_multiqc_report.html` — rapport MultiQC de référence (inspiration/comparaison).

## État de la maquette

### Sections déjà présentes
- Sélecteur d'échantillon (trio : proband / mère / père — données mère/père dégradées pour la démo).
- Filtres : recherche par gène, panel prédéfini, liste custom téléversée.
- Critères QC : profondeur minimale (seuil clinique) + complétude requise.
- 5 cartes de synthèse cliquables (Gènes analysés / Conformes / Attention / Échec / Non mappables) — servent aussi de filtre de statut.
- Tableau paginé : Gène, Taille, Couv. moyenne, colonnes `%≥Nx` pour plusieurs seuils, Statut.
- Export CSV filtré, dialogue d'aide sur les critères.

### Modifications récentes
- **2026-07-08** : retrait de la colonne « Bases <Nx » (dernière colonne du tableau) et de la variable `t` devenue inutilisée.

## Analyse clinique (généticien / diagnostic moléculaire)

Résumé des questions qu'un généticien se pose devant ce tableau et de la couverture actuelle de l'interface.

| Question clinique | Support actuel |
|---|---|
| Les gènes du panel/phénotype sont-ils couverts ? | **Très bon** — panel + liste custom + recherche |
| Alignement avec les seuils cliniques du labo | **Très bon** — sélecteurs profondeur + complétude |
| Verdict sample-level global (moyenne, % à 20x, uniformité) | Faible — à ajouter |
| Granularité intra-gène (couverture par exon/région) | **Absent — priorité 1** |
| Comparaison trio en une seule vue | Faible (obligé de cliquer sur chaque échantillon) |
| Note de limitation pré-formatée pour le rapport final | **Absent — priorité 2** |
| Annotation des gènes structurellement difficiles (pseudogènes, régions dupliquées) | Absent |
| Aide à la décision (Sanger, retest, méthode alternative) | Absent (hors scope court terme) |

### Pourquoi ces priorités

1. **Drill-down par exon** — un gène marqué « Attention » à 95 % à 20x peut cacher un exon entièrement à 0. Sans cette vue, on peut manquer un variant candidat dans une région non couverte tout en pensant que le gène est « OK ».
2. **Bloc limitations pour le rapport** — les cliniciens doivent aujourd'hui composer à la main la note de limitations de couverture. Un bouton « copier la note » leur ferait gagner un temps significatif.
3. **Bandeau sample-level** — quelques chiffres agrégés en haut (couverture moyenne, % du panel à la profondeur cible, fold-80) permettraient au clinicien d'établir sa confiance dans le sample en 3 secondes.

## Prochaines étapes envisagées

- D'autres sections QC seront ajoutées à la maquette (au-delà de la couverture par gène).
- Intégration éventuelle dans `~/src/radiant-portal` comme onglet de la page Case.
