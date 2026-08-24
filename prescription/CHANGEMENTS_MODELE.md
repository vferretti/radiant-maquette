# Changements de modèle induits par la maquette « Création de cas »

**Le modèle de référence est désormais la page Notion « Radiant Prescription » §5**
(`app.notion.com/p/ferlab/Radiant-Prescription-3c6b0fcecb3d804a8290d98ac1646eae`), qui acte
les changements ci-dessous. Ce fichier garde la trace du **pourquoi** et des points restés
ouverts.

Schéma actuel : `~/src/radiant-portal/backend/scripts/init-sql/migrations/000001_init.up.sql`.

## 0. Ce que le modèle Notion a tranché

| | Ce que j'avais proposé | Ce que Notion acte |
|---|---|---|
| `cases.primary_condition` | → `analysis_catalog` | ✅ idem |
| `cases.condition_code_system` | → `analysis_catalog` | ✅ idem |
| `cases.case_type_code` | → `analysis_catalog` | ✅ **et renommée `analysis_type_code`** → `analysis_type(code)` |
| `cases.case_category_code` | question ouverte | ❌ **reste sur `cases`** — un cas prénatal peut basculer |
| `analysis_catalog.panel_id` | conservée | ❌ **supprimée** → nouvelle table `analysis_has_panels` (n-n) |
| HPO par défaut | pas envisagé | ✅ nouvelle table **`default_phenotype`** (`analysis_catalog_id`, `hpo_id`) |

Les `ValueSet-<code>-default-hpo.json` de `clin-fhir` sont la source de `default_phenotype`
(présents pour `conco`, `eidi`, `fean`, `genor`, `mitn`, `mmg`, `polym`, `rapide`, `rgdi`),
et les `ValueSet-<code>-default-exam.json` leur équivalent pour les examens paracliniques —
à reprendre quand on fera l'étape « Examens ».

Radiant nomme **déjà** `analysis_type_code` dans ses traductions
(`case_exploration.analysis_type_code.*`) : le renommage aligne le schéma sur l'UI existante.

## 1. Déplacer trois colonnes de `cases` vers `analysis_catalog`

Décidé le 2026-08-24, à l'occasion de la section « Analyse » (étape 1).

| Colonne | Aujourd'hui | Proposé |
|---|---|---|
| `case_type_code` (« type de cas ») | `cases.case_type_code` → FK `case_type(code)` | `analysis_catalog.case_type_code` |
| `primary_condition` | `cases.primary_condition` (texte, ex. `MONDO:0700092`) | `analysis_catalog.primary_condition` |
| `condition_code_system` | `cases.condition_code_system` (texte, ex. `mondo`) | `analysis_catalog.condition_code_system` |

**Pourquoi** — ces trois valeurs ne dépendent pas du cas mais de l'analyse demandée :
tout cas `DYSM` est germinal et porte la condition « dystrophie musculaire ». Les laisser
sur `cases` oblige le prescripteur à ressaisir (et à pouvoir contredire) une information
que le catalogue connaît déjà. Une fois déplacées, l'étape 1 de la création de cas devient
un simple choix d'analyse et les trois champs deviennent **dérivés, en lecture seule** —
c'est ce que montre l'encart « Provient du catalogue d'analyses » de la maquette.

**Points d'attention**

- **`germline_family` reste dérivé, pas stocké.** `case_type(code)` ne contient que
  `germline` et `somatic` ; `germline_family` est calculé par les requêtes StarRocks à partir
  du nombre de patients/expériences du cas (cf. `backend/internal/repository/starrocks/cases.go`
  et `cases_test.go`). Le déplacement ne concerne donc que l'axe **germinal / somatique**,
  qui est bien une propriété de l'analyse. L'axe **solo / famille** doit rester dérivé du cas.
- **Un « défaut de portée » serait tout de même utile** dans le catalogue : `RGDI`, `FEAN`,
  `POLYM`, `EIDI`, `GENOR` se prescrivent en trio, les panels musculaires et `MITN` en solo.
  La maquette l'affiche (puce `Trio` / `Solo`) sous le nom provisoire
  `analysis_catalog.default_scope` — **à confirmer** : simple valeur par défaut du formulaire,
  pas une contrainte.
- **`case_category_code`** (`prenatal` / `postnatal`) : **tranché — reste sur `cases`.**
  Bien que `FEAN` soit prénatal par construction, un cas peut basculer. La maquette ne
  l'affiche donc plus comme valeur dérivée du catalogue.
- **API batch** (`backend/internal/types/case_batch.go`) : les champs `type`,
  `primary_condition_code_system` et `primary_condition_value` du payload deviennent
  redondants avec `analysis_code`. À conserver en lecture (tolérance) mais à ignorer, ou
  à retirer d'une v2 du contrat.
- **Rétrocompatibilité de lecture** : `types.CaseEntity` expose `case_type`,
  `primary_condition_id` et `primary_condition_name`. Ces champs doivent rester dans la
  réponse API — alimentés par une jointure sur `analysis_catalog` au lieu de colonnes de
  `cases`. Aucun changement côté frontend (`apps/case/src/entity/layout/header.tsx`
  continue de lire `case_type` et `analysis_catalog_code`).
- **Migration des données** : les cas existants portent tous `MONDO:0700092` /
  `germline` dans les semences ; en production il faudra vérifier que
  `cases.primary_condition` est bien constant par `analysis_catalog_id` avant de laisser
  tomber la colonne, et journaliser les écarts.

## 2. Nouvelles colonnes de `analysis_catalog`

- `case_type_code text NOT NULL` → FK `case_type(code)` (cf. §1).
- `primary_condition text NULL` — NULL pour les analyses **non spécifiques** (`GENOR`).
- `condition_code_system text NULL` — `mondo` en général, **`hpo` pour `RHAB`**
  (la rhabdomyolyse est un phénotype, pas une maladie : `HP:0003201`). Le champ étant déjà
  du texte libre côté `cases`, aucun élargissement n'est nécessaire — mais il faut confirmer
  que le frontend sait résoudre un code HPO comme il résout un code MONDO.
- `condition_group text NULL` **(nouveau, propre à la maquette)** — famille de conditions
  servant à regrouper les analyses dans la fenêtre de choix
  (`nonspec`, `neurodev`, `malfo`, `muscle`, `metab`, `immuno`). Sans elle, le regroupement
  logique de la fenêtre modale devrait être codé en dur dans le frontend, exactement comme
  le groupe « Maladies musculaires » l'est aujourd'hui dans clin
  (`AnalysisChoiceModal/index.tsx`). **Proposé — à valider.**
- `is_global_panel boolean DEFAULT false` **(nouveau)** — marque `MMG` comme panel global.
  Aujourd'hui clin le déduit d'un test sur le code (`isMuscularAnalysisAndNotGlobal`), ce qui
  bloque toute extension du mécanisme de réflexe à d'autres familles. **Proposé.**
- `reflex_to_analysis_code text NULL` **(nouveau)** — cible du réflexe (`MMG` pour les
  panels musculaires spécialisés), pour la même raison. **Proposé.**

## 3. Resté non modélisé — le réflexe

Le modèle Notion **ne prévoit rien** pour le mécanisme de réflexe. Dans clin, les 5 panels
musculaires spécialisés peuvent déclencher en réflexe le panel global `MMG`
(`isMuscularAnalysisAndNotGlobal`, `analysis.is_reflex`, affiché sur la fiche par
`AnalysisCard` : « Panel en réflexe »). **La case à cocher a donc été retirée de la maquette**
— elle n'aurait aucune colonne où atterrir. Il faut soit :

- `analysis_catalog.reflex_to_analysis_code text NULL` + `cases.is_reflex boolean` — le
  réflexe devient une propriété du catalogue, extensible à d'autres familles ; soit
- garder la règle en dur dans le frontend comme clin le fait aujourd'hui.

**À trancher** — c'est une fonctionnalité clinique réelle, actuellement perdue.

## 4. À faire côté `cases`

- `cases.is_reflex boolean DEFAULT false` **(nouveau)** — la case « analyser en réflexe le
  panel global » de l'étape 1 n'a aujourd'hui aucun équivalent dans Radiant. Dans clin, c'est
  `analysis.is_reflex` (`store/prescription/types.ts`) et c'est affiché sur la fiche
  (`AnalysisCard` : « Panel en réflexe »). **Proposé.**

---

## Écarts constatés (sans changement de modèle)

- **Le CodeSystem FHIR est la source de vérité des codes d'analyse** :
  `~/src/clin-fhir/site_root/input/resources/terminology/CodeSystem-analysis-request-code.json`,
  **37 codes**. Vérifié : ensemble **identique** à celui de la semence Radiant
  `qlin/analysis_catalog.sql`, dans les deux sens. Les deux listes sont donc déjà alignées —
  reste à savoir **laquelle génère l'autre** (aujourd'hui : personne, elles sont maintenues à
  la main en parallèle). **À proposer** : générer `analysis_catalog.sql` depuis le CodeSystem.
- **Catalogue ≠ analyses prescriptibles.** Les 37 codes existent au catalogue mais
  `clin-prescription-ui` n'en offre que **12** au formulaire (`AnalysisChoiceModal`). Il faut
  donc un **`analysis_catalog.is_orderable boolean`** pour distinguer les analyses
  prescriptibles de celles seulement importables par batch. La maquette porte déjà le drapeau
  (`orderable`) sans l'afficher. **Proposé.**
- **`case_type_code` n'est pas dérivable du nom de l'analyse.** Les trois panels de
  **prédisposition** au cancer (`TUHEM`, `TUPED`, `CONCO`) sont **germinaux** — la recherche
  se fait sur tissu normal — alors que `EXTUM`, `TRATU`, `SHEMA`, `STMO` sont **somatiques**
  (tissu tumoral). C'est l'argument le plus net en faveur du §1 : la valeur doit être saisie
  **une fois** par le labo dans le catalogue, pas déduite par le prescripteur à chaque cas.
- **`STMO` (« Sarcome des tissus mous et osseux ») : type indéterminé.** Le libellé ne dit pas
  s'il s'agit d'un profilage tumoral ou d'une prédisposition. Classé somatique par défaut dans
  la maquette, avec une puce « Somatique ? ». **À trancher avec le labo.**
- **`condition_code_system` ne sera pas toujours `mondo`.** `RHAB` (rhabdomyolyse) est un
  **phénotype**, pas une maladie : codé `HP:0003201` en HPO. Le champ est déjà du texte libre,
  mais il faut vérifier que le frontend sait **résoudre un code HPO** comme il résout un code
  MONDO (aujourd'hui `primary_condition_name` vient d'une table de termes MONDO côté
  StarRocks).
- **Sept conditions sur 37 n'ont pas de terme MONDO satisfaisant** (`HYPM`, `RHAB`, `DPSO`,
  `HDIP`, `HLEB`, `EIII`, `MSMD` — détail dans `CLAUDE.md`). Si `primary_condition` devient une
  colonne du catalogue, elle doit rester **nullable** et le catalogue doit pouvoir dire
  « condition non codable » sans bloquer la création de cas.
- **Doublon `NPC` / `NEUTP`** : même libellé « Neutropénie congénitale » dans le CodeSystem
  **et** dans la semence Radiant. À signaler à l'équipe Radiant / au labo.
- **`analysis_catalog.panel_id`** existe déjà (FK vers `panel`) — la maquette affiche donc un
  nom de panel, sans inventer de nombre de gènes. Quatre analyses n'ont pas de panel
  (`GENOR`, `RAPIDE`, `EXTUM`, `TRATU`) : la colonne doit rester nullable.
