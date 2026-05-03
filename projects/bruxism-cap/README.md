# bruxism-cap

Minimal starter scaffold for **bruxism detection from EEG / EMG signals** using the public **PhysioNet CAP Sleep Database**.

This is intentionally a **small reproduction / benchmarking project**, not a clinical detector.

## Project goal

Build the smallest honest baseline that can:
- load a tiny CAP subset (`brux1`, `brux2`, plus a few controls)
- extract one signal channel into fixed windows
- compute classical handcrafted features
- train simple models
- compare **leaky random window splits** vs **subject-aware splits**

## Why this project exists

The ai-lab research pass found that the easiest credible starting point is:
- one public dataset
- one channel family
- one binary task
- classical models
- subject-aware evaluation

CAP is not a purpose-built bruxism benchmark, but it is openly accessible and already used by recent bruxism papers. That makes it good enough for a first reproducible pilot.

## Scope for version 1

**Do now**
- reproduce a tiny EEG/EMG window-classification baseline
- keep the task binary: `bruxism` vs `control`
- report balanced accuracy, sensitivity, specificity, and AUROC
- report the gap between random window CV and leave-one-subject-out CV

**Do not do yet**
- deep learning
- multimodal fusion
- clinical claims
- custom hardware collection

## Folder layout

- `data/README.md` — raw-data and manifest notes
- `data/subject_manifest.example.csv` — starter manifest format
- `notebooks/00_cap_subset_inspection.ipynb` — first inspection notebook stub
- `src/features.py` — handcrafted window features
- `src/prepare_windows.py` — EDF -> feature CSV pipeline
- `src/train_baseline.py` — baseline training with random vs LOSO CV
- `src/eval.py` — comparison helper for saved metric JSON files
- `reports/first-baseline.md` — experiment checklist / artifact template

## Environment

Bootstrap the repo if needed:

```bash
cd /home/hermes/work/ai-lab
./scripts/bootstrap-python.sh
source .venv/bin/activate
uv pip install -e '.[biosignals]'
```

The `biosignals` extra is intentionally optional so the main Unsloth/Modal workflow stays lightweight.

## Step 1: download a tiny CAP subset

```bash
cd /home/hermes/work/ai-lab
mkdir -p projects/bruxism-cap/data/raw/capslpdb
cd projects/bruxism-cap/data/raw/capslpdb

wget -nc https://physionet.org/files/capslpdb/1.0.0/brux1.edf
wget -nc https://physionet.org/files/capslpdb/1.0.0/brux2.edf
wget -nc https://physionet.org/files/capslpdb/1.0.0/n3.edf
wget -nc https://physionet.org/files/capslpdb/1.0.0/n5.edf
wget -nc https://physionet.org/files/capslpdb/1.0.0/n10.edf
wget -nc https://physionet.org/files/capslpdb/1.0.0/n11.edf
```

These controls mirror the small compatible-control set described in one of the recent single-channel EEG papers. If channel availability differs, swap them for other healthy controls.

## Step 2: inspect channel names first

```bash
python3 projects/bruxism-cap/src/prepare_windows.py \
  --edf projects/bruxism-cap/data/raw/capslpdb/brux1.edf \
  --list-channels
```

The exact channel name may differ by record. Start with a single EEG derivation such as `C4-P4` if present.

## Step 3: build a feature CSV

Example for one record:

```bash
python3 projects/bruxism-cap/src/prepare_windows.py \
  --edf projects/bruxism-cap/data/raw/capslpdb/brux1.edf \
  --subject-id brux1 \
  --label bruxism \
  --channel C4-P4 \
  --window-seconds 30 \
  --limit-windows 120 \
  --out projects/bruxism-cap/data/window_features.csv
```

Append more records with `--append`:

```bash
python3 projects/bruxism-cap/src/prepare_windows.py \
  --edf projects/bruxism-cap/data/raw/capslpdb/n3.edf \
  --subject-id n3 \
  --label control \
  --channel C4-P4 \
  --window-seconds 30 \
  --limit-windows 120 \
  --append \
  --out projects/bruxism-cap/data/window_features.csv
```

## Step 4: train a baseline

Leakage-prone reference split:

```bash
python3 projects/bruxism-cap/src/train_baseline.py \
  --features-csv projects/bruxism-cap/data/window_features.csv \
  --cv random \
  --out projects/bruxism-cap/reports/random-window-cv.json
```

Subject-aware split:

```bash
python3 projects/bruxism-cap/src/train_baseline.py \
  --features-csv projects/bruxism-cap/data/window_features.csv \
  --cv loso \
  --out projects/bruxism-cap/reports/loso-cv.json
```

Compare the two:

```bash
python3 projects/bruxism-cap/src/eval.py \
  projects/bruxism-cap/reports/random-window-cv.json \
  projects/bruxism-cap/reports/loso-cv.json
```

## Success criterion for the first pass

A successful first pass is **not** “95% accuracy.”

It is:
- a reproducible raw-data subset
- a feature CSV that can be regenerated
- one honest baseline report
- a clear comparison between leaky and subject-aware evaluation

## Where to extend next

After this scaffold works, the next sensible directions are:
1. use richer EMG-focused channels when available
2. add REM-only filtering if annotations are available and worth the extra complexity
3. test whether simple channel fusion helps after the single-channel baseline is stable
4. only then consider a small neural baseline
