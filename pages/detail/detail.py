from taipy.gui import Markdown, State
from ...data.data import load_all

metadata, assets, tree_df, kpis, treemap_data = load_all()

if assets is not None and not assets.empty:
    selected_variant = assets.iloc[0]["variant_name"]
else:
    selected_variant = ""

# Derived detail fields
def get_asset_detail(variant_name: str):
    if assets is None or assets.empty or not variant_name:
        return {
            "asset_family": "",
            "polycount": 0,
            "material_count": 0,
            "hierarchy_depth": 0,
            "folder_size_mb": 0.0,
            "obj_path": "",
        }

    row = assets.loc[assets["variant_name"] == variant_name]
    if row.empty:
        return {
            "asset_family": "",
            "polycount": 0,
            "material_count": 0,
            "hierarchy_depth": 0,
            "folder_size_mb": 0.0,
            "obj_path": "",
        }

    row = row.iloc[0]
    return {
        "asset_family": row["asset_family"],
        "polycount": int(row["polycount"]),
        "material_count": int(row["material_count"]),
        "hierarchy_depth": int(row["hierarchy_depth"]),
        "folder_size_mb": float(row["folder_size_mb"]),
        "obj_path": row["obj_path"],
    }

detail_state = get_asset_detail(selected_variant)

def on_change_variant(state: State):
    state.detail_state = get_asset_detail(state.selected_variant)

detail_md = Markdown("pages/detail/detail.md")
