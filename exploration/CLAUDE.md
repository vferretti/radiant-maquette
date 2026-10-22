# `exploration/` — Exploration des variants

Maquette d'une **nouvelle section de premier niveau** de Radiant : un formulaire de recherche
qui permet d'atteindre un variant **en dehors de tout cas**. Fichier de travail :
`exploration_radiant.html`. Les conventions transversales (HTML autonome, vérif headless,
terminologie, partage) sont dans le `CLAUDE.md` **racine**.

## Le problème

Dans Radiant aujourd'hui, **on ne peut atteindre un variant que par un cas**. Tous les
endpoints d'occurrences sont portés par un triplet de cas :

```
/{tenant}/occurrences/germline/snv/{case_id}/{seq_id}/{task_id}/list
```

La page entité du variant existe pourtant déjà et vit hors du cas
(`/variants/entity/:locusId`, `frontend/apps/variant/`) — mais **rien n'y mène** sinon un clic
depuis le tableau de variants d'un cas. Le généticien qui veut simplement savoir « qu'est-ce
qu'on a déjà vu à ce locus ? » doit d'abord trouver un cas qui le porte.

Cette section est la porte d'entrée manquante.

## Nom de la section

« Exploration » est retenu **faute de mieux**, mais il ne sort pas de nulle part : le
vocabulaire du produit l'emploie déjà. `frontend/apps/case/src/exploration/` désigne la vue
liste des cas, et les traductions portent déjà
`main_navbar.links.data_exploration` = « Exploration des données » ainsi qu'une mention de
« pages d'exploration des variants » (`analysis.set_operations.empty.description`).

D'où le choix de la maquette : **« Exploration » dans la barre de navigation**, **« Exploration
des variants » en titre de page**. Les autres candidats sont `main_navbar.links.variants`
= « Variants » (plus court, mais ambigu avec l'onglet Variants d'un cas) et « Exploration des
données » (plus large que ce qu'on livre). À trancher.

## Le formulaire — trois contrôles, rien d'autre

```
Type de variant      Origine
[ SNV ][ CNV ]       [ Germinal ][ Somatique ]

Variant ou gène
[🔍  1-55051215-G-GA · chr10:g.99235506G>A · PCSK9              ✕ ]
Exemples :  1-55051215-G-GA   10-99235506-G-A   M-8602-T-C   PCSK9
```

- **Deux segments** (`Type de variant`, `Origine`) : ce sont deux banques de données
  différentes, pas deux filtres. Le choix précède la recherche, il ne la raffine pas.
  Le type change le placeholder, les exemples, et ce que le champ accepte (voir « CNV »).
- **Un seul champ de recherche**, pas deux. Le clinicien ne devrait pas avoir à déclarer s'il
  cherche un variant ou un gène : ce que la chaîne saisie est se **déduit** de sa forme, comme
  dans la boîte unique de gnomAD. C'est un geste de moins et une décision de moins.
- **Le champ *est* la recherche** — même parti pris que `prescription/` : curseur déjà dedans,
  on tape, `↵`. `↑` `↓` parcourent, `↵` choisit, `esc` referme ; les options réagissent au
  `mousedown` (sinon le `blur` referme la liste avant le clic).
- **Ligne d'exemples** cliquables (propre à chaque type : `EXAMPLES.snv` / `EXAMPLES.cnv`) sous le champ. C'est le seul texte ajouté à l'écran, et il
  est là parce que la syntaxe du locus n'est devinable par personne — gnomAD affiche la même
  chose sur sa page de recherche. Ce ne sont pas des explications, ce sont des amorces.

### Ce que le champ accepte

Trois formes, testées dans cet ordre (`parseQuery`) :

| Forme | Exemple | Sortie |
|---|---|---|
| **HGVSg** | `chr10:g.99235506G>A` | locus |
| **Locus gnomAD** | `1-55051215-G-GA`, `chr1:55051215:G:GA`, `M-8602-T-C` | locus |
| **Symbole de gène** | `PCSK9` | gène |

- Le préfixe `chr` est facultatif, les séparateurs `-` `:` `_` sont interchangeables,
  chromosomes 1–22, X, Y, M/MT (`MT` ramené à `M`).
- Tout est **normalisé vers `chr-pos-ref-alt`**, c'est-à-dire le format de la colonne `locus`
  de StarRocks (`snv__variant.locus`) — vérifié sur le jeu de test Cypress :
  `locus = '10-99235506-G-A'` pour `hgvsg = 'chr10:g.99235506G>A'`.
- **HGVSg est accepté parce que c'est ce que le titre de la page entité affiche** : un
  utilisateur qui recopie un variant depuis Radiant recolle un `hgvsg`, pas un locus.

En type **SNV**, une chaîne de forme CNV n'est pas rejetée en silence : la liste déroulante
affiche « Ceci est un CNV. Chercher parmi les CNV » (bascule de type) — et inversement.

### Ce qu'il n'accepte pas encore

`rs72840396` (dbSNP), un identifiant de transcrit, une région (`19-11078371-11144910`), un
locus mitochondrial autrement que sous forme de SNV. Volontairement hors périmètre — voir
« Prochaines étapes ».

## Les deux issues de la recherche

1. **Un locus → la page entité, directement.** Pas d'écran de résultat intermédiaire : un
   locus identifie un variant et un seul.
   - S'il n'existe pas dans la banque choisie, on retombe sur l'état vide **« Variante
     introuvable »** (le message réel de Radiant, `variant_entity.not_found`), assorti d'un
     bouton qui **rejoue la recherche dans l'autre banque** — c'est la méprise la plus probable.
2. **Un gène → un tableau de variants**, avec un retour « ‹ Exploration » et, depuis une ligne,
   le passage à la page entité (qui revient alors « ‹ PCSK9 »).

## CNV

Deux formes en type CNV : **un CNV** ou **un symbole de gène**.

| Forme | Exemples | Normalisé |
|---|---|---|
| **CNV** | `GAIN:chr16:29580020-30180000`, `LOSS-22-18912231-21465672` | `GAIN:chr16:29580020-30180000` |

- `GAIN` ou `LOSS` (casse libre), `chr` facultatif, séparateurs `-` `:` `_` libres, virgules
  tolérées dans les positions, début/fin remis dans l'ordre. Affichage au format du `name` de
  Radiant (`GAIN:chrN:début-fin`) ; clé interne `GAIN-N-début-fin` (`cnvKey`).
- **Un CNV n'ouvre jamais une page entité** (il n'en existe pas) : c'est une **région**, et le
  résultat est toujours une **liste** — les CNV du même type qui la chevauchent, le CNV
  identique (s'il existe) en tête avec la pastille « identique », puis par % de chevauchement.
  Aucun chevauchement → état vide « Aucun CNV trouvé » + bouton « Chercher dans la banque … ».
- **Un gène** → les CNV (des deux types) qui le touchent.
- Colonnes (libellés `variant.headers.*`, ordre inspiré de `germline-cnv-occurrence-table-settings.tsx`) :
  Variant · Type · Cytobande · Chr · Début · Fin · Longueur · **% CNV** (recherche par région
  seulement : part du CNV chevauchée par la région saisie) · Gènes · # Gènes · gnomAD · Fréq. G /
  Fréq. TN · Interpr. Exclus, car propres à une occurrence : CN, GT, Filtre, Qual., PE, # SNVs,
  Exomiser.
- Le nom du CNV renvoie à **Franklin** (`…/variant/sv/chrN-début-fin-DUP|DEL-HG38`), exactement
  comme `CNVNameCell` de Radiant.

## Le tableau — colonnes retenues

Les colonnes sont à arbitrer, mais **le principe de sélection, lui, n'est pas négociable :
c'est un tableau de *variants*, pas d'*occurrences***. Tout ce qui n'a de sens qu'à l'intérieur
d'un cas est donc exclu — zygosité, qualité de génotypage (QG), ratio de profondeur allélique,
génotype, et **le score Exomiser** (calculé à partir des phénotypes d'un patient : hors cas, il
ne veut rien dire). C'est ce qui distingue cette vue de l'onglet Variants d'un cas, et c'est
aussi pourquoi elle ne peut pas réutiliser le même endpoint.

Libellés repris tels quels de `variant.headers.*` (`frontend/translations/common/fr.json`) :

| Germinal | Somatique |
|---|---|
| Variant · Type · Gène · AA · Conséquence · MANE · dbSNP · **OMIM** · ClinVar · gnomAD · **Fréq. G** · Interpr. | Variant · Type · Gène · AA · Conséquence · MANE · dbSNP · **Hotspot** · ClinVar · gnomAD · **Fréq. TN** · Interpr. |

Deux colonnes changent avec l'origine, et c'est voulu : le segment « Origine » doit avoir une
conséquence visible, sans quoi on se demande pourquoi on l'a réglé.

- **Conséquence** porte l'`ImpactIndicator` de Radiant : triangle rouge `HIGH`, losange ambre
  `MODERATE`, triangle vert `LOW`, rond gris `MODIFIER`. Les libellés de conséquence restent en
  anglais (`Missense`, `Stop Gained`…) : le fichier FR les laisse ainsi.
- **Interpr.** = les interprétations du réseau pour ce variant (pastille + compte). C'est la
  colonne qui justifie à elle seule la section : « ce variant, l'a-t-on déjà classé ? ».
- Les pastilles de classification reprennent les couleurs de `ClassificationBadge`
  (P rouge, LP orange, VUS jaune, LB lime, B vert, O rouge, LO violet).

## La page entité

Elle **existe déjà** dans Radiant ; la maquette en donne une reproduction allégée pour que le
parcours soit démontrable de bout en bout, pas pour la remettre en question :

- en-tête `HeaderNavigation` — titre = `hgvsg`, badges `GRCh38` (= `assembly_version`) et
  `Germinal` / `Somatique` ;
- la barre d'onglets réelle : Résumé · Fréquences · Preuves et conditions · Transcrits · Cas ;
- l'onglet **Résumé** avec ses six cartes (`apps/variant/src/entity/overview/`) : conséquence
  la plus délétère, Interprétation, Classifications, Scores de prédiction, Conditions associées
  (OMIM), Références externes.

Les onglets autres que Résumé ne sont pas maquettés.

## Ce qu'il faudra construire côté produit

Constats tirés du code, à valider avec l'équipe :

1. **La route de l'entité prend un identifiant numérique, pas un locus.**
   `/variants/entity/:locusId` attend le `locus_id` de StarRocks (un hash `bigint`, p. ex.
   `-6314429946999603200`), alors que la recherche produit `10-99235506-G-A`. Deux options :
   ajouter une résolution `locus → locus_id`, ou **faire accepter le locus à la route**.
   *Recommandé : la seconde.* Une URL en `/variants/entity/10-99235506-G-A` est lisible,
   collable dans un courriel et devinable — ce que le hash n'est pas.
2. **Il n'existe aucun endpoint de recherche de variants hors cas.** Les endpoints
   `/variants/germline/{locus_id}/…` servent une page entité déjà ouverte ; les endpoints
   d'occurrences sont scopés au cas. La branche « gène » a donc besoin d'un nouvel endpoint de
   liste au niveau variant (les tables `snv__variant` et
   `snv__consequence_filter_partitioned` portent déjà les colonnes voulues).
3. **La page entité est germinale uniquement.** `getGermlineVariantHeader`, et toutes les
   routes en `/variants/germline/…`. La maquette montre le segment « Somatique » parce que la
   distinction est réelle côté données (`somatic__snv__occurrence`), mais **il n'existe pas de
   page entité somatique** : c'est un chantier à part entière, pas un branchement.
4. **La branche « gène » peut réutiliser l'existant** : `GET /{tenant}/genes/autocomplete`
   (préfixe + limite) alimente exactement la liste déroulante de la maquette.
5. **CNV : il n'y a pas de table « variant »**, seulement `cnv__occurrence`. Chaque appel a
   ses propres bornes : la maquette agrège les appels **strictement identiques** (type, chr,
   début, fin) et compte les patients, mais côté produit il faudra décider comment regrouper
   (identité exacte ? chevauchement réciproque ≥ x % ?) — c'est la vraie question ouverte du CNV.
6. **Place dans la navigation** : une entrée de plus dans `protected-navbar.tsx`, à côté de
   « Cas » et « Fichiers », et une route dans `portals/radiant/app/routes.ts`.

## Données de démonstration

Inlinées en JS (`GENES`, `VARIANTS`, `CNVS`), rien n'est branché.

- **`10-99235506-G-A` (HPSE2) reprend les valeurs réelles** du jeu de test Cypress de Radiant
  (`cypress/pom/shared/Data.ts` → `variantGermline`) : locus, hgvsg, rs72840396, conséquence,
  transcrit `ENST00000370552`, `c.290+7C>T`, gnomAD `1.66e-3`, patients `2 (1.43e-1)`, ClinVar
  `784210`, OMIM 236730. C'est le variant à utiliser pour toute vérification.
- **CNV** (`CNVS`) : germinal — 22q11.2, 16p11.2 (GAIN et LOSS), DMD (4), MECP2, PCSK9 ;
  somatique — ERBB2, EGFR, CDKN2A (2), TP53, PTEN. Coordonnées GRCh38 plausibles, inventées.
- **Germinal** : `PCSK9` (7 variants, dont le `1-55051215-G-GA` de l'énoncé) et `HPSE2` (4).
- **Somatique** : `TP53` (6) et `KRAS` (4) — coordonnées GRCh38 et dbSNP réels pour les points
  chauds (R273H, R248Q, R175H, G12D…), le reste est inventé.
- Les autres gènes du catalogue d'autocomplétion (BRCA1, CFTR…) **n'ont aucun variant** (DMD n'a que des CNV) :
  c'est ce qui permet de montrer l'état vide du tableau.

## Vérification

```sh
google-chrome --headless=new --disable-gpu --window-size=1500,760 \
  --screenshot=out.png "file://$PWD/exploration_radiant.html"
```

Pour photographier un état interactif, injecter un appel à la place du `$('q').focus();` final,
sur une copie temporaire :

```sh
sed "s|^\$('q').focus();\$|\$('q').value='PCSK9';submit();|" exploration_radiant.html > /tmp/t.html
```

États utiles : `$('q').value='PC';refreshDrop();` (liste déroulante) ·
`$('q').value='PCSK9';submit();` (tableau) ·
`openEntityByLocus('1-55052746-C-T')` (page entité) ·
`setOrigin('somatic');$('q').value='1-55051215-G-GA';submit();` (variante introuvable) ·
`setOrigin('somatic');$('q').value='BRCA1';submit();` (gène sans variant) ·
`setType('cnv');$('q').value='LOSS:chr22:18912231-21465672';submit();` (CNV chevauchants) ·
`setType('cnv');$('q').value='DMD';submit();` (CNV d'un gène) ·
`$('q').value='LOSS-1-100-200';$('q').focus();refreshDrop();` (mauvais type → bascule).

## Prochaines étapes

- **CNV** : règle de regroupement des appels (voir point 5 ci-dessus), recherche par région
  **sans type** (`1-55039447-55064852` → GAIN et LOSS), et une éventuelle page entité CNV.
- **rsID** (`rs72840396`) : troisième forme à reconnaître, la plus demandée après le locus.
- **Recherche par région** et par **transcrit** (`ENST00000302118`), comme gnomAD.
- **Colonnes du tableau** : à arbitrer avec les généticiens (la liste ci-dessus est une
  proposition), ainsi que le tri par défaut — aujourd'hui l'ordre est celui des coordonnées.
- **Assemblage** : la maquette affiche `GRCh38` en dur ; le champ existe
  (`VariantHeader.assembly_version`). Prévoir le cas d'un déploiement en GRCh37.
