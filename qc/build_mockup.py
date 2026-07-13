#!/usr/bin/env python3
"""Génère une maquette HTML statique explorable pour le QC de couverture des gènes (Radiant)."""
import csv, json, random, io

random.seed(42)
SRC = "test_gene_coverage.csv"

COLS = ["coverage5","coverage15","coverage30","coverage50","coverage100",
        "coverage200","coverage300","coverage400","coverage500","coverage1000"]
THRESH = [5,15,30,50,100,200,300,400,500,1000]

rows = []
with open(SRC) as f:
    r = csv.reader(f)
    header = next(r)  # #gene,size,average_coverage,coverage5,...
    for line in r:
        if not line: continue
        g = {
            "gene": line[0],
            "size": int(line[1]),
            "avg": float(line[2]),
            "cov": [float(x) for x in line[3:13]],
        }
        rows.append(g)

by_gene = {g["gene"]: g for g in rows}

# Gènes cliniques explicites (existent dans le CSV)
clinical = ["BRCA1","BRCA2","TP53","CFTR","MLH1","MSH2","DMD","MECP2","SCN1A",
            "FBN1","PTEN","APC","RB1","NF1","VHL"]

# Bande "attention": c15 entre 0.5 et 0.999
warn_band = [g for g in rows if 0.5 <= g["cov"][1] < 0.999]
# Bien couvert à 15x mais partiel à 30x
c30_partial = [g for g in rows if g["cov"][1] >= 0.999 and 0.4 <= g["cov"][2] < 0.9]
# Régions sombres / non mappables (multicopie)
dark = [g for g in rows if g["cov"][0] < 0.1 or g["avg"] < 5]
# Normaux (bien couverts partout jusqu'à 30x)
normals = [g for g in rows if g["cov"][2] >= 0.999]

sel = {}
def add(lst, n):
    for g in random.sample(lst, min(n, len(lst))):
        sel[g["gene"]] = g

for name in clinical:
    if name in by_gene: sel[name] = by_gene[name]
add(warn_band, 45)
add(c30_partial, 15)
add(dark, 18)
add(normals, 120)

sample = sorted(sel.values(), key=lambda g: g["gene"])
# format compact: [gene, size, avg, cov[10]]
data = [[g["gene"], g["size"], round(g["avg"],1), [round(c,4) for c in g["cov"]]] for g in sample]

# Panels prédéfinis (utilisent des gènes présents dans l'échantillon)
panels = {
    "Cancer héréditaire sein/ovaire": ["BRCA1","BRCA2","TP53","PTEN","MLH1","MSH2","APC"],
    "Prédispositions ACMG SF (extrait)": ["BRCA1","BRCA2","TP53","PTEN","MLH1","MSH2","APC","RB1","VHL","NF1"],
    "Neurodéveloppement (extrait)": ["MECP2","SCN1A","DMD","NF1"],
}
# ne garder que les gènes présents
present = {g["gene"] for g in sample}
panels = {k:[x for x in v if x in present] for k,v in panels.items()}

print(f"Échantillon: {len(data)} gènes | total CSV: {len(rows)}")
with open("_sample_data.json","w") as f:
    json.dump({"genes": data, "panels": panels, "thresholds": THRESH,
               "total_csv": len(rows)}, f, ensure_ascii=False)
print("écrit _sample_data.json")
