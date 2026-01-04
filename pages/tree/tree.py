from taipy.gui import Markdown
from ...data.data import load_all

metadata, assets, tree_df, kpis, treemap_data = load_all()

# DataFrame with id, parent, label, type, size_mb
tree_data = tree_df

tree_md = Markdown("pages/tree/tree.md")
