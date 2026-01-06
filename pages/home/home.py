from taipy.gui import Markdown
from data.cache import metadata, assets, tree_df, kpis, treemap_data
from pages.navbar import navbar

total_assets = kpis["total_assets"]
total_variants = kpis["total_variants"]
total_props = sum(1 for fam in assets["asset_family"] if fam not in ["character", "environment"])
total_cameras = kpis["total_cameras"]
total_materials = kpis["total_materials"]

home_md = Markdown("pages/home/home.md")
