from taipy.gui import Markdown
from data.cache import metadata, assets, tree_df, kpis, treemap_data

# DataFrame with id, parent, label, type, size_mb
tree_data = tree_df.to_dict("records")

tree_md = Markdown("pages/tree/tree.md")
