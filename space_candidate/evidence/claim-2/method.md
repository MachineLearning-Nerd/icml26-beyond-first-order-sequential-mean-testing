# Claim 2 method

The implementation simulates Bernoulli observations sequentially and evaluates the exact binary `KL_inf` at every integer time. It records the first crossing for both the theorem-supported growing boundary and the paper's practical constant-boundary comparator without pooling them. At every stop it records current and previous evidence and thresholds so the checker can verify the first-hit property.

The `b=log(1/alpha)` grid is fixed before the run and extends the paper's two levels geometrically. The 500,000-step guard is a fixed safety ceiling, not a formula-derived stopping horizon; evidence consists of the observed first-hit distributions. Seeds, gates, and controls are committed in `reproduction/config.json` and `claim_contract.json`.
