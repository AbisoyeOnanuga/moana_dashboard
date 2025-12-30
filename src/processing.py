import pandas as pd
import numpy as np

# ---------------------------------------------------------
# Basic Filters
# ---------------------------------------------------------

def filter_by_type(df, asset_type):
    """
    Filter DataFrame by asset_type.
    If asset_type is None or 'All', return df unchanged.
    """
    if asset_type is None or asset_type == "All":
        return df
    return df[df["asset_type"] == asset_type]


def filter_by_poly(df, min_poly, max_poly):
    """
    Filter DataFrame by poly_count range.
    Handles NaN poly_count safely.
    """
    df2 = df.copy()
    df2 = df2[df2["poly_count"].fillna(0).between(min_poly, max_poly)]
    return df2


# ---------------------------------------------------------
# Ranking / Sorting
# ---------------------------------------------------------

def get_heaviest(df, n=10):
    """
    Return the top N assets by poly_count.
    Ignores rows with NaN poly_count.
    """
    df2 = df.dropna(subset=["poly_count"])
    df2 = df2.sort_values(by="poly_count", ascending=False)
    return df2.head(n)


# ---------------------------------------------------------
# Optimization Suggestions
# ---------------------------------------------------------

def compute_suggestions(df):
    """
    Generate simple rule-based optimization suggestions.
    Returns a list of strings.
    """
    suggestions = []

    if df.empty:
        return ["No assets match the current filters."]

    # Rule 1: High poly assets
    high_poly = df[df["poly_count"] > 500_000]
    if not high_poly.empty:
        suggestions.append(
            f"{len(high_poly)} assets exceed 500k polys — consider LODs or decimation."
        )

    # Rule 2: Very large files
    large_files = df[df["file_size_mb"] > 100]
    if not large_files.empty:
        suggestions.append(
            f"{len(large_files)} assets exceed 100 MB — consider compression or splitting."
        )

    # Rule 3: Extremely high instance counts
    heavy_instancing = df[df["instance_count"] > 100_000]
    if not heavy_instancing.empty:
        suggestions.append(
            f"{len(heavy_instancing)} assets have over 100k instances — verify if instancing is intentional."
        )

    # Rule 4: Missing geometry
    missing_geo = df[df["poly_count"].isna()]
    if not missing_geo.empty:
        suggestions.append(
            f"{len(missing_geo)} assets have no poly data — check for curves, archives, or missing OBJ files."
        )

    # Default fallback
    if not suggestions:
        suggestions.append("No major optimization issues detected.")

    return suggestions


# ---------------------------------------------------------
# Combined Filter Pipeline
# ---------------------------------------------------------

def apply_filters(df, asset_type="All", poly_range=(0, np.inf)):
    """
    Apply all filters in one step.
    Returns a filtered DataFrame.
    """
    min_poly, max_poly = poly_range

    df2 = filter_by_type(df, asset_type)
    df2 = filter_by_poly(df2, min_poly, max_poly)

    return df2
