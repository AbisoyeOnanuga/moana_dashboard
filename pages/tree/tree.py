from taipy.gui import Markdown
from data.cache import metadata, assets, tree_df, kpis, treemap_data

# DataFrame with id, parent, label, type, size_mb
tree_data = tree_df.to_dict("records")

# --------------------------------------------------
# CLEAN TREE DATAFRAME
# --------------------------------------------------

def format_size_mb(mb):
    if mb >= 1024:
        return f"{mb/1024:.2f} GB"
    if mb < 1:
        return f"{mb*1024:.2f} KB"
    return f"{mb:,.2f} MB"

tree_clean_df = tree_df.copy()

# Remove id and parent columns if present
for col in ["id", "parent"]:
    if col in tree_clean_df.columns:
        tree_clean_df = tree_clean_df.drop(columns=[col])

# Format size column
if "size_mb" in tree_clean_df.columns:
    tree_clean_df["size"] = tree_clean_df["size_mb"].apply(format_size_mb)
    tree_clean_df = tree_clean_df.drop(columns=["size_mb"])

tree_md = Markdown("pages/tree/tree.md")
