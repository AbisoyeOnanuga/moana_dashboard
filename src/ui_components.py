#from taipy import gui as ui
import os
from taipy.gui import Gui as ui

# ---------------------------------------------------------
# Asset Table (Grouped by Scene)
# ---------------------------------------------------------


def asset_table_grouped(df):
    """
    Returns Taipy markup: one expandable section per scene_name,
    each containing a compact, readable table.
    """

    blocks = ""

    for scene, group_df in df.groupby("scene_name"):
        # Work on a copy so we don't touch the original df
        view = group_df.copy()

        # Shorten file path
        if "file_path" in view.columns:
            view["file_name"] = view["file_path"].apply(lambda p: os.path.basename(str(p)))
            view["folder"] = view["file_path"].apply(
                lambda p: os.path.basename(os.path.dirname(str(p)))
            )

        # Only show readable columns
        cols = ["asset_name", "asset_type", "poly_count", "file_size_mb", "file_name", "folder"]
        cols = [c for c in cols if c in view.columns]
        view = view[cols]

        blocks += f"""
<|{scene}|expandable|collapsed=True|>
<|{view}|table|height=300px|>
"""

    return blocks



# ---------------------------------------------------------
# Treemap Visualizer (File Size)
# ---------------------------------------------------------

def file_size_treemap(df):    
    """
    Treemap-like visualization for file sizes.
    Size = file_size_mb
    Color = poly_count
    """
    df2 = df.dropna(subset=["file_size_mb"])
    if df2.empty:
        return "No file size data available."

    return f"""
<|{df2}|chart|type=treemap|values=file_size_mb|labels=asset_name|color=poly_count|height=500px|>
"""


# ---------------------------------------------------------
# Filters Panel
# ---------------------------------------------------------

def filters_panel(state, df):
    """
    UI panel for filtering assets.
        State should contain:
        state.asset_type
        state.poly_min
        state.poly_max
        state.file_min
        state.file_max
        state.scene_filter
        state.heavy_only
    """
    asset_types = ['All'] + sorted(df['asset_type'].dropna().unique().tolist())
    scenes = ['All'] + sorted(df['scene_name'].dropna().unique().tolist())

    return f"""
<|layout|columns=1|gap=12px|>

**Asset Type**  
<|{state.asset_type}|selector|lov={asset_types}|on_change=asset_type|>

**Poly Count Min**  
<|{state.poly_min}|slider|min=0|max={int(df['poly_count'].max())}|on_change=poly_min|>

**Poly Count Max**  
<|{state.poly_max}|slider|min=0|max={int(df['poly_count'].max())}|on_change=poly_max|>

**File Size Min (MB)**  
<|{state.file_min}|slider|min=0|max={int(df['file_size_mb'].max())}|on_change=file_min|>

**File Size Max (MB)**  
<|{state.file_max}|slider|min=0|max={int(df['file_size_mb'].max())}|on_change=file_max|>

**Scene Filter**  
<|{state.scene_filter}|selector|lov={scenes}|on_change=scene_filter|>

**Heavy Only**  
<|{state.heavy_only}|toggle|on_change=heavy_only|>

</|layout|>
"""


# ---------------------------------------------------------
# Suggestions Panel
# ---------------------------------------------------------

def suggestions_panel(suggestions):
    if not suggestions:
        return "No optimization suggestions for the current filters."
    
    items = "\n".join(f"- {s}" for s in suggestions)

    """
    Display optimization suggestions as a list.
    """
    return f""" 
<|Optimization Suggestions|expandable|>
{items}
"""
