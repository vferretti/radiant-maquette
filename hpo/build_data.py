#!/usr/bin/env python3
"""Injecte les données HPO dans `signes_cliniques_radiant.html`.

La maquette est un HTML autonome : l'arbre HPO complet y vit inliné, entre les
deux marqueurs `/*HPO-DATA-BEGIN*/` … `/*HPO-DATA-END*/`. Ce script est le seul
endroit qui touche à ce bloc ; tout le reste du fichier s'édite à la main.

    python3 build_data.py [--obo …/hp.obo] [--babelon …/hp-fr-amended.babelon.tsv]

Sources (dépôt `poc_hpo`) :
  hp.obo                    l'ontologie HPO (release téléchargée sur hpo.jax.org)
  hp-fr-amended.babelon.tsv les traductions françaises (officielles + Google)

Format d'une ligne, `|` comme séparateur (aucun libellé n'en contient) :

    <num>|<libellé fr>|<libellé en>|<a>|<parents>

  num      « HP:0001250 » → 1250 (le préfixe et les zéros se reconstruisent)
  fr       vide si le terme n'est pas traduit — l'anglais sert alors de repli
  en       vide si identique au français
  a        « 1 » si la traduction est automatique (Google), sinon vide
  parents  numéros des parents, séparés par des virgules (HPO est un DAG :
           un terme peut en avoir plusieurs)
"""

from __future__ import annotations

import argparse
import csv
import re
import sys
from collections import deque
from pathlib import Path

PA_ROOT = "HP:0000118"  # Anomalie phénotypique — la maquette s'y restreint
HERE = Path(__file__).resolve().parent
HTML = HERE / "signes_cliniques_radiant.html"
DEFAULT_POC = Path.home() / "src" / "poc_hpo"
BEGIN, END = "/*HPO-DATA-BEGIN*/", "/*HPO-DATA-END*/"


def esc_js(text: str) -> str:
    """Neutralise ce qui casserait le littéral gabarit JS qui porte les données.

    Un seul libellé est concerné aujourd'hui (une apostrophe inversée parasite
    dans HP:0000448 côté babelon), mais l'échappement doit tenir pour toute
    release à venir.
    """
    return text.replace("\\", "\\\\").replace("`", "\\`").replace("${", "$\\{")


def parse_obo(path: Path) -> tuple[dict[str, str], dict[str, list[str]]]:
    """→ ({id: libellé anglais}, {id: [parents]}), termes obsolètes exclus."""
    labels: dict[str, str] = {}
    parents: dict[str, list[str]] = {}
    cur_id = cur_name = None
    cur_is_a: list[str] = []
    obsolete = in_term = False

    def commit() -> None:
        if cur_id and cur_name and not obsolete:
            labels[cur_id] = cur_name
            parents[cur_id] = list(cur_is_a)

    with path.open(encoding="utf-8") as fh:
        for raw in fh:
            line = raw.rstrip("\n")
            if line == "[Term]":
                if in_term:
                    commit()
                cur_id = cur_name = None
                cur_is_a, obsolete, in_term = [], False, True
                continue
            if line.startswith("[") and line.endswith("]"):
                if in_term:
                    commit()
                in_term = False
                continue
            if not in_term:
                continue
            if line.startswith("id: "):
                cur_id = line[4:]
            elif line.startswith("name: "):
                cur_name = line[6:]
            elif line.startswith("is_a: "):
                cur_is_a.append(line[6:].split(" ", 1)[0])
            elif line.startswith("is_obsolete: true"):
                obsolete = True
    if in_term:
        commit()
    return labels, parents


def pa_subtree(labels: dict[str, str], parents: dict[str, list[str]]) -> set[str]:
    """Descendants de « Anomalie phénotypique », racine incluse."""
    children: dict[str, list[str]] = {}
    for nid, pids in parents.items():
        for pid in pids:
            if pid in labels:
                children.setdefault(pid, []).append(nid)
    if PA_ROOT not in labels:
        sys.exit(f"{PA_ROOT} absent de l'OBO — abandon")
    seen = {PA_ROOT}
    queue = deque([PA_ROOT])
    while queue:
        for cid in children.get(queue.popleft(), ()):
            if cid not in seen:
                seen.add(cid)
                queue.append(cid)
    return seen


def parse_babelon(path: Path, pa: set[str]) -> dict[str, tuple[str, bool]]:
    """→ {id: (libellé français, traduction automatique ?)}."""
    fr: dict[str, tuple[str, bool]] = {}
    with path.open(newline="", encoding="utf-8") as fh:
        for row in csv.DictReader(fh, delimiter="\t"):
            if row["predicate_id"] != "rdfs:label":
                continue
            hp_id, value = row["subject_id"], row.get("translation_value", "")
            if hp_id in pa and value:
                fr[hp_id] = (value, row.get("translation_status") == "AUTOMATIC")
    return fr


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--obo", type=Path, default=DEFAULT_POC / "hp.obo")
    ap.add_argument("--babelon", type=Path, default=DEFAULT_POC / "hp-fr-amended.babelon.tsv")
    args = ap.parse_args()

    for p in (args.obo, args.babelon, HTML):
        if not p.exists():
            sys.exit(f"introuvable : {p}")

    labels, parents = parse_obo(args.obo)
    pa = pa_subtree(labels, parents)
    fr = parse_babelon(args.babelon, pa)

    lines = []
    for nid in sorted(pa, key=lambda i: int(i[3:])):
        label_fr, auto = fr.get(nid, ("", False))
        label_en = labels[nid]
        lines.append("|".join((
            str(int(nid[3:])),
            esc_js(label_fr),
            "" if label_en == label_fr else esc_js(label_en),
            "1" if auto else "",
            ",".join(str(int(p[3:])) for p in parents.get(nid, ()) if p in pa),
        )))
    payload = "\n".join(lines)

    html = HTML.read_text(encoding="utf-8")
    if BEGIN not in html or END not in html:
        sys.exit(f"marqueurs {BEGIN} … {END} absents de {HTML.name}")
    block = f"{BEGIN}\n`{payload}`\n{END}"
    html = re.sub(re.escape(BEGIN) + r".*?" + re.escape(END), lambda _: block, html, flags=re.S)
    HTML.write_text(html, encoding="utf-8")

    auto = sum(1 for _, a in fr.values() if a)
    missing = sum(1 for nid in pa if nid != PA_ROOT and nid not in fr)
    print(f"{len(pa)} termes, dont la racine {PA_ROOT} — {len(pa) - 1} sélectionnables")
    print(f"  traductions : {len(fr) - auto} officielles + {auto} automatiques"
          f" — {missing} termes sans traduction (l'anglais sert de repli)")
    print(f"  arêtes parent→enfant : {sum(len(parents.get(n, ())) for n in pa)}")
    print(f"→ {HTML.name} : {HTML.stat().st_size / 1024:.0f} Ko")


if __name__ == "__main__":
    main()
