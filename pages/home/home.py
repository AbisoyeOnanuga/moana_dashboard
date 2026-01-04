from taipy.gui import Markdown
from data.data import load_all

# Load once at import time (fine for dashboard)
metadata, assets, tree_df, kpis, treemap_data = load_all()

total_assets = kpis["total_assets"]
total_variants = kpis["total_variants"]
total_characters = kpis["total_characters"]
total_props = kpis["total_props"]
total_environments = kpis["total_environments"]
total_materials = kpis["total_materials"]

home_md = Markdown("pages/home/home.md")
