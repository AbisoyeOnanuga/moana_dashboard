from taipy import gui as ui

# ---------------------------------------------------------
# Asset Table (Grouped by Scene)
# ---------------------------------------------------------

def asset_table_grouped(df):
    """
    Returns a list of UI expanders, one per scene_name.
    Each expander contains a sortable table of assets.
    """
    ui_blocks = []
    groups = df.groupby("scene_name")

    for scene, group_df in groups:
        # Sort by poly_count descending for readability
        group_df = group_df.sort_values("poly_count", ascending=False)

        ui_blocks.append(
            ui.expander(
                scene,
                ui.table(
                    group_df,
                    columns=[
                        "asset_name",
                        "asset_type",
                        "poly_count",
                        "file_size_mb",
                        "instance_count",
                        "obj_path"
                    ],
                    height="300px"
                )
            )
        )

    return ui_blocks


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
        return ui.text("No file size data available for treemap.")

    return ui.chart(
        data=df2,
        type="treemap",
        values="file_size_mb",
        labels="asset_name",
        color="poly_count",
        height="500px"
    )


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
    return ui.column(
        ui.text("Filters", mode="title"),

        ui.select(
            label="Asset Type",
            value=state.asset_type,
            options=["All"] + sorted(df["asset_type"].unique()),
            on_change=lambda s, v: setattr(s, "asset_type", v)
        ),

        ui.slider(
            label="Poly Count Range",
            min=0,
            max=int(df["poly_count"].max() or 1_000_000),
            value=(state.poly_min, state.poly_max),
            on_change=lambda s, v: (setattr(s, "poly_min", v[0]), setattr(s, "poly_max", v[1]))
        ),

        ui.slider(
            label="File Size (MB)",
            min=0,
            max=int(df["file_size_mb"].max() or 1000),
            value=(state.file_min, state.file_max),
            on_change=lambda s, v: (setattr(s, "file_min", v[0]), setattr(s, "file_max", v[1]))
        ),

        ui.select(
            label="Scene",
            value=state.scene_filter,
            options=["All"] + sorted(df["scene_name"].unique()),
            on_change=lambda s, v: setattr(s, "scene_filter", v)
        ),

        ui.checkbox(
            label="Show only heavy assets",
            value=state.heavy_only,
            on_change=lambda s, v: setattr(s, "heavy_only", v)
        ),

        width="100%"
    )


# ---------------------------------------------------------
# Suggestions Panel
# ---------------------------------------------------------

def suggestions_panel(suggestions):
    """
    Display optimization suggestions as a list.
    """
    return ui.card(
        ui.text("Optimization Suggestions", mode="title"),
        ui.list(suggestions)
    )
