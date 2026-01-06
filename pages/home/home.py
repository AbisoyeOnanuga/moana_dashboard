from taipy.gui import Markdown
from data.cache import metadata, assets, tree_df, kpis, treemap_data
from pages.navbar import navbar

total_assets = kpis["total_assets"]
total_variants = kpis["total_variants"]
total_characters = kpis["total_characters"]
total_props = sum(1 for fam in assets["asset_family"] if fam not in ["character", "environment"])
total_environments = sum(1 for fam in assets["asset_family"] if fam in ["environment"])
total_materials = kpis["total_materials"]

home_md = Markdown("pages/home/home.md")
