#from taipy import gui as ui
from taipy.gui import Gui as ui

# ---------------------------------------------------------
# Asset Table (Grouped by Scene)
# ---------------------------------------------------------


def asset_table_grouped(df):
    """
    Returns a list of UI expanders, one per scene_name.
    Each expander contains a sortable table of assets.
    """
    blocks = ""

    for scene, group_df in df.groupby("scene_name"):
        blocks += f"""
<|{scene}|expandable|>
<|{group_df}|table|height=300px|>
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
    return f"""
    <|layout|columns=1|gap=10px|>

    **Asset Type**  
    <|{state.asset_type}|selector|lov={['All'] + sorted(df['asset_type'].unique().tolist())}|on_change=asset_type|>

    **Poly Count Range**  
    <|{state.poly_min}|slider|min=0|max={int(df['poly_count'].max())}|on_change=poly_min|>  
    <|{state.poly_max}|slider|min=0|max={int(df['poly_count'].max())}|on_change=poly_max|>

    **File Size (MB)**  
    <|{state.file_min}|slider|min=0|max={int(df['file_size_mb'].max())}|on_change=file_min|>  
    <|{state.file_max}|slider|min=0|max={int(df['file_size_mb'].max())}|on_change=file_max|>

    **Scene Filter**  
    <|{state.scene_filter}|selector|lov={['All'] + sorted(df['scene_name'].unique().tolist())}|on_change=scene_filter|>

    **Heavy Only**  
    <|{state.heavy_only}|toggle|on_change=heavy_only|>

    </|layout|>
"""



# ---------------------------------------------------------
# Suggestions Panel
# ---------------------------------------------------------

def suggestions_panel(suggestions):     
    """
    Display optimization suggestions as a list.
    """
    return f""" 
    <|Optimization Suggestions|expandable|>
    <|{suggestions}|list|>
"""
