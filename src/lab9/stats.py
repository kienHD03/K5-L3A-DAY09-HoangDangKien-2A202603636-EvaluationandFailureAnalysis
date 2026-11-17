"""Statistics students implement (M2 judge calibration, M4 paired bootstrap).

Rules: a judge is a classifier -- measure it like one. A higher mean is not
"better" until the paired CI of the difference excludes 0.
Reference values to self-check are in tests/test_lab9_stats.py.
"""

from __future__ import annotations

from collections.abc import Sequence

POS = "FAIL"   # the judge's job is to FIND failures, so FAIL is the positive class


def confusion(human: Sequence[str], judge: Sequence[str]) -> dict[str, int]:
    """tp/fp/fn/tn with FAIL as positive."""
    tp = sum(h == "FAIL" and j == "FAIL" for h, j in zip(human, judge))
    fp = sum(h == "PASS" and j == "FAIL" for h, j in zip(human, judge))
    fn = sum(h == "FAIL" and j == "PASS" for h, j in zip(human, judge))
    tn = sum(h == "PASS" and j == "PASS" for h, j in zip(human, judge))
    return {"tp": tp, "fp": fp, "fn": fn, "tn": tn}


def precision_recall(human: Sequence[str], judge: Sequence[str]) -> tuple[float, float]:
    cm = confusion(human, judge)
    p = cm["tp"] / (cm["tp"] + cm["fp"]) if (cm["tp"] + cm["fp"]) else 0.0
    r = cm["tp"] / (cm["tp"] + cm["fn"]) if (cm["tp"] + cm["fn"]) else 0.0
    return p, r


def cohen_kappa(human: Sequence[str], judge: Sequence[str]) -> float:
    """kappa = (p_o - p_e) / (1 - p_e). Raise ValueError when undefined (p_e == 1):
    a constant judge has no signal and must FAIL calibration, not pass on a technicality."""
    cm = confusion(human, judge)
    n = sum(cm.values())
    p_o = (cm["tp"] + cm["tn"]) / n
    p_pos = ((cm["tp"] + cm["fp"]) * (cm["tp"] + cm["fn"])) / (n * n)
    p_neg = ((cm["tn"] + cm["fn"]) * (cm["tn"] + cm["fp"])) / (n * n)
    p_e = p_pos + p_neg
    if p_e == 1:
        raise ValueError("kappa undefined: constant judge")
    return (p_o - p_e) / (1 - p_e)


def rogan_gladen(observed_rate: float, sensitivity: float, specificity: float) -> float:
    """Correct an observed failure rate for judge error; clip to [0, 1]."""
    denom = sensitivity + specificity - 1
    if denom == 0:
        return 0.0
    val = (observed_rate + specificity - 1) / denom
    return max(0.0, min(1.0, val))


def paired_bootstrap(a: Sequence[float], b: Sequence[float], *, n_resamples: int = 1000,
                     rng: int = 2027, confidence: float = 0.95) -> tuple[float, float, float]:
    """a[i], b[i] = per-item mean over seeds, SAME items, SAME order.
    Return (mean(a)-mean(b), lo, hi) with scipy.stats.bootstrap(paired=True, method="percentile",
    rng=numpy.random.default_rng(rng)). If a == b everywhere return (0.0, 0.0, 0.0)."""
    import numpy as np
    from scipy import stats as sp_stats
    a, b = list(a), list(b)
    if a == b:
        return (0.0, 0.0, 0.0)
    diff = np.array(a) - np.array(b)
    d = float(diff.mean())
    res = sp_stats.bootstrap(
        (diff,),
        np.mean,
        n_resamples=n_resamples,
        method="percentile",
        confidence_level=confidence,
        random_state=np.random.default_rng(rng),
        paired=True,
    )
    lo, hi = float(res.confidence_interval.low), float(res.confidence_interval.high)
    return (d, lo, hi)


def pass_at_k(n: int, c: int, k: int) -> float:
    """Probability that AT LEAST ONE of k trials drawn from n (c of them passing) passes.
    Unbiased estimator (Chen et al. 2021): 1 - C(n-c, k) / C(n, k). Raise ValueError if k > n."""
    import math
    if k <= 0 or k > n or c < 0 or c > n:
        raise ValueError(f"Invalid args: n={n}, c={c}, k={k}")
    if n - c < k:
        return 1.0
    return 1.0 - math.comb(n - c, k) / math.comb(n, k)


def pass_hat_k(n: int, c: int, k: int) -> float:
    """pass^k (tau-bench, Yao et al. 2024): probability that ALL k trials drawn from n pass.
    Unbiased estimator: C(c, k) / C(n, k). Raise ValueError if k > n.
    pass^k <= pass@1 <= pass@k; a reliable agent keeps pass^k close to pass@1."""
    import math
    if k <= 0 or k > n or c < 0 or c > n:
        raise ValueError(f"Invalid args: n={n}, c={c}, k={k}")
    if c < k:
        return 0.0
    return math.comb(c, k) / math.comb(n, k)
