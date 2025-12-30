from taipy.gui import Gui
from data_loader import load_metadata
from processing import apply_filters, compute_suggestions

# ---------------------------------------------------------
# Load metadata
# ---------------------------------------------------------
df = load_metadata("../data/moana_metadata.csv")

# Precompute LOVs for selectors
asset_types = ["All"] + sorted(df["asset_type"].dropna().unique().tolist())
scene_options = ["All"] + sorted(df["scene_name"].dropna().unique().tolist())

# ---------------------------------------------------------
# Reactive state variables
# Taipy automatically tracks these and updates the UI
# ---------------------------------------------------------

# Theme toggle
dark_mode = False

# Filters
asset_type = "All"
poly_min = 0
poly_max = 18_000_000  # calibrated for Moana dataset

file_min = 0
file_max = 3000  # calibrated for Moana dataset

scene_filter = "All"
heavy_only = False

# Filtered data + suggestions
filtered_df = df.copy()
suggestions_text = "Adjust filters to see optimization suggestions."


# ---------------------------------------------------------
# Callback: recompute filtered data when any filter changes
# ---------------------------------------------------------
def on_filter_change(state, var_name, var_value):
    """
    Called whenever a filter control changes.
    Recomputes filtered_df and suggestions_text.
    """

    # Apply all filters
    state.filtered_df = apply_filters(
        df,
        asset_type=state.asset_type,
        poly_range=(state.poly_min, state.poly_max),
        file_range=(state.file_min, state.file_max),
        scene_filter=state.scene_filter,
        heavy_only=state.heavy_only,
    )

    # Compute suggestions
    suggestions = compute_suggestions(state.filtered_df)
    if not suggestions:
        state.suggestions_text = "No optimization suggestions for the current filters."
    else:
        state.suggestions_text = "\n".join(f"- {s}" for s in suggestions)


# ---------------------------------------------------------
# Page Layout (Taipy GUI Markup)
# ---------------------------------------------------------
page = """
# Moana Technical Artist Dashboard

<|layout|columns=2 10|gap=20px|>

<|
### Theme
Toggle Dark Mode  
<|{dark_mode}|toggle|on_change=on_filter_change|>
|>

<|
### Filters
<|Filters|expandable|collapsed=True|>

<|layout|columns=1|gap=14px|>

**Asset Type**
<|{asset_type}|selector|lov={asset_types}|on_change=on_filter_change|>

**Poly Count Range**
<|{poly_min}|slider|min=0|max=18000000|on_change=on_filter_change|>
<|{poly_max}|slider|min=0|max=18000000|on_change=on_filter_change|>

**File Size Range (MB)**
<|{file_min}|slider|min=0|max=3000|on_change=on_filter_change|>
<|{file_max}|slider|min=0|max=3000|on_change=on_filter_change|>

<|Scene Filter|expandable|collapsed=True|>
<|{scene_filter}|selector|lov={scene_options}|on_change=on_filter_change|>

**Heavy Only**
<|{heavy_only}|toggle|on_change=on_filter_change|>

</|layout|>

|>

</|layout|>

---

### File Size Treemap

<|{filtered_df}|chart|type=treemap|values=file_size_mb|labels=asset_name|color=poly_count|height=500px|>

---

<|layout|columns=7 5|gap=20px|>

<|
### Assets (Filtered)
<|{filtered_df}|table|height=400px|>
|>

<|
### Optimization Suggestions
<|{suggestions_text}|text|>
|>

</|layout|>
"""


# ---------------------------------------------------------
# Run GUI
# ---------------------------------------------------------
if __name__ == "__main__":
    gui = Gui(page, css_file="theme.css")
    gui.run(title="Moana Technical Artist Dashboard")
