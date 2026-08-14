# Resonant Chemistry bibliography policy

`references.bib` is the live project bibliography used by the working textbook.

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

The working monograph currently uses `\nocite{*}` so the live source ledger is
visible in the compiled PDF even before every new development note has been
converted into a dedicated textbook chapter with inline `\cite{...}` calls.
