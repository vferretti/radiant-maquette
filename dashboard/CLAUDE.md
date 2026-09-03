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
- **Mise en page en deux rangées** (`.layout`) :
  - **Rangée 1** (`.row1`, grille 2 colonnes) — **colonne gauche** (`.col-a`) = **Cas** ; **colonne droite** = **Activités**. Colonne **Cas** (`case-summary-card`) : carte compacte empilant l'**identité du cas-index** (`.cas-info`, `<dl>` : Patient, Dossier `594383-CHUSJ`, Sexe, Naissance, **Échantillon** `DMxxxxxx` — cas-index uniquement — et **Analyse** = pastille `RGDI` + libellé) **au-dessus** d'un **petit pédigrée du trio en SVG** (`.cas-ped`, séparé par un filet) : carré = masculin, cercle = féminin, **rempli = atteint** / **vide = non atteint** (légende `.ped-leg`) ; père atteint × mère non atteinte → **cas-index** (fille, atteinte) marquée d'une **flèche proband**. Colonne **Activités** (actions de l'utilisateur) — deux cartes empilées (`.stack`) :
    1. **Variants** (`activity-variants-card`) — liste avec **colonnes alignées** (`.av-head` / `.av-row`, grid `1fr 56px 42px 42px`) ; en-tête de 1re colonne = **SNV** (gène + AA) · **Interprétation** · **Commentaires** · **Flag**. Les colonnes **Commentaires** et **Flag** reprennent **fidèlement les icônes lucide du tableau de variants de Radiant** (`.vic`) : `MessageSquare`, `Flag` ; l'en-tête d'interprétation garde `ClipboardList`. États repris de Radiant : **actif** = `text-primary fill-primary/20` (commenté) — le commentaire ajoute un **point** `bg-primary` (`.dot`) ; flag actif = **rouge plein** ; **vide** = `text-muted-foreground/40`. La cellule **Interprétation** affiche le **verdict abrégé** coloré (`.cls`, `CLS_ABBR` : P / LP / VUS) ou **—** ; libellé complet en infobulle. Deux sous-listes partageant le même rendu (`variantRow`) : **SNV** (`#variants`) puis **CNV** (`#cnvs`, format `Type:chr:start-end`). Compteur = SNV + CNV.
    2. **Commentaire sur le cas** (`activity-note-card`) — **texte libre** : affiche le commentaire existant (`CASE_NOTE`, ou rien si `null`) puis une **zone d'ajout** (`textarea` + bouton Enregistrer, non câblé).
  - **Rangée 2** (`.row2`, pleine largeur) — groupe **Priorisation des variants**, deux cartes côte à côte (`.grid2`), volontairement **adjacentes** pour que le lecteur compare l'algorithme et la synthèse :
    - **Priorisation algorithmique** (`summary-prioritization-card`) — matrice **variant × méthode** (`.pm-head` / `.pm-row`, grid `1fr 62px 62px`), données `PRIO` : **Exomiser** et **Radiant** en colonnes (`.pm-cell`) : rang `#n` (`—` si non retenu) et, sous le rang Exomiser, son **score de variant** (`exomiser_variant_score`, 0 à 1). Pas de score affiché pour Radiant : la pondération des couches n'est pas encore validée par les généticiens, un nombre suggérerait une précision qu'on n'a pas — les pastilles de critères portent la justification. Radiant = la **requête combinée en quatre couches** (rareté gnomAD *et* cohorte interne · cohérence génotype-phénotype · preuve établie · in-silico en départage), dont les critères sont les nôtres, d'où le **tri par rang Radiant**. Chaque ligne porte ses **critères déclenchés** sous forme de pastilles (`.pm-crits` / `.crit`, valeur en chasse fixe : `Impact HIGH`, `gnomAD 4,1e-5`, `CADD 27`, `Déjà classé pathogénique 2 cas`), et en rouge (`.crit.neg`) le motif d'exclusion (`Écarté — appel douteux ratio 0,18 · 12×`). **Aucun de ces libellés n'est rédigé par le modèle** : chacun correspond à un drapeau ou une valeur renvoyés par la requête, d'où le passage par des **codes** (`crits:[{c:'de_novo'},…]` + table `CRIT_LABEL`) — dans le portail ils viendront de l'i18n FR/EN. Rendus en pastilles et non en phrase, précisément pour qu'on ne les prenne pas pour du texte généré. **Barre latérale colorée** (`.pm-row.accord`) = variant retenu par les deux méthodes ; son absence signale une divergence (TRAPPC9 hors Exomiser, CDKL5 écarté par Radiant). Phenovar et Franklin ne seront pas disponibles : leurs colonnes et l'ancien badge de consensus `N/3` ont disparu.
    - **Variants prioritaires — synthèse de l'assistant** (`summary-ai-card`) — la carte IA. En-tête : titre + pastille **« IA · non validé »** (`.chip.ai`, icône étincelles) + pastille **« Périmée »** conditionnelle + **bouton régénérer** (`icon-btn`, `RotateCw`). Corps (`#aiCard`) : **synthèse de 3-4 phrases** (`.ai-syn`), puis les **candidats** (`.ai-row`, grid `1fr 62px`) = variant + **motif** (`.ai-why`, la couche qui l'a fait remonter) + **rang Exomiser en référence** (`—` si hors top 5), puis les **divergences** (`.ai-div`, flèche bas = écarté malgré Exomiser, flèche haut = ajouté hors classement), puis un **pied** (`.ai-foot`) avec horodatage, modèle, mention « à valider par le généticien » et lien **« Ouvrir dans l'assistant → »**. Quatre états pilotés par la constante `AI_STATE` : `ready` · `stale` (bandeau orange « les données ont changé depuis cette synthèse ») · `loading` (spinner + squelettes, première ouverture de l'onglet) · `error` (message + lien vers l'assistant, la priorisation Exomiser restant disponible à côté).

## Décisions de design (session 2026-07-16)

- **Variants affichés en changement d'acide aminé** (`GÈNE AAchange`, ex. `BRAF V600E`), **jamais en coordonnées génomiques** (demande utilisateur).
- **Listes de variants aplaties** : plus de « ligne gène + sous-lignes variants » ; une ligne par variant, tout au même niveau (ClinVar comme Priorisation).
- **Plusieurs algorithmes de priorisation dans une seule carte** avec mise en avant du **consensus** (accord entre Exomiser/Phenovar/Franklin = argument fort → remonte en tête).
- **Distinction annotations vs actions utilisateur** matérialisée par les trois groupes ; les variants interprétés/commentés/flaggés + rapports du POC sont regroupés dans **une seule boîte** plus compacte.
- **Section QC ajoutée** (n'existait pas dans le POC) qui résume les statuts des indicateurs de `qc/` — pas de valeurs, juste les verdicts.
- **Pas de texte explicatif sur la maquette dans le HTML** (les explications vont dans Notion). Ligne d'intro retirée.
- **Mise en page** (session 2026-07-17) : rangée 1 = **colonne gauche `Cas` + `Contrôle qualité` empilés** · **colonne droite `Activités`** ; rangée 2 = **Annotations** (pleine largeur). Empiler Cas + QC à gauche équilibre les hauteurs (une 3e colonne QC isolée laissait de trop grands écarts de hauteur). Avant : deux colonnes (Activités à gauche ; annotations + QC à droite). Dans Variants, interprétation/commentaires/flags **alignés en colonnes**. Rapports = **un ou aucun** (état vide géré). Carte **« Commentaire sur le cas »** en texte libre (afficher + ajouter).

## Décisions de design (session 2026-09-03) — cartes retenues pour la V1

- **Cartes retirées** : la boîte de question en texte libre, **Contrôle qualité**, **Rapports**, et **ClinVar**. Conservées : **Cas**, **Activités** (Variants + Commentaire), **Priorisation Exomiser**, plus la nouvelle **carte IA**. Périmètre suffisant pour une première version.
- **Conséquence de mise en page** : la colonne gauche ne porte plus que « Cas » (le QC équilibrait sa hauteur face à « Activités »). Assumé pour l'instant ; à revoir si l'écart de hauteur gêne — une option est de déplacer la carte IA sous « Cas ».
- **La requête combinée Radiant est une colonne, pas un implicite** : elle apparaît à côté d'Exomiser dans la carte algorithmique, avec ses motifs. Première version où seule la carte IA la montrait : une carte estampillée « IA · non validé » contenant en fait du déterministe brouille la lecture — le déterministe doit être visible comme tel.
- **Carte IA = synthèse, pas seconde liste**. La priorisation algorithmique reste la source du classement ; la carte IA apporte ce qu'Exomiser ne peut pas savoir (fréquence dans la cohorte interne, historique d'interprétation du tenant, CNV et second hit, qualité d'appel, statut de porteur) et **énonce l'accord comme les divergences** — sans quoi deux cartes voisines donnent l'illusion d'une corroboration indépendante alors que la seconde relit le score de la première.
- **Génération à l'ouverture de l'onglet, conservée, régénérable** : d'où les états `loading` / `ready` / `stale` / `error` et le bouton de rafraîchissement. Le cache est invalidé par une **empreinte des entrées** (données du cas, version du prompt, modèle), pas par une durée de validité — voir la page Notion « Radiant LibreChat » pour la stratégie complète (backend, coût, droits).
- **Aucune donnée identifiante dans la carte IA** (gène, changement d'acide aminé, zygosité, transmission uniquement) : c'est ce qui rend son cache partageable entre utilisateurs d'un même tenant.
- **Pas de tasks dans l'interface** : la notion de task (`task_id`) est un concept de pipeline que les généticiens ignorent — la carte parle de séquençage et de variants.

## Écarts vs le POC (assumés)

- **Données** : `MOCK_*` du POC réinlinés en JS (`CLINVAR`, `EXOMISER`, `QC_INDICATORS`, `VARIANTS`, `REPORTS`). Les AA changes sont inventés (démo) et cohérents entre les cartes. Rien n'est branché sur l'API.
- **Terminologie** : « Proband » du POC → **« Cas-index »** dans les noms de rapports (convention racine).

## Prochaines étapes

- Câbler la carte IA sur l'endpoint du portail (`/cases/{id}/ai-insight`) quand il existera ; d'ici là, données `AI` inlinées.
- Harmoniser les données de démonstration : « Activités » et le commentaire du cas parlent de gènes de cancer (BRCA1/TP53/MLH1) alors que le cas est un RGDI et que la priorisation parle de gènes de développement — incohérence héritée du POC, à nettoyer avant de montrer la maquette aux généticiens.
- Enrichir : statut/avancement du cas, échéances, membres du trio, raccourcis vers les autres onglets.
- À l'intégration : brancher sur les vraies données (variants, scores Exomiser, statuts QC réels depuis la section `qc/`).
