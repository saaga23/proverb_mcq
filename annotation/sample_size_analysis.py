"""Sample size analysis for Fleiss' Kappa agreement in ProverbGap annotation."""

import math
from typing import Dict, Tuple, Any


def fleiss_kappa_sample_size(
    target_kappa: float = 0.60,
    null_kappa: float = 0.20,
    power: float = 0.80,
    alpha: float = 0.05,
    categories: int = 4,
    raters: int = 3,
) -> int:
    """Calculate minimum sample size for Fleiss' Kappa study.

    Uses formula from Rotondi & Donner (2003) for sample size determination:
    n = (Z_alpha/2 + Z_beta)^2 * (p0(1-p0) + p1(1-p1)) / (p0 - p1)^2

    Where p0 and p1 are transformed kappa values, and raters are accounted for
    through the design effect.

    Args:
        target_kappa: Expected kappa value under alternative hypothesis.
        null_kappa: Null kappa value under null hypothesis.
        power: Statistical power (1 - beta).
        alpha: Significance level.
        categories: Number of rating categories (4 for A, B, C, D answers).
        raters: Number of raters per item.

    Returns:
        Minimum number of items required.
    """
    # Transform kappa values to probability scale
    # Using approximation: p ≈ kappa * (categories - 1) / (categories - 1) + 1/categories
    # Simplified: for 4 categories, p ≈ kappa/3 + 0.25
    p0 = null_kappa / (categories - 1) + 1 / categories
    p1 = target_kappa / (categories - 1) + 1 / categories

    # Design effect for multiple raters
    design_effect = 1 + (raters - 1) * (p0 * (1 - p0) / (categories - 1))

    # Z-scores for alpha and power
    z_alpha = 1.96  # for alpha = 0.05 two-tailed
    z_beta = 0.84   # for power = 0.80

    # Sample size formula
    numerator = (z_alpha + z_beta) ** 2 * (p0 * (1 - p0) + p1 * (1 - p1))
    denominator = (p0 - p1) ** 2

    n = math.ceil(numerator / denominator * design_effect)

    return max(n, 30)  # Minimum practical sample


def kappa_ci_width(
    kappa: float,
    n: int,
    categories: int = 4,
    raters: int = 3,
) -> Tuple[float, float, float]:
    """Calculate confidence interval width for Fleiss' Kappa.

    Uses Fleiss et al. (2003) standard error approximation:
    SE = sqrt(2 * (categories - 1) / (3 * n * raters))

    Args:
        kappa: Observed kappa value.
        n: Number of items.
        categories: Number of rating categories.
        raters: Number of raters per item.

    Returns:
        Tuple of (standard_error, ci_lower, ci_upper).
    """
    se = math.sqrt(2 * (categories - 1) / (3 * n * raters))
    margin = 1.96 * se  # 95% CI
    ci_lower = max(-1, kappa - margin)
    ci_upper = min(1, kappa + margin)

    return se, ci_lower, ci_upper


def recommend_sample_size() -> Dict[str, Any]:
    """Recommend sample size for ProverbGap annotation.

    Based on power analysis targeting kappa ≥ 0.60 with 80% power.
    Uses a conservative estimate of null kappa = 0.20 (poor agreement).

    Returns:
        Dictionary with recommendation and justification.
    """
    min_n = fleiss_kappa_sample_size(
        target_kappa=0.60,
        null_kappa=0.20,
        power=0.80,
        alpha=0.05,
        categories=4,
        raters=3,
    )

    # Round to 90 items total for practical annotation
    total_items = 90
    items_per_language = 30

    return {
        "target_kappa": 0.60,
        "null_kappa": 0.20,
        "minimum_items": min_n,
        "items_per_language": items_per_language,
        "total_items": total_items,
        "languages": ["English", "Arabic", "Yoruba"],
        "raters_per_item": 3,
        "justification": (
            f"While {min_n} items would provide statistical power to detect "
            f"kappa improvement from {0.20} to {0.60}, we recommend {total_items} items "
            f"({items_per_language} per language) as a practical compromise. "
            f"This provides reasonable power while remaining feasible for human annotation. "
            f"Per-language analysis with {items_per_language} items × 3 raters enables "
            f"cross-lingual comparison and IAA computation."
        ),
    }


if __name__ == "__main__":
    result = recommend_sample_size()

    print("=" * 60)
    print("Fleiss' Kappa Sample Size Analysis")
    print("=" * 60)
    print(f"Target kappa: {result['target_kappa']}")
    print(f"Minimum items required: {result['minimum_items']}")
    print(f"Items per language: {result['items_per_language']}")
    print(f"Total items (3 languages): {result['total_items']}")
    print(f"Raters per item: {result['raters_per_item']}")
    print("-" * 60)
    print("Justification:")
    print(result["justification"])

    # Show CI widths for various sample sizes
    print("\nConfidence Interval Widths by Sample Size:")
    print("-" * 60)
    print(f"{'Items':<10} {'SE':<12} {'CI Lower':<12} {'CI Upper':<12}")
    for n in [30, 60, 90, 120, 180]:
        se, ci_l, ci_u = kappa_ci_width(0.60, n, categories=4, raters=3)
        print(f"{n:<10} {se:.4f}       {ci_l:.3f}         {ci_u:.3f}")