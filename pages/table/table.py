from taipy.gui import Markdown, State
from ...data.data import load_all

metadata, assets, tree_df, kpis, treemap_data = load_all()

# Table data
table_data = assets.copy() if assets is not None else None
columns = list(table_data.columns) if table_data is not None else []

# Selected asset + variant
selected_family = table_data.iloc[0]["asset_family"] if table_data is not None and not table_data.empty else ""
selected_variant = table_data.iloc[0]["variant_name"] if table_data is not None and not table_data.empty else ""

def on_select_row(state: State):
    """
    This callback can be wired to a table if you configure row selection.
    For now, we simply keep selected_family/selected_variant in sync if used.
    """
    # Placeholder – you can expand when you enable row selection
    pass

table_md = Markdown("pages/table/table.md")
