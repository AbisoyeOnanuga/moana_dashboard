# pages/visualization/visualization.py

from taipy.gui import Markdown
import pandas as pd
from data.cache import assets, treemap_data

# --------------------------------------------------
# TREEMAP DATA
# --------------------------------------------------
labels = treemap_data["labels"]
parents = treemap_data["parents"]
values = treemap_data["values"]

treemap_df = pd.DataFrame({
    "labels": labels,
    "parents": parents,
    "values": values,
})


# --------------------------------------------------
# HISTOGRAM DATA WITH HOVER LABELS
# --------------------------------------------------

# Triangle histogram
hist_tri_df = pd.DataFrame({
    "triangles": assets["triangles"],
    "variant": assets["variant_name"],
    "hover": assets["variant_name"] + " — " + assets["triangles_fmt"] + " tris"
})

# Material histogram
hist_mat_df = pd.DataFrame({
    "materials": assets["material_count"],
    "variant": assets["variant_name"],
    "hover": assets["variant_name"] + " — " + assets["material_count_fmt"] + " mats"
})

# Polycount histogram
hist_poly_df = pd.DataFrame({
    "polycount": assets["polycount"],
    "variant": assets["variant_name"],
    "hover": assets["variant_name"] + " — " + assets["polycount_fmt"] + " polys"
})


# --------------------------------------------------
# SCATTER PLOTS WITH HOVER LABELS
# --------------------------------------------------

scatter_poly_df = pd.DataFrame({
    "polycount": assets["polycount"],
    "materials": assets["material_count"],
    "variant": assets["variant_name"],
    "hover": assets["variant_name"]
             + " — " + assets["polycount_fmt"] + " polys"
             + " — " + assets["material_count_fmt"] + " mats"
})

scatter_tri_df = pd.DataFrame({
    "triangles": assets["triangles"],
    "materials": assets["material_count"],
    "variant": assets["variant_name"],
    "hover": assets["variant_name"]
             + " — " + assets["triangles_fmt"] + " tris"
             + " — " + assets["material_count_fmt"] + " mats"
})


# --------------------------------------------------
# BAR CHART (heaviest families)
# --------------------------------------------------

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


# --------------------------------------------------
# Load Markdown LAST
# --------------------------------------------------
visualization_md = Markdown("pages/visualization/visualization.md")
