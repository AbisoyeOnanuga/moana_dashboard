from taipy.gui import Gui
import math

# ---------------------------------------------------------
# Your existing project utilities
# ---------------------------------------------------------
from data_loader import load_metadata
from processing import apply_filters, compute_suggestions

# ---------------------------------------------------------
# Load the Moana dataset
# ---------------------------------------------------------
df = load_metadata("../data/moana_metadata.csv")

# Basic global stats for the whole collection
total_assets = len(df)
total_scenes = df["scene_name"].nunique()
total_file_size_mb = df["file_size_mb"].sum()
avg_polycount = int(df["poly_count"].mean())
max_polycount = int(df["poly_count"].max())
max_file_size_mb = df["file_size_mb"].max()

# Lists of values for selectors
asset_types = ["All"] + sorted(df["asset_type"].dropna().unique().tolist())
scene_options = ["All"] + sorted(df["scene_name"].dropna().unique().tolist())

# ---------------------------------------------------------
# Reactive state variables (Taipy tracks these automatically)
# ---------------------------------------------------------

# Navigation
current_page = "Overview"  # "Overview", "Scenes", "Assets", "Settings"

# Theme
dark_mode = False          # False = light theme, True = dark theme
theme_class = "app-light"  # used as CSS class on the main container

# Filter state (log sliders for better control)
# Log10(polycount): range from 1 to ~8 (10 to 100M)
poly_min_log = 1.0
poly_max_log = 8.0

# Log10(file_size_mb): range from -3 (~0.001 MB) to 4 (10,000 MB)
file_min_log = -3.0
file_max_log = 4.0

asset_type = "All"
scene_filter = "All"
heavy_only = False

# Filtered dataset and suggestions
filtered_df = df.copy()
suggestions_text = "Adjust filters to see optimization suggestions."


# ---------------------------------------------------------
# Helper: convert log slider values to real ranges
# ---------------------------------------------------------
def _compute_ranges_from_logs(state):
    """
    Convert the log-scale slider values into real polycount and file-size ranges.
    Keep values within realistic bounds of the dataset.
    """
    poly_min = int(10 ** state.poly_min_log)
    poly_max = int(10 ** state.poly_max_log)

    file_min = float(10 ** state.file_min_log)
    file_max = float(10 ** state.file_max_log)

    # Clamp to actual dataset ranges for safety
    poly_min = max(poly_min, int(df["poly_count"].min()))
    poly_max = min(poly_max, int(df["poly_count"].max()))

    file_min = max(file_min, float(df["file_size_mb"].min()))
    file_max = min(file_max, float(df["file_size_mb"].max()))

    return (poly_min, poly_max), (file_min, file_max)


# ---------------------------------------------------------
# Core reactive callback: filters and theme
# ---------------------------------------------------------
def on_state_change(state, var_name, var_value):
    """
    Central callback for changes in filters, theme, and navigation.
    Taipy will call this when a bound variable changes (on_change).
    """

    # 1. Update theme class whenever dark_mode changes
    if var_name == "dark_mode":
        state.theme_class = "app-dark" if var_value else "app-light"

    # 2. Recompute filtered data when any filter changes
    if var_name in (
        "poly_min_log",
        "poly_max_log",
        "file_min_log",
        "file_max_log",
        "asset_type",
        "scene_filter",
        "heavy_only",
    ):
        poly_range, file_range = _compute_ranges_from_logs(state)

        state.filtered_df = apply_filters(
            df,
            asset_type=state.asset_type,
            poly_range=poly_range,
            file_range=file_range,
            scene_filter=state.scene_filter,
            heavy_only=state.heavy_only,
        )

        suggestions = compute_suggestions(state.filtered_df)
        if not suggestions:
            state.suggestions_text = (
                "No optimization suggestions for the current filters."
            )
        else:
            state.suggestions_text = "\n".join(f"- {s}" for s in suggestions)


# ---------------------------------------------------------
# Overview page layout
# ---------------------------------------------------------
overview_page = """
<|layout|columns=1|class_name={theme_class} page-container|>

# Moana Technical Artist Dashboard

<|layout|columns=6 6|gap=10px|class_name=top-bar|>
<|
**Page**
<|{current_page}|selector|lov=Overview;Scenes;Assets;Settings|on_change=on_state_change|>
|>
<|
**Theme**
Dark mode  
<|{dark_mode}|toggle|on_change=on_state_change|>
|>
</|layout|>

---

<|Overview Stats|expandable|collapsed=False|class_name=panel|>
<|layout|columns=6 6 6|gap=10px|class_name=stats-row|>

<|Total Assets\n{total_assets}|card|class_name=stat-card|>
<|Total Scenes\n{total_scenes}|card|class_name=stat-card|>
<|Total File Size\n{total_file_size_mb:.1f} MB|card|class_name=stat-card|>
<|Average Polycount\n{avg_polycount}|card|class_name=stat-card|>
<|Max Polycount\n{max_polycount}|card|class_name=stat-card|>
<|Max File Size\n{max_file_size_mb:.2f} MB|card|class_name=stat-card|>

</|layout|>
|>

---

<|Filters|expandable|collapsed=False|class_name=panel|>

<|layout|columns=6 6|gap=20px|>

<|
**Asset Type**
<|{asset_type}|selector|lov={asset_types}|dropdown=True|on_change=on_state_change|>
|>

<|
**Scene Filter**
<|{scene_filter}|selector|lov={scene_options}|dropdown=True|on_change=on_state_change|>
|>

</|layout|>

<|layout|columns=6 6|gap=20px|>

<|
**Poly Count Range (log scale)**  
Lower bound: 10^{poly_min_log:.1f} polys  
Upper bound: 10^{poly_max_log:.1f} polys  

<|{poly_min_log}|slider|min=1|max=8|step=0.1|on_change=on_state_change|>
<|{poly_max_log}|slider|min=1|max=8|step=0.1|on_change=on_state_change|>
|>

<|
**File Size Range (log scale)**  
Lower bound: 10^{file_min_log:.1f} MB  
Upper bound: 10^{file_max_log:.1f} MB  

<|{file_min_log}|slider|min=-3|max=4|step=0.1|on_change=on_state_change|>
<|{file_max_log}|slider|min=-3|max=4|step=0.1|on_change=on_state_change|>
|>

</|layout|>

**Heavy Only**
<|{heavy_only}|toggle|on_change=on_state_change|>

|>

---

<|File Size Treemap|expandable|collapsed=False|class_name=panel|>

### File Size by Asset

<|{filtered_df}|chart
    |type=treemap
    |values=file_size_mb
    |labels=asset_name
    |color=poly_count
    |height=500px|>

|>

---

<|Optimization Suggestions|expandable|collapsed=False|class_name=panel|>

<|{suggestions_text}|text|>

|>

---

<|layout|columns=7 5|gap=20px|class_name=panel|>

<|
### Assets (Filtered)
<|{filtered_df}|table|height=400px|>
|>

<|
### Notes
Use filters above to focus on heavy assets, large files, or specific scenes.
|>

</|layout|>

</|layout|>
"""


# ---------------------------------------------------------
# Scenes page layout
# ---------------------------------------------------------
scenes_page = """
<|layout|columns=1|class_name={theme_class} page-container|>

# Scenes Overview

<|layout|columns=6 6|gap=10px|class_name=top-bar|>
<|
**Page**
<|{current_page}|selector|lov=Overview;Scenes;Assets;Settings|on_change=on_state_change|>
|>
<|
**Theme**
Dark mode  
<|{dark_mode}|toggle|on_change=on_state_change|>
|>
</|layout|>

---

The sections below group assets by scene. Each scene can be expanded or collapsed.

<|layout|columns=1|gap=10px|>

"""

# We will append one expandable block per scene dynamically in on_init


# ---------------------------------------------------------
# Assets page layout
# ---------------------------------------------------------
assets_page = """
<|layout|columns=1|class_name={theme_class} page-container|>

# Assets

<|layout|columns=6 6|gap=10px|class_name=top-bar|>
<|
**Page**
<|{current_page}|selector|lov=Overview;Scenes;Assets;Settings|on_change=on_state_change|>
|>
<|
**Theme**
Dark mode  
<|{dark_mode}|toggle|on_change=on_state_change|>
|>
</|layout|>

---

<|All Assets|expandable|collapsed=False|class_name=panel|>

<|{filtered_df}|table|height=600px|>

|>

</|layout|>
"""


# ---------------------------------------------------------
# Settings page layout
# ---------------------------------------------------------
settings_page = """
<|layout|columns=1|class_name={theme_class} page-container|>

# Settings

<|layout|columns=6 6|gap=10px|class_name=top-bar|>
<|
**Page**
<|{current_page}|selector|lov=Overview;Scenes;Assets;Settings|on_change=on_state_change|>
|>
<|
**Theme**
Dark mode  
<|{dark_mode}|toggle|on_change=on_state_change|>
|>
</|layout|>

---

<|Theme Settings|expandable|collapsed=False|class_name=panel|>

**Dark Mode**
<|{dark_mode}|toggle|on_change=on_state_change|>

Dark theme uses deep ocean blues with bright aqua text for readability.  
Light theme uses sand and lagoon tones for a Moana-inspired look.

|>

---

<|About|expandable|collapsed=False|class_name=panel|>

This dashboard is a technical-artist focused tool built on the Moana island dataset.  
It is designed to support scene and asset optimization in animation, VFX, games, and virtual production.

|>

</|layout|>
"""


# ---------------------------------------------------------
# Pages dictionary for top-bar navigation
# ---------------------------------------------------------
pages = {
    "Overview": overview_page,
    "Scenes": scenes_page,
    "Assets": assets_page,
    "Settings": settings_page,
}


# ---------------------------------------------------------
# Optional: initialize dynamic parts (like scenes page content)
# ---------------------------------------------------------
def on_init(state):
    """
    Called when the GUI starts.
    Here we can build dynamic pieces like per-scene sections.
    """
    # Build per-scene expandable blocks as simple text, using the filtered df by scene.
    # For now we use the full df; you can later tie this to filtered_df if desired.
    scene_blocks = []
    grouped = df.groupby("scene_name")
    for scene_name, scene_df in grouped:
        block = f"""
<|Scene: {scene_name}|expandable|collapsed=True|class_name=panel|>

**Assets in Scene:** {len(scene_df)}  
**Total File Size:** {scene_df["file_size_mb"].sum():.1f} MB  
**Average Polycount:** {int(scene_df["poly_count"].mean())}

<|{scene_df}|table|height=300px|>

|>
"""
        scene_blocks.append(block)

    # Attach dynamic blocks to the scenes page
    state.scenes_page_dynamic = (
        scenes_page + "\n".join(scene_blocks) + "\n</|layout|>\n"
    )


# ---------------------------------------------------------
# Entry point
# ---------------------------------------------------------
if __name__ == "__main__":
    gui = Gui(pages={"Overview": overview_page,
                     "Scenes": lambda s: s.scenes_page_dynamic if hasattr(s, "scenes_page_dynamic") else scenes_page,
                     "Assets": assets_page,
                     "Settings": settings_page},
              css_file="theme.css")

    gui.run(
        title="Moana Technical Artist Dashboard",
        on_state_change=on_state_change,
        on_init=on_init,
    )
