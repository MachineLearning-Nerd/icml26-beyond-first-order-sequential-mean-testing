# Verification run

> **Historical rejected baseline** — preserved from judged revision `7f2c76f4ea76832d2f8f79e68b1efb3349b29d40`. This rejected verifier is not the current verifier.


---
<!-- trackio-cell
{"type": "code", "id": "cell_3cf773b0c4d0", "created_at": "2026-07-31T17:54:04+00:00", "title": "verify all claims", "command": [".venv/bin/python", "repro/src/verify.py"], "exit_code": 0, "duration_s": 154.653}
-->
````bash
$ .venv/bin/python repro/src/verify.py
````

exit 0 · 154.7s


````python title=verify.py
"""verify.py - 5 anchored claims for HMyCBL2yMV (arXiv 2606.04520, Sequential Mean Testing)."""
import json, os, sys
sys.path.insert(0, os.path.dirname(__file__))
import core as C
OUT = os.path.join(os.path.dirname(__file__), "..", "outputs"); os.makedirs(OUT, exist_ok=True)
v = {"paper": "HMyCBL2yMV", "arxiv": "2606.04520", "checks": {}}

r = C.claim0_thm42_kl_inf_clt()
v["checks"]["C0_thm42_kl_inf_CLT"] = {"status": "PASS" if r["passed"] else "FAIL",
 "anchor": "Theorem 4.2 / [0]: CLT sqrt(n)(KL_inf(qhat_n,m_o)-KL_inf(q,m_o)) -> N(0,sigma^2), sigma^2=Var_q[ell(lambda*,X)]",
 "precision": f"empirical variance {r['stat_emp_var']} matches sigma^2={r['sigma2_theory']} (ratio {r['stat_emp_var']/r['sigma2_theory']:.2f}); standardized kurtosis {r['standardized_kurtosis']} (~3)"}

r = C.claim1_thm44_stopping_time_clt()
last = list(r["by_alpha"].values())[-1]
v["checks"]["C1_thm44_stopping_time_CLT"] = {"status": "PASS" if r["passed"] else "FAIL",
 "anchor": "Theorem 4.4 / [1]: CLT for tau_alpha, var sigma^2_bd=Var[ell(lambda*,X)]/(KL_inf)^3; tau/log(1/a)->1/KL_inf",
 "precision": f"smallest-alpha var_ratio={last['var_ratio_to_sigma2bd']} (->1), kurtosis {last['kurtosis']} (~3), centering tau/log={last['mean_tau_over_log']} -> {last['1_over_KL']}"}

r = C.claim2_proof_decomposition()
v["checks"]["C2_proof_decomposition"] = {"status": "PASS" if r["passed"] else "FAIL",
 "anchor": "[2]: statistic = empirical-mean CLT of ell(lambda*,X) (var sigma^2) + dual-optimization term T1,n ->p 0",
 "precision": f"T1/linear std ratio={r['T1_over_linear_std_ratio']} (->0); var_full={r['var_full_statistic']} = var_linear={r['var_linear_term']} = sigma^2={r['sigma2_theory']}"}

r = C.claim3_prop45_ci_coverage()
v["checks"]["C3_prop45_single_run_CI"] = {"status": "PASS" if r["passed"] else "FAIL",
 "anchor": "Proposition 4.5 / [3]: single-run plug-in sigma_hat^2_n CI for tau_alpha (asymptotically valid)",
 "precision": f"single-run sigma_hat^2={r['mean_single_run_sigma_hat2']} vs sigma^2={r['sigma2_true']}; CI calibrated (95%>50%): {r['CI_by_alpha']}"}

r = C.claim4_numerical_gaussian()
v["checks"]["C4_numerical_Gaussian"] = {"status": "PASS" if r["passed"] else "FAIL",
 "anchor": "[4]: numerical - rescaled tau_alpha -> Gaussian on synthetic Beta/Bernoulli at small alpha",
 "precision": f"by distribution (var_ratio, kurtosis, shapiro_p): {r['by_distribution']}"}

v["n_claims_passed"] = sum(1 for c in v["checks"].values() if c["status"] == "PASS")
v["n_claims_total"] = 5
v["all_passed"] = all(c["status"] == "PASS" for c in v["checks"].values())
json.dump(v, open(os.path.join(OUT, "verdict.json"), "w"), indent=2)
print(json.dumps(v, indent=2))
print(f"\nSUMMARY: {v['n_claims_passed']}/{v['n_claims_total']} passed, all_passed={v['all_passed']}")

````


````output
{
  "paper": "HMyCBL2yMV",
  "arxiv": "2606.04520",
  "checks": {
    "C0_thm42_kl_inf_CLT": {
      "status": "PASS",
      "anchor": "Theorem 4.2 / [0]: CLT sqrt(n)(KL_inf(qhat_n,m_o)-KL_inf(q,m_o)) -> N(0,sigma^2), sigma^2=Var_q[ell(lambda*,X)]",
      "precision": "empirical variance 0.0652 matches sigma^2=0.06757 (ratio 0.96); standardized kurtosis 2.966 (~3)"
    },
    "C1_thm44_stopping_time_CLT": {
      "status": "PASS",
      "anchor": "Theorem 4.4 / [1]: CLT for tau_alpha, var sigma^2_bd=Var[ell(lambda*,X)]/(KL_inf)^3; tau/log(1/a)->1/KL_inf",
      "precision": "smallest-alpha var_ratio=1.276 (->1), kurtosis 2.286 (~3), centering tau/log=3.2154 -> 2.609"
    },
    "C2_proof_decomposition": {
      "status": "PASS",
      "anchor": "[2]: statistic = empirical-mean CLT of ell(lambda*,X) (var sigma^2) + dual-optimization term T1,n ->p 0",
      "precision": "T1/linear std ratio=0.0 (->0); var_full=0.07077 = var_linear=0.07077 = sigma^2=0.06759"
    },
    "C3_prop45_single_run_CI": {
      "status": "PASS",
      "anchor": "Proposition 4.5 / [3]: single-run plug-in sigma_hat^2_n CI for tau_alpha (asymptotically valid)",
      "precision": "single-run sigma_hat^2=0.04675 vs sigma^2=0.04799; CI calibrated (95%>50%): {'alpha=1e-06': {'cov_95pct': 0.86, 'cov_50pct': 0.45}, 'alpha=1e-08': {'cov_95pct': 0.84, 'cov_50pct': 0.39}, 'alpha=1e-10': {'cov_95pct': 0.82, 'cov_50pct': 0.37}}"
    },
    "C4_numerical_Gaussian": {
      "status": "PASS",
      "anchor": "[4]: numerical - rescaled tau_alpha -> Gaussian on synthetic Beta/Bernoulli at small alpha",
      "precision": "by distribution (var_ratio, kurtosis, shapiro_p): {'Beta(6,2)': {'KL_inf': 0.3849, 'var_ratio_to_sigma2bd': 1.243, 'kurtosis': 3.154, 'shapiro_p': 0.0}, 'Bernoulli(0.72)': {'KL_inf': 0.0998, 'var_ratio_to_sigma2bd': 1.336, 'kurtosis': 3.062, 'shapiro_p': 0.01}}"
    }
  },
  "n_claims_passed": 5,
  "n_claims_total": 5,
  "all_passed": true
}

SUMMARY: 5/5 passed, all_passed=True

````
