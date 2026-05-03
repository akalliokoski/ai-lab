# Bruxism CAP Scaffold Implementation Plan

> **For Hermes:** keep this project deliberately small and reproducible; optimize for honest evaluation, not model complexity.

**Goal:** Create a minimal repo-ready starter scaffold for a CAP Sleep Database bruxism pilot.

**Architecture:** Use a lightweight project under `projects/bruxism-cap/` with one raw-data note, one feature-extraction script, one baseline training script, one comparison/eval helper, and one notebook stub for inspection. Keep preprocessing classical and subject-aware so the first result can expose leakage risk immediately.

**Tech Stack:** Python 3.11+, pandas, numpy, scikit-learn, optional MNE for EDF reading, existing ai-lab repo docs/wiki workflow.

---

### Task 1: Create the project skeleton
- Add `projects/bruxism-cap/README.md`
- Add `projects/bruxism-cap/data/README.md`
- Add `projects/bruxism-cap/reports/first-baseline.md`
- Add `projects/bruxism-cap/notebooks/00_cap_subset_inspection.ipynb`

### Task 2: Add the minimal data-prep code
- Add `projects/bruxism-cap/src/features.py`
- Add `projects/bruxism-cap/src/prepare_windows.py`
- Add `projects/bruxism-cap/data/subject_manifest.example.csv`

### Task 3: Add the baseline training/eval code
- Add `projects/bruxism-cap/src/train_baseline.py`
- Add `projects/bruxism-cap/src/eval.py`

### Task 4: Wire the scaffold into the repo
- Add optional biosignal dependencies to `pyproject.toml`
- Mention the project in the root `README.md`
- Update the wiki with the new scaffold and why it exists

### Task 5: Verify the scaffold
- Run Python syntax checks over the new files
- Validate the notebook JSON
- Re-read the changed wiki/index/log entries
