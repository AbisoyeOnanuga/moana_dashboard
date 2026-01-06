from taipy.gui import Markdown

from data.cache import (
    assets,
    treemap_data,
    treemap_df,
    hist_tri_df,
    hist_mat_df,
    hist_poly_df,
    scatter_poly_df,
    bar_df,
)
from pages.navbar import navbar


# --------------------------------------------------
# FILTER STATE + OPTIONS (selector currently disabled)
# --------------------------------------------------

# if assets is not None and not assets.empty:
#     family_options = ["All"] + sorted(assets["asset_family"].astype(str).unique())
# else:
#     family_options = ["All"]
#
# selected_family = "All"
#
# def on_family_change(state):
#     # Rebuild charts based on selected family
#     state.viz_state = compute_viz_state(state.selected_family)
#
# # This will hold all data/properties for the charts
# viz_state = {}


# --------------------------------------------------
# LAYOUT CONFIGS
# --------------------------------------------------

layout_log_y = {"yaxis": {"type": "log"}}
layout_log_x = {"xaxis": {"type": "log"}}


# --------------------------------------------------
# MULTI-TRACE HELPERS (kept for future selector reactivation)
# --------------------------------------------------

def build_datasets(df, x_col, y_col, text_col):
    """
    Build a list of datasets, one per asset family.
    Each dataset is a dict with x, y, text arrays.
    """
    datasets = []
    families = sorted(df["family"].unique())
    for fam in families:
        sub = df[df["family"] == fam]
        datasets.append({
            x_col: sub[x_col].tolist(),
            y_col: sub[y_col].tolist(),
            text_col: sub[text_col].tolist(),
        })
    return datasets, families


def build_properties(families, x_col, y_col, text_col, colors):
    """
    Build a Taipy 'properties' dict mapping datasets to traces.
    """
    props = {}
    for i, fam in enumerate(families):
        idx = i + 1
        props[f"x[{idx}]"] = f"{i}/{x_col}"
        props[f"y[{idx}]"] = f"{i}/{y_col}"
        props[f"text[{idx}]"] = f"{i}/{text_col}"
    props["name"] = families
    props["marker_color"] = colors[:len(families)]
    return props


# Moana-inspired palette (20 colors)
family_colors = [
    "#0B4F2E",  # Deep Forest Green
    "#3C8D40",  # Palm Leaf Green
    "#6CC551",  # Fern Bright Green
    "#8BAF5B",  # Moss Green
    "#4A2E1A",  # Dark Bark Brown
    "#7A4F2A",  # Coconut Husk Brown
    "#B89A6A",  # Driftwood Tan
    "#D9C7A3",  # Woven Fiber Beige
    "#3A3A3A",  # Basalt Dark Gray
    "#5A524C",  # Lava Rock Warm Gray
    "#7E756C",  # Cliffside Stone
    "#E8D7B8",  # Coral Sand
    "#F2E4C9",  # Warm Beach Sand
    "#0A3D62",  # Deep Ocean Blue
    "#1E6F78",  # Lagoon Teal
    "#4FB3BF",  # Shallow Water Aqua
    "#7EC8E3",  # Tropical Sky Blue
    "#F4F4F2",  # Cloud Soft White
    "#D64550",  # Hibiscus Red
    "#F4D35E",  # Plumeria Yellow
]


# --------------------------------------------------
# DERIVED STATE: DATA + PROPERTIES PER CHART
# (we compute only the "All" case once, no selector)
# --------------------------------------------------

def compute_viz_state(selected_family_value: str):
    """
    Build data+properties for all charts, possibly filtered by family.
    Returns a dict:
      tri_data, tri_props, mat_data, mat_props, poly_data, poly_props, scatter_data, scatter_props
    """
    state = {}

    # ----- TRIANGLES -----
    if selected_family_value == "All":
        tri_source = hist_tri_df
    else:
        tri_source = hist_tri_df[hist_tri_df["family"] == selected_family_value]

    tri_data, tri_families = build_datasets(tri_source, "variant", "value", "hover")
    tri_props = build_properties(tri_families, "variant", "value", "hover", family_colors)
    state["tri_data"] = tri_data
    state["tri_props"] = tri_props

    # ----- MATERIALS -----
    if selected_family_value == "All":
        mat_source = hist_mat_df
    else:
        mat_source = hist_mat_df[hist_mat_df["family"] == selected_family_value]

    mat_data, mat_families = build_datasets(mat_source, "variant", "value", "hover")
    mat_props = build_properties(mat_families, "variant", "value", "hover", family_colors)
    state["mat_data"] = mat_data
    state["mat_props"] = mat_props

    # ----- POLYCOUNT -----
    if selected_family_value == "All":
        poly_source = hist_poly_df
    else:
        poly_source = hist_poly_df[hist_poly_df["family"] == selected_family_value]

    poly_data, poly_families = build_datasets(poly_source, "variant", "value", "hover")
    poly_props = build_properties(poly_families, "variant", "value", "hover", family_colors)
    state["poly_data"] = poly_data
    state["poly_props"] = poly_props

    # ----- SCATTER (POLYCOUNT vs MATERIALS) -----
    if selected_family_value == "All":
        scatter_source = scatter_poly_df
    else:
        scatter_source = scatter_poly_df[scatter_poly_df["family"] == selected_family_value]

    scatter_data, scatter_families = build_datasets(scatter_source, "polycount", "materials", "hover")
    scatter_props = build_properties(scatter_families, "polycount", "materials", "hover", family_colors)
    state["scatter_data"] = scatter_data
    state["scatter_props"] = scatter_props

    return state


# Compute the "All families" multi-trace data once, at import
_viz_all = compute_viz_state("All")

tri_data = _viz_all["tri_data"]
tri_props = _viz_all["tri_props"]

mat_data = _viz_all["mat_data"]
mat_props = _viz_all["mat_props"]

poly_data = _viz_all["poly_data"]
poly_props = _viz_all["poly_props"]

scatter_data = _viz_all["scatter_data"]
scatter_props = _viz_all["scatter_props"]


# --------------------------------------------------
# Load Markdown LAST
# --------------------------------------------------

visualization_md = Markdown("pages/visualization/visualization.md")
