from taipy.gui import Markdown, State
from data.cache import metadata, assets, tree_df, kpis, treemap_data

# Build the list of variants for the selector
if assets is not None and not assets.empty:
    variants = list(assets["variant_name"])
    selected_variant = variants[0]
else:
    variants = []
    selected_variant = ""

# Derived detail fields
def get_asset_detail(variant_name: str):
    if assets is None or assets.empty or not variant_name:
        return {
            "asset_family": "",
            "polycount": 0,
            "triangles": 0,
            "material_count": 0,
            "hierarchy_depth": 0,
            "folder_size_mb": 0.0,
            "asset_path": "",
        }

    row = assets.loc[assets["variant_name"] == variant_name]
    if row.empty:
        return {
            "asset_family": "",
            "polycount": 0,
            "triangles": 0,
            "material_count": 0,
            "hierarchy_depth": 0,
            "folder_size_mb": 0.0,
            "asset_path": "",
        }

    row = row.iloc[0]
    return {
        "asset_family": row["asset_family"],
        "polycount": row["polycount_fmt"],
        "triangles": row["triangles_fmt"],
        "material_count": row["material_count_fmt"],
        "hierarchy_depth": row["hierarchy_depth_fmt"],
        "folder_size_mb": row["folder_size_fmt"],
        "asset_path": row["asset_path"],
    }

detail_state = get_asset_detail(selected_variant)

def on_change_variant(state: State):
    state.detail_state = get_asset_detail(state.selected_variant)

detail_md = Markdown("pages/detail/detail.md")
