# `hpo/` — Signes cliniques (navigateur de phénotype HPO)

Maquette de la **sélection des signes cliniques** : la carte « Signes cliniques » du
formulaire de création de cas, et la fenêtre modale qui donne accès à l'arbre HPO.
C'est le portage en HTML autonome du POC **`~/src/poc_hpo`** (React + antd devant un
serveur FastAPI qui chargeait `hp.obo` en mémoire). La maquette n'a plus de serveur :
**l'ontologie entière est inlinée dans le fichier**.

| Fichier | Rôle |
|---|---|
| **`signes_cliniques_radiant.html`** | **la maquette** — 1,5 Mo, dont ~1,4 Mo de données HPO |
| `build_data.py` | (re)génère le bloc de données inliné ; le seul script à relancer |

C'est l'**étape 3 du formulaire de prescription** (voir `prescription/CLAUDE.md`, table
d'avancement). La maquette est autonome pour ne pas alourdir
`prescription/create_case_radiant.html` ni anticiper l'étape 2 (Cas-index) : quand le
formulaire aura son enchaînement d'étapes, cette carte s'y glisse telle quelle.

## Ce que la maquette montre

**La carte « Signes cliniques »** — l'ordre est celui du POC :

1. **`Parcourir l'arbre HPO`** (bouton primaire) ouvre le navigateur ;
2. **`Sélectionnés depuis l'arbre HPO (n)`** — ce qui vient du navigateur, avec son
   **âge d'apparition** ;
3. **`Suggestions pour cette analyse`** — la liste par défaut de l'analyse (13 termes,
   repliée à 8) ; cocher ajoute le signe, avec son âge ;
4. **`Ajouter des signes NON OBSERVÉS`** *(facultatif)* — même navigateur, autre cible,
   **sans** âge d'apparition ;
5. **`Commentaire clinique général`**.

Le cas de démonstration est l'analyse **MITN** (55370 - Mitochondriopathies nucléaires) :
les 13 suggestions sont sa liste par défaut, d'où le badge `MITN` dans l'en-tête.

**Le navigateur de phénotype (HPO)** — deux volets :

- à gauche l'arbre des **18 689 termes** de la sous-arborescence « Anomalie phénotypique »
  (`HP:0000118`), replié sur ses 23 catégories en gras, la bascule **FR / EN** et le champ
  de recherche ;
- à droite la sélection en cours, retirable une à une ;
- en pied la note de provenance des traductions, `Annuler` / `Appliquer`.

La **recherche** (3 caractères minimum) cherche dans les libellés de la langue affichée et
dans les identifiants `HP:`, puis **remonte les ancêtres** de chaque résultat et ouvre les
branches, le texte trouvé surligné. Un terme HPO ayant plusieurs parents (HPO est un DAG,
22 978 arêtes), il **apparaît sous chacun de ses chemins** — cocher une occurrence coche
les autres.

## Les données

**Sources** (dépôt `poc_hpo`) : `hp.obo` pour l'ontologie, `hp-fr-amended.babelon.tsv`
pour le français. Ce sont les mêmes fichiers que le POC monte en mémoire au démarrage.

```sh
python3 build_data.py                    # chemins par défaut : ~/src/poc_hpo/
python3 build_data.py --obo … --babelon … # après une nouvelle release HPO
```

Le script réécrit **uniquement** le bloc entre `/*HPO-DATA-BEGIN*/` et `/*HPO-DATA-END*/`,
tout en bas du fichier. Le reste du HTML s'édite à la main, comme les autres maquettes.

État actuel :

| | |
|---|---|
| termes | **18 690** dont la racine — **18 689** sélectionnables |
| arêtes parent → enfant | 22 978 |
| traductions | **13 555 officielles + 5 135 automatiques** (Google), 0 terme sans traduction |

Les termes obsolètes de l'OBO sont écartés, comme dans le POC.

Format d'une ligne : `num|libellé fr|libellé en|auto|parents`. `num` est l'identifiant sans
son préfixe ni ses zéros (`HP:0001250` → `1250`), `en` est vide s'il est identique au
français, `auto` vaut `1` pour une traduction Google. Aucun libellé ne contient de `|` ;
l'apostrophe inversée parasite de `HP:0000448` est échappée par le script.

**Le poids est assumé.** 1,5 Mo là où les autres maquettes tiennent en 30-46 ko : c'est le
prix de l'arbre complet. Un arbre élagué aurait rendu la maquette trompeuse — un clinicien
tape un terme réel et doit le trouver, sinon ce qu'on met à l'épreuve n'est plus la
recherche mais un décor. Le fichier compresse à **434 ko** en zip (mesuré), ce qui reste
envoyable par courriel.

## Fidélité au POC

Repris tel quel, y compris ce qui surprend :

- recherche à partir de **3 caractères**, sinon retour à la navigation ;
- **tri des enfants par libellé**, comparaison par point de code (le tri Python du POC) —
  d'où `Anomalie de l'appareil…` avant `Anomalie de la cavité…` ;
- **astérisque** sur les traductions Google, **infobulle** donnant le terme anglais et la
  provenance de la traduction ; note de pied `* … (5135 sur 18689 termes au total)`,
  affichée en français seulement ;
- les termes **déjà retenus** (observés ou non observés) sont **désactivés** dans l'arbre ;
- la bascule **FR / EN vide la recherche et remonte l'arbre** ;
- la modale **se réinitialise à chaque ouverture** (français, arbre replié, sélection vide) ;
- suggestions repliées à **8**, les cochées remontent en tête ;
- **`Appliquer à tous`** n'apparaît qu'après un changement d'âge et seulement à partir de
  deux signes observés ;
- la recherche **ignore accents, ligatures `œ`/`æ`, apostrophes typographiques et espaces
  insécables** : `fold()` est le miroir de `app/text.py` du POC, index et requête repliés
  des deux côtés, surlignage compris. Les chiffres sont identiques de part et d'autre —
  `deficience` et `déficience` → 51, `coeur` et `cœur` → 21, `oeil` et `œil` → 33.

## Écarts assumés

- **Chrome Radiant** : `PageHeader` (fil d'Ariane « ‹ Cas », badges type + code d'analyse,
  pastille `Brouillon`) et carte, là où le POC était une page nue. Conforme à la ligne
  « fidélité au produit » du dépôt.
- **Pied de carte `Précédent` / `Suivant`**, ajouté : `Suivant` ne s'active qu'avec **au
  moins un signe observé** — la seule règle du formulaire, autrement invisible. Les deux
  boutons ne mènent nulle part tant que les étapes voisines n'existent pas.
- **Un seul navigateur** pour les observés et les non observés, avec une cible ; le POC en
  instancie deux.
- **Débounce 120 ms** au lieu de 600 : les 600 ms du POC payaient l'aller-retour réseau,
  qui n'existe plus. Tout est local — **9 ms** pour `ataxie`, recherche et rendu compris ;
  le décodage des 18 690 termes au chargement prend **6 ms**.
- **`Aucun terme ne correspond.`** là où le POC laisse l'arbre vide.
- **Pas de virtualisation** : l'arbre est réécrit en entier à chaque dépliage. Tenu jusqu'à
  quelques milliers de lignes — `anomalie du` (338 résultats, 954 lignes) s'affiche en
  **18 ms** ; au-delà, la vraie intégration reposera sur le `Tree` d'antd, virtualisé.

## Observations à porter au produit

Ce que la maquette rend visible, à trancher hors maquette :

1. ~~La recherche est sensible aux accents et à la ponctuation~~ — **corrigé**, dans le POC
   (`app/text.py` + `PhenotypeTree/fold.ts`) puis ici. C'est la maquette qui a rendu le
   défaut visible : les libellés mélangent les deux graphies du même mot, si bien que
   `deficience` ne ramenait **rien** contre 52 pour `déficience`, et que ni `coeur` (9) ni
   `cœur` (12) ne trouvaient tout. Le repli porte sur les accents, les ligatures `œ`/`æ`,
   les apostrophes typographiques et les espaces insécables.
2. **La traduction de `HP:0001250` est fautive** : `Epilépsie` pour `Seizures`, accent
   déplacé et sens glissé, et pourtant marquée `OFFICIAL`. Le repli de la recherche la rend
   désormais trouvable (`epilepsie` ramène les 6 termes de la famille, contre 2 avant), mais
   le libellé reste faux à l'écran. C'est un terme de la liste par défaut de MITN : à
   signaler en amont, côté babelon.
3. **Le même code porte deux noms selon l'endroit** : `HP:0001250` s'affiche
   `Crise d'épilepsie` dans les suggestions (nom venu de la configuration du formulaire) et
   `Epilépsie` dans l'arbre (nom venu de babelon). Le clinicien voit deux libellés pour un
   seul code.
4. **27 % des termes (5 135 sur 18 689) sont des traductions Google.** L'astérisque et
   l'infobulle le disent, mais c'est la proportion qui mérite l'arbitrage du labo.
5. **La bascule FR / EN remonte l'arbre et vide la recherche** : cherchant en français sans
   trouver, on repart de zéro en anglais.

## Vérification

```sh
google-chrome --headless=new --disable-gpu --window-size=1440,1000 \
  --screenshot=out.png "file://$PWD/signes_cliniques_radiant.html"
```

Pour photographier un état interactif, injecter un appel avant `</body>` sur une copie
temporaire — les fonctions sont globales :

```js
toggleSuggestion(1251, true);          // cocher une suggestion (numéro HPO sans préfixe)
openBrowser('observed');               // ouvrir le navigateur
toggleNode('707');                     // déplier une branche
el('q').value = 'ataxie'; onQuery();   // chercher (le débounce s'applique)
toggleTerm(2073); applyBrowser();      // cocher un terme trouvé, puis Appliquer
setLang('en');                         // basculer en anglais
```
