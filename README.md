# RES-SAT Solver

This project implements the RES‑SAT algorithm in Python. The RES‑SAT algorithm takes a CNF formula (given as a set of clauses) that is known to be satisfiable and produces a satisfying interpretation using resolution.

## Run RES-SAT on Single CNF File

Run these scripts to find the interpretation and satisfiability of CNF files.

```
python src/main.py examples/aim-100-1_6-no-1.cnf
python src/main.py examples/aim-50-1_6-yes1-4_simplified.cnf
```

## Compute Memory & Runtime

```
python src/test_aim.py # compute for AIM dataset
python src/test_phole.py # compute for Pigeonhole dataset
```
