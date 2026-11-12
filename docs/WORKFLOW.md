# Git workflow (3 people, no conflicts)

## One-time
1. One person creates the repo on GitHub (private) and pushes this folder.
2. Settings -> Collaborators: add the other two.
3. Everyone clones it. Put the raw CSV in `data/raw/` (it is gitignored).

## Daily routine
```bash
git checkout main && git pull            # start from the latest
git checkout -b a/cleaning-missing       # branch name: a/ b/ c/ + topic
# ...work, run your script...
git add src/01_cleaning.py notes/A_cleaning_notes.md reports/figures
git commit -m "A: add missing-value check by state"
git push -u origin a/cleaning-missing
```
Then open a **Pull Request** on GitHub and ask one teammate to review (this is also how everyone learns the others' work). Merge into `main` after one approval.

## Rules
- Never commit data files, never push straight to `main`.
- Edit only your own files. Need a change in `common.py` or someone's script? Ask in the group or open a PR.
- If `01_cleaning.py` changes, A tells B and C so they re-run the pipeline (`./run_all.sh`).
- Small commits with clear messages ("B: add birth-season chart", not "update").

## If you get a merge conflict
Open the file, keep both sides' intended changes, delete the `<<<<`, `====`, `>>>>` markers, then `git add` and `git commit`. If unsure, ask the other person before resolving.
