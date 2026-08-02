# Claim 3 source audit

- Source: https://ar5iv.labs.arxiv.org/html/2606.04520, retrieved 2026-08-01 with explicit User-Agent, SHA-256 `cf1579a4827d3248d278fc782191e672b191676c10e338d0ecd3439b9884caa0`.
- Exact decomposition: Section 4.1 equations (5) and (6), anchors `#S4.E5` and `#S4.E6`.
- Exact Anscombe statement: Lemma A.8, anchor `#A1.Thmtheorem8`: for every `epsilon>0` and `eta>0`, there are `delta in (0,1)` and `n0>=1` such that for every `n>=n0`, `P(max_{|k-n|<=n delta}|Y_k-Y_n|>epsilon)<eta`.
- The implemented `Y_n=sqrt(n)(KL_inf(qhat_n,m0)-KL_inf(q,m0))` is exactly the lemma's process.
- Bernoulli(0.6) at `m0=0.2` is in the bounded model, has mean unequal to `m0`, and satisfies Assumption 4.1 vacuously because of its endpoint atom.

The finite contract fixes `epsilon=0.35` and `eta=0.1`, searches only the declared delta/n grid, and does not replace the lemma's universal quantifiers.
