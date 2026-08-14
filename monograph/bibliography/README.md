# Resonant Chemistry bibliography policy

`monograph/bibliography/*.bib` is the live modular project bibliography used by
the working textbook.

Current modules:

- `references.bib` — active/current source ledger;
- `compound_legacy.bib` — provenance backfilled from compound gates that
  predated the live bibliography invariant;
- `molecular_screening.bib` — molecular-method and software sources introduced
  by the v0.14 common relaxation-screen trajectory.

The monograph must wire every `.bib` module, and
`scripts/audit_compound_bibliography.py` treats the directory as one logical
ledger.

Operational rule from the compound-relation track onward:

1. If a paper is used to motivate a gate, constrain a method, label a benchmark,
   provide a falsifier, or support a structural/energetic statement, add its
   bibliographic record in the **same development iteration**.
2. Prefer primary literature for technical claims. Reviews may be added for
   orientation but must not replace the primary source behind a validation
   label when the primary source is available.
3. A bibliography entry records provenance; it does **not** promote the cited
   claim to validated Resonant Chemistry canon.
4. Benchmark JSON files should use a stable bibliography key and DOI whenever
   possible.
5. Motivating/preknown sources must be labelled separately from blind or
   post-preregistered validation sources.
6. Falsifying sources remain in the bibliography and prediction ledger; do not
   delete a candidate merely because later evidence is negative.
7. Missing literature is never by itself a negative chemical-existence label.
8. Duplicate BibTeX keys or DOI records across modules are CI failures.
9. A DOI referenced by the active compound benchmarks/docs but missing from the
   live bibliography is a CI failure.
10. A `.bib` module present under `monograph/bibliography/` but not wired into
    `monograph/main.tex` is a CI failure.

The working monograph currently uses `\nocite{*}` so the live source ledger is
visible in the compiled PDF even before every new development note has been
converted into a dedicated textbook chapter with inline `\cite{...}` calls.

CI gates:

- `.github/workflows/compound-relations-ci.yml` runs full Python test discovery,
  benchmark JSON parsing, the DOI/key/wiring audit, and branch-surface checks;
- `.github/workflows/bibliography-ci.yml` compiles the monograph through
  LaTeX/BibTeX and rejects unresolved citations/references.
