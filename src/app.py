from taipy.gui import Gui
from data_loader import load_metadata
from processing import apply_filters, compute_suggestions

# ---------------------------------------------------------
# Load base data
# ---------------------------------------------------------

df = load_metadata("../data/moana_metadata.csv")

# Derive LOVs for filters
asset_types = ["All"] + sorted(df["asset_type"].dropna().unique().tolist())
scene_options = ["All"] + sorted(df["scene_name"].dropna().unique().tolist())

# ---------------------------------------------------------
# Reactive state variables (Taipy will manage these)
# ---------------------------------------------------------

# Filter variables
asset_type = "All"
poly_min = int(df["poly_count"].min())
poly_max = int(df["poly_count"].max())

file_min = int(df["file_size_mb"].min())
file_max = int(df["file_size_mb"].max())

scene_filter = "All"
heavy_only = False

# Data driven by filters
filtered_df = df.copy()
suggestions_text = "No optimization suggestions yet. Adjust filters to see recommendations."


# ---------------------------------------------------------
# Callback: recompute filtered data when any control changes
# ---------------------------------------------------------

def on_filter_change(state, var_name, var_value):
    """
    Called whenever a filter control changes.
    'state' holds the current GUI variables.
    """
    # Recompute filtered dataframe
    state.filtered_df = apply_filters(
        df,
        asset_type=state.asset_type,
        poly_range=(state.poly_min, state.poly_max),
        file_range=(state.file_min, state.file_max),
        scene_filter=state.scene_filter,
        heavy_only=state.heavy_only,
    )

    # Recompute suggestions
    suggestions = compute_suggestions(state.filtered_df)
    if not suggestions:
        state.suggestions_text = "No optimization suggestions for the current filters."
    else:
        state.suggestions_text = "\n".join(f"- {s}" for s in suggestions)


# ---------------------------------------------------------
# Page layout (Taipy GUI markup)
# ---------------------------------------------------------

page = """
# Moana Technical Artist Dashboard

<|layout|columns=3 9|gap=20px|>

<|
### Filters

<|layout|columns=1|gap=14px|>

**Asset Type**
<|{asset_type}|selector|lov={asset_types}|on_change=on_filter_change|>

**Poly Count Range**
<|{poly_min}|slider|min={int(df['poly_count'].min())}|max={int(df['poly_count'].max())}|on_change=on_filter_change|>
<|{poly_max}|slider|min={int(df['poly_count'].min())}|max={int(df['poly_count'].max())}|on_change=on_filter_change|>

**File Size Range (MB)**
<|{file_min}|slider|min={int(df['file_size_mb'].min())}|max={int(df['file_size_mb'].max())}|on_change=on_filter_change|>
<|{file_max}|slider|min={int(df['file_size_mb'].min())}|max={int(df['file_size_mb'].max())}|on_change=on_filter_change|>

**Scene Filter**
<|{scene_filter}|selector|lov={scene_options}|on_change=on_filter_change|>

**Heavy Only**
<|{heavy_only}|toggle|on_change=on_filter_change|>

</|layout|>

|>

<|
### File Size Treemap

<|{filtered_df}|chart
    |type=treemap
    |values=file_size_mb
    |labels=asset_name
    |color=poly_count
    |height=500px|>

|>

</|layout|>

---

<|layout|columns=7 5|gap=20px|>

<|
### Assets (Filtered)

<|{filtered_df}|table|height=400px|>

|>

<|
### Optimization Suggestions

{suggestions_text}

|>

</|layout|>
"""


# ---------------------------------------------------------
# Run GUI
# ---------------------------------------------------------

if __name__ == "__main__":
    gui = Gui(page)
    gui.run(title="Moana Technical Artist Dashboard", css_file="theme.css")
