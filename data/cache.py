from data.data import load_all
import pandas as pd

# Load core data once
metadata, assets, tree_df, kpis, treemap_data = load_all()

# --------------------------------------------------
# PRECOMPUTED DATAFRAMES FOR VISUALIZATION
# --------------------------------------------------

# Treemap dataframe
labels = treemap_data["labels"]
parents = treemap_data["parents"]
values = treemap_data["values"]

treemap_df = pd.DataFrame({
    "labels": labels,
    "parents": parents,
    "values": values,
})

# Base histograms
hist_tri_df = pd.DataFrame({
    "variant": assets["variant_name"],
    "value": assets["triangles"],
    "hover": assets["variant_name"] + " — " + assets["triangles_fmt"] + " tris",
    "family": assets["asset_family"].astype(str),
})

hist_mat_df = pd.DataFrame({
    "variant": assets["variant_name"],
    "value": assets["material_count"],
    "hover": assets["variant_name"] + " — " + assets["material_count_fmt"] + " mats",
    "family": assets["asset_family"].astype(str),
})

hist_poly_df = pd.DataFrame({
    "variant": assets["variant_name"],
    "value": assets["polycount"],
    "hover": assets["variant_name"] + " — " + assets["polycount_fmt"] + " polys",
    "family": assets["asset_family"].astype(str),
})

# Scatter data
scatter_poly_df = pd.DataFrame({
    "polycount": assets["polycount"],
    "materials": assets["material_count"],
    "hover": assets["variant_name"]
             + " — " + assets["polycount_fmt"] + " polys"
             + " — " + assets["material_count_fmt"] + " mats",
    "family": assets["asset_family"].astype(str),
})

# Heaviest families
heaviest = (
    assets.groupby("asset_family")
    .agg({"folder_size_mb": "max"})
    .sort_values("folder_size_mb", ascending=False)
    .head(10)
    .reset_index()
)

bar_df = pd.DataFrame({
    "family": heaviest["asset_family"],
    "size": heaviest["folder_size_mb"],
    "hover": heaviest["asset_family"] + " — " +
             heaviest["folder_size_mb"].round(2).astype(str) + " MB"
})
