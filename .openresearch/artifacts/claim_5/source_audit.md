# Claim 5 source audit

Retrieved `https://ar5iv.labs.arxiv.org/html/2606.04520` with an explicit browser User-Agent on 2026-08-02. SHA-256: `cf1579a4827d3248d278fc782191e672b191676c10e338d0ecd3439b9884caa0`.

Section 5 states three studies. Experiment 1 fixes `m0=0.7`, uses Beta(3,2) and Bernoulli(0.6), and draws 5,000 independent samples at each `n` to test the fixed-sample `KL_inf` statistic. Experiment 2 fixes `m0=0.2`, uses Bernoulli(0.6), 5,000 paths, alpha in `{1e-4,1e-8}`, and compares both equation (7)'s growing boundary and equation (8)'s constant boundary. It reports better Gaussian agreement at smaller alpha, particularly with the practical constant boundary. Experiment 3 fixes `m0=0.5`, alpha `1e-4`, equation (8), and 3,000 with-replacement bootstrap paths from a normalized DSSAT crop-yield pool, using the empirical pool for the plug-in center and variance.

The supplied campaign wording incorrectly implies that Beta is a stopping-time experiment. This verifier preserves the paper's actual split.

The source names only `https://dssat.net`; it does not identify the crop, observations, file revision, pool, normalization, or bootstrap seed, and the paper source contains only the finished figure. Exact author-panel numerical reproduction is therefore impossible from released materials. The same protocol is independently rerun on observed maize `HWAM` values in the primary `DSSAT/dssat-csm-data` repository at commit `a4f95d3ef36f1358bdeb5db49d498d5db373ba7a`. This substitution is disclosed everywhere and is not represented as the hidden author pool.
