from taipy.gui import Markdown
from data.data import load_all

metadata, assets, tree_df, kpis, treemap_data = load_all()

# Treemap data
labels = treemap_data["labels"]
parents = treemap_data["parents"]
values = treemap_data["values"]

# Example: polycount vs material_count chart
if assets is not None and not assets.empty:
    scatter_x = list(assets["polycount"])
    scatter_y = list(assets["material_count"])
    scatter_text = list(assets["variant_name"])
else:
    scatter_x = scatter_y = scatter_text = []

visualization_md = Markdown("pages/visualization/visualization.md")
