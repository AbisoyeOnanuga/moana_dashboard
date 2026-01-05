import pandas as pd


def apply_filters(
    df: pd.DataFrame,
    asset_type: str,
    poly_range: tuple[int, int],
    file_range: tuple[int, int],
    scene_filter: str,
    heavy_only: bool,
) -> pd.DataFrame:
    """
    Apply all filters to the base dataframe and return a new filtered dataframe.
    """
    result = df.copy()

    # Scene filter
    if scene_filter != "All":
        result = result[result["scene_name"] == scene_filter]

    # Asset type
    if asset_type != "All":
        result = result[result["asset_type"] == asset_type]

    # Poly range
    poly_min, poly_max = poly_range
    result = result[result["poly_count"].between(poly_min, poly_max)]

    # File size range
    file_min, file_max = file_range
    result = result[result["file_size_mb"].fillna(0).between(file_min, file_max)]

    # Heavy only
    if heavy_only:
        # You can tune this threshold
        result = result[result["poly_count"] > 500_000]

    return result


def compute_suggestions(df: pd.DataFrame) -> list[str]:
    """
    Generate simple, readable optimization suggestions based on the current filtered set.
    """
    if df.empty:
        return []

    suggestions: list[str] = []

    avg_poly = df["poly_count"].mean()
    max_poly = df["poly_count"].max()
    total_mb = df["file_size_mb"].sum()

    if max_poly > 1_000_000:
        heavy_assets = df[df["poly_count"] > 1_000_000]["asset_name"].tolist()
        suggestions.append(
            f"{len(heavy_assets)} assets exceed 1M polys. Consider LODs or decimation for: {', '.join(heavy_assets[:5])}..."
        )

    if total_mb > 5000:
        suggestions.append(
            f"Total file size is {total_mb:.1f} MB. Consider compressing or removing unused assets."
        )

    if avg_poly > 300_000:
        suggestions.append(
            f"Average poly count per asset is {avg_poly:,.0f}. Review topology or proxy workflows."
        )

    if not suggestions:
        suggestions.append("Current selection looks reasonable. No major issues detected.")

    return suggestions
