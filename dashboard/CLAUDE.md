# Section Aperçu — vue d'ensemble du cas

Maquette de l'onglet **« Aperçu »** de la page Case de Radiant, placé **en premier**, à gauche de « Détails ». Fichier de travail : `dashboard_radiant.html` (le nom de fichier/dossier est resté `dashboard`, mais l'onglet s'intitule **Aperçu**). Les conventions transversales (HTML autonome, vérif headless, terminologie, en-tête, partage) sont dans le `CLAUDE.md` **racine**.

## Contexte

Onglet qui met en évidence les informations les plus importantes du cas en un coup d'œil. **Point de départ = le POC local de l'utilisateur** dans `~/src/radiant-portal`, branche `Vincent`, commit `ee45513d9` (« add overview tab ») + `c9286e687` (« cards content poc ») — jamais mergé/déployé, d'où son absence en production. Le vrai onglet s'appelle `Summary` dans le code (`CaseEntityTabs.Summary`), titre i18n `case_entity.summary.title` = « Aperçu », icône `FileText`.

La maquette **reproduit fidèlement** le contenu du POC (voir `frontend/apps/case/src/entity/summary/`), pour servir de base à l'itération.

## Fichiers

- `dashboard_radiant.html` — maquette principale (autonome, données inlinées en JS). Fichier de travail.

## État de la maquette

- **En-tête de page** — reproduit le `PageHeader` Radiant, identique à la maquette QC (Cas 1008, badges Germinal familial / EXM / Routine / En cours).
- **Barre d'onglets** — ordre : **Aperçu** (actif, icône FileText) · Détails · Variants · Fichiers · QC. *(« Détails de Cas » raccourci en « Détails ».)*
- **Boîte de texte libre façon assistant** (`.ask-wrap` / `.ask`) — centrée en haut de la page (`window.open`-style non câblé, maquette) : champ arrondi + icône « étincelles » + bouton d'envoi. Placeholder « Posez une question sur ce cas… ».
- **Mise en page en deux colonnes** (`.layout`, grille) sous la boîte de question :
  - **Colonne gauche — groupe « Activités »** (`.col-left`, actions de l'utilisateur), placé **en haut à gauche**. Trois cartes empilées (`.stack`) :
    1. **Variants** (`activity-variants-card`) — liste avec **colonnes alignées** (`.av-head` / `.av-row`, grid `1fr 84px 30px 20px`) : Variant (gène + AA) · **Interprétation** (badge court Pathogène / Prob. path. / VUS, ou `—`) · **Commentaires** (nombre, icône 💬 en tête de colonne) · **Flag** (drapeau rouge, icône en tête). Compteur dans l'en-tête.
    2. **Rapports** (`activity-reports-card`) — un ou aucun rapport (nom + taille + date + bouton téléchargement) ; **état vide** géré (« Aucun rapport généré pour ce cas. »). Compteur dans l'en-tête.
    3. **Commentaire sur le cas** (`activity-note-card`) — **texte libre** : affiche le commentaire existant (`CASE_NOTE` : texte + auteur + date, ou rien si `null`) puis une **zone d'ajout** (`textarea` + bouton Enregistrer, non câblé).
  - **Colonne droite** (`.col-right`) — deux groupes :
    - **Annotations** — deux cartes côte à côte (`.grid2`) :
      - **ClinVar** (`summary-clinvar-card`) — **liste plate, une ligne par variant** (`.cv-row`) : gène + **AA change** + badge Pathogénique / Prob. pathogénique.
      - **Priorisation des variants** (`summary-prioritization-card`) — **une seule carte pour les 3 algorithmes** (Exomiser · Phenovar · Franklin). Matrice **variant × algorithme** : une ligne par variant, colonne par algo = **rang `#n`** (ou `—`). **Union** triée par **consensus** (nb d'algos ↓, puis rang moyen) ; signalé par **barre latérale colorée** (vert = 3, indigo = 2) + badge `N/3`. Données `PRIO` (chevauchement volontaire).
    - **Contrôle qualité** (`summary-qc-card`) — **résumé minimal** : **verdict global** (badge = pire statut sur `QC_INDICATORS`) + icône colorée + **phrase-type** selon le statut + **lien « Ouvrir l'onglet QC → »** vers `../qc/qc_radiant.html`.

## Décisions de design (session 2026-07-16)

- **Variants affichés en changement d'acide aminé** (`GÈNE AAchange`, ex. `BRAF V600E`), **jamais en coordonnées génomiques** (demande utilisateur).
- **Listes de variants aplaties** : plus de « ligne gène + sous-lignes variants » ; une ligne par variant, tout au même niveau (ClinVar comme Priorisation).
- **Plusieurs algorithmes de priorisation dans une seule carte** avec mise en avant du **consensus** (accord entre Exomiser/Phenovar/Franklin = argument fort → remonte en tête).
- **Distinction annotations vs actions utilisateur** matérialisée par les trois groupes ; les variants interprétés/commentés/flaggés + rapports du POC sont regroupés dans **une seule boîte** plus compacte.
- **Section QC ajoutée** (n'existait pas dans le POC) qui résume les statuts des indicateurs de `qc/` — pas de valeurs, juste les verdicts.
- **Pas de texte explicatif sur la maquette dans le HTML** (les explications vont dans Notion). Ligne d'intro retirée.
- **Mise en page deux colonnes** : « Activités » (actions de l'utilisateur) déplacé **en haut à gauche** et renommé **« Activités »** ; annotations + QC à droite. Dans Variants, interprétation/commentaires/flags **alignés en colonnes**. Rapports = **un ou aucun** (état vide géré). Ajout d'une carte **« Commentaire sur le cas »** en texte libre (afficher + ajouter).

## Écarts vs le POC (assumés)

- **Données** : `MOCK_*` du POC réinlinés en JS (`CLINVAR`, `EXOMISER`, `QC_INDICATORS`, `VARIANTS`, `REPORTS`). Les AA changes sont inventés (démo) et cohérents entre les cartes. Rien n'est branché sur l'API.
- **Terminologie** : « Proband » du POC → **« Cas-index »** dans les noms de rapports (convention racine).

## Prochaines étapes

- Câbler (plus tard) la boîte de question à un vrai assistant ; définir son comportement.
- Enrichir : statut/avancement du cas, échéances, membres du trio, raccourcis vers les autres onglets.
- À l'intégration : brancher sur les vraies données (variants, scores Exomiser, statuts QC réels depuis la section `qc/`).
