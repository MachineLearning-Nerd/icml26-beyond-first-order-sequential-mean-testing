from __future__ import annotations

import math

import numpy as np
from scipy import integrate, optimize, stats


def ell(lam: float | np.ndarray, x: float | np.ndarray, m0: float) -> np.ndarray:
    return np.log1p(-np.asarray(lam) * (np.asarray(x) - m0))


def binary_kl(p: np.ndarray | float, m0: float) -> np.ndarray:
    p = np.asarray(p, dtype=float)
    with np.errstate(divide="ignore", invalid="ignore"):
        left = np.where(p == 0.0, 0.0, p * np.log(p / m0))
        right = np.where(p == 1.0, 0.0, (1.0 - p) * np.log((1.0 - p) / (1.0 - m0)))
    return left + right


def binary_reference(p: float, m0: float) -> dict[str, float]:
    kval = float(binary_kl(p, m0))
    lam = (m0 - p) / (m0 * (1.0 - m0))
    values = ell(lam, np.array([0.0, 1.0]), m0)
    mean = (1.0 - p) * values[0] + p * values[1]
    variance = (1.0 - p) * (values[0] - mean) ** 2 + p * (values[1] - mean) ** 2
    return {"klinf": kval, "lambda_star": float(lam), "sigma2": float(variance)}


def beta_reference(a: float, b: float, m0: float) -> dict[str, float]:
    mean = a / (a + b)
    if mean >= m0:
        raise ValueError("baseline Beta reference expects mean below m0")

    upper = np.nextafter(1.0 / (1.0 - m0), 0.0)

    def score(lam: float) -> float:
        value, _ = integrate.quad(
            lambda x: ((x - m0) / (1.0 - lam * (x - m0))) * stats.beta.pdf(x, a, b),
            0.0,
            1.0,
            epsabs=2e-13,
            epsrel=2e-13,
            limit=300,
        )
        return value

    lam = optimize.brentq(score, 0.0, upper, xtol=5e-15, rtol=5e-15)

    def moment(power: int) -> float:
        value, _ = integrate.quad(
            lambda x: math.log1p(-lam * (x - m0)) ** power * stats.beta.pdf(x, a, b),
            0.0,
            1.0,
            epsabs=2e-13,
            epsrel=2e-13,
            limit=300,
        )
        return value

    kval = moment(1)
    sigma2 = moment(2) - kval * kval
    return {"klinf": kval, "lambda_star": lam, "sigma2": sigma2, "score_residual": score(lam)}


def _plus_empirical(samples: np.ndarray, m0: float) -> np.ndarray:
    rows = samples.shape[0]
    result = np.zeros(rows, dtype=float)
    means = samples.mean(axis=1)
    active = means < m0 - 1e-14
    if not np.any(active):
        return result

    idx = np.flatnonzero(active)
    work = samples[idx]
    upper_exact = 1.0 / (1.0 - m0)
    upper = np.nextafter(upper_exact, 0.0)
    with np.errstate(divide="ignore"):
        phi = np.mean((1.0 - m0) / (1.0 - work), axis=1)
    boundary = phi <= 1.0 + 2e-13
    if np.any(boundary):
        boundary_idx = idx[boundary]
        result[boundary_idx] = np.mean(ell(upper_exact, samples[boundary_idx], m0), axis=1)

    interior_idx = idx[~boundary]
    if interior_idx.size == 0:
        return result

    for start in range(0, interior_idx.size, 256):
        target_idx = interior_idx[start : start + 256]
        block = samples[target_idx]
        block_means = means[target_idx]
        lo = np.zeros(block.shape[0])
        hi = np.full(block.shape[0], upper)
        lam = np.clip((m0 - block_means) / (m0 * (1.0 - m0)), lo, hi)
        bad = (lam <= lo) | (lam >= hi) | ~np.isfinite(lam)
        lam[bad] = 0.5 * (lo[bad] + hi[bad])

        for _ in range(60):
            delta = block - m0
            denominator = 1.0 - lam[:, None] * delta
            score = np.mean(delta / denominator, axis=1)
            derivative = np.mean((delta / denominator) ** 2, axis=1)
            hi = np.where(score > 0.0, lam, hi)
            lo = np.where(score <= 0.0, lam, lo)
            converged = (np.abs(score) <= 2e-11) | ((hi - lo) <= 2e-12 * (1.0 + np.abs(lam)))
            if np.all(converged):
                break
            proposal = lam - score / derivative
            invalid = (~np.isfinite(proposal)) | (proposal <= lo) | (proposal >= hi)
            proposal[invalid] = 0.5 * (lo[invalid] + hi[invalid])
            lam = proposal
        else:
            lam = 0.5 * (lo + hi)

        result[target_idx] = np.mean(ell(lam[:, None], block, m0), axis=1)
    return result


def empirical_klinf_batch(samples: np.ndarray, m0: float) -> np.ndarray:
    samples = np.asarray(samples, dtype=float)
    if samples.ndim != 2 or samples.shape[1] == 0:
        raise ValueError("samples must be a non-empty matrix")
    if np.any((samples < 0.0) | (samples > 1.0)):
        raise ValueError("samples must lie in [0,1]")

    means = samples.mean(axis=1)
    result = np.zeros(samples.shape[0])
    plus = means <= m0
    if np.any(plus):
        result[plus] = _plus_empirical(samples[plus], m0)
    if np.any(~plus):
        result[~plus] = _plus_empirical(1.0 - samples[~plus], 1.0 - m0)
    return result
