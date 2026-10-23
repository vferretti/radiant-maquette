# `cnv/` — Visualisation des CNV (copy ratio, BAF, ROH)

Section **en phase d'analyse** : aucune maquette HTML encore. Point de départ : la figure
`<échantillon>.combined_copyratio_baf_roh.png` produite par le CQGC (pipeline DRAGEN
WES_germinal) et déjà disponible dans Radiant et Qlin. Objectif : la comprendre, identifier
ses sources de données, puis proposer une version **interactive** intégrable comme section
du cas. Les conventions transversales (HTML autonome, vérif headless, terminologie,
partage) sont dans le `CLAUDE.md` **racine**.

## Fichiers de données — NON versionnés

Les fichiers d'échantillon (`50857.*`, `50877.*` : PNG, bigWig, VCF, `.tgz`…) sont
**récupérés hors git** (volumineux, données patient). Ne jamais les committer. Échantillons
vus : **50877** (PNG seul) et **50857** (PNG + données ; c'est sur lui qu'on a tout vérifié).
Le nom de l'échantillon n'a pas d'importance : on raisonne sur les **types de fichiers**.

`<éch>.extra.tgz` est une archive tar de 57 fichiers DRAGEN avec un `ReadMe.txt` du CQGC
qui décrit chaque fichier (`tar tzf` pour lister, `tar xzOf … ReadMe.txt` pour lire).
Extraire dans un répertoire temporaire, pas dans `cnv/`.

## La figure — trois panneaux alignés sur le même axe génomique

Chromosomes chr1→chrY de gauche à droite ; gris/vert alterné = simple repère par chromosome.

1. **Copy ratios with CNV calls**
   - Petits points = signal normalisé **par bin** (~60 pb, dans les cibles), affiché en
     **linéaire** (1 = 2 copies, 0.5 = délétion hétérozygote, 0 = homozygote, 1.5 = 3 copies).
   - Gros points = appels CNV, hauteur = `SM` (ratio moyen du segment) ; **rouge = perte,
     bleu = gain** ; **creux / pâles = appels non-PASS**.
2. **B-Allelic Frequency** — un point par SNV PASS ; 0/1 = homozygote, 0.5 = hétérozygote.
   Délétion → bande 0.5 disparaît ; duplication → bandes 0.33/0.67.
3. **Regions of Homozygosity** — un point par région (la taille réelle n'est pas montrée).

**L'alignement est essentiel** : c'est le croisement à la même position qui permet de
conclure (délétion vs homozygotie sans perte — consanguinité ou UPD isodisomique — vs
artéfact). Toute maquette doit garder un axe X partagé et un **zoom synchronisé**.

Limites de la figure actuelle (= opportunités pour la maquette) : taille des CNV et des
ROH invisible (1 exon = 5 Mb), aucun gène, pas de distinction bruit/pertinent, statique,
pas de trio (parents).

## Sources de données — vérifiées sur 50857 (DRAGEN 4.4.4)

| Élément de la figure | Fichier | Détails vérifiés |
|---|---|---|
| Petits points du copy ratio | `tn.tsv.gz` / `tn.bw` | 389 772 bins, valeurs **log2** (figure = 2^x) ; colonnes `contig start stop name <éch> improper_pairs` ; en-tête `#sex = FEMALE` ; pas de chrY |
| Gros points (appels CNV) | `cnv.vcf.gz` | 92 appels (70 PASS) ; `FORMAT` `GT:SM:CN:BC:PE:LR` ; filtres `cnvQual`, `dinucQual`, `cnvLikelihoodRatio`, `cnvBinSupportRatio`, `cnvCopyRatio` ; ID `DRAGEN:LOSS:chr1:65509-70017` |
| Idem en TSV, + segments neutres | `seg.called.merged` | colonnes `Num_Targets Segment_Mean Qual Filter Copy_Number…` |
| Segmentation complète | `seg.bw` | 194 intervalles = 107 segments neutres (~1.0) + 87 identiques aux appels du VCF (même `SM`) |
| BAF | `hard-filtered.baf.bw` | 330 914 positions de 1 pb ; 0 et 1 en proportions égales (allèle B ≠ ALT, convention Illumina) ; contient des contigs secondaires (`chrUn_`, `_random`, `HLA-…`, chrM) à **filtrer** |
| ROH | `roh.bed` | `chrom start end score nb_homozygotes nb_hétérozygotes` ; 13 régions = 13 points de la figure |

Autres fichiers utiles de l'archive : `cnv.excluded_intervals.bed.gz` (régions ignorées —
à montrer, sinon « pas d'appel » se lit « pas de CNV »), `cnv_metrics.csv`,
`ploidy_estimation_metrics.csv`, `improper.pairs.bw`, `target.counts*`, `cnv.gff3`,
`cnv.igv_session.xml`, `sv.vcf.gz` (SV Manta, complémentaire), `HyperExomeV2_combined_targets.bed`.

Observations sur 50857 : appels très courts (médiane 240 pb, 1–2 bins ; 3 > 100 kb) →
surtout bruit d'exome / CNV polymorphes ; amas gain/perte alterné chrX ~135,7–135,9 Mb
(duplications segmentaires probables) ; plus forte ROH dans la région HLA (chr6 ~29,6 Mb).

## ⚠️ Ploïdie « XXX » — ne pas afficher comme verdict

`ploidy_estimation_metrics.csv` de 50857 conclut **XXX** (X/autosomes = 1.30), mais c'est
un **artéfact** de l'estimation sur couverture brute d'exome : les rapports autosomiques
varient de 0.78 à **1.92 (chr19)**. Contre-preuves : `tn` chrX médiane 1.015 (XXX ≈ 1.5),
en-tête `#sex = FEMALE`, BAF chrX centré sur 0.50 comme les autosomes (XXX → 0.33/0.67).
Dans une maquette : soit ne pas montrer cette valeur, soit l'accompagner du BAF et du ratio
normalisé de chrX. Point à remonter au CQGC.

## Outillage

Pas de `pip` ni `pyBigWig` sur la machine d'origine : un **lecteur bigWig en Python pur**
(struct + zlib : en-tête, arbre B+ des chromosomes, R-tree, sections bedGraph type 1) a
suffi. À réécrire au besoin (~50 lignes) ou installer `pyBigWig`.

## Prochaines étapes envisagées

- Regarder ce que Radiant / clin affichent déjà pour les CNV (liste, filtres, IGV).
- Maquette interactive : 3 pistes empilées, axe partagé, zoom synchronisé, vue génome
  entier + vue chromosome ; clic sur un appel → région + détail (gènes, taille, qualité,
  filtre) ; ROH en **segments** ; régions exclues ; pour un trio, BAF des parents empilés.
