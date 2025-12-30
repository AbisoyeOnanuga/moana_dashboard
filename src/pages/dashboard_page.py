from taipy import gui as ui
from processing import apply_filters, compute_suggestions
from ui_components import (
    asset_table_grouped,
    file_size_treemap,
    filters_panel,
    suggestions_panel
)

# ---------------------------------------------------------
# Dashboard Page
# ---------------------------------------------------------

def create_dashboard_page(state, df):
    """
    Build the full dashboard page layout.
    This function is called from app.py and receives:
        - state: Taipy state object
        - df: full metadata DataFrame
    """

    # -----------------------------------------------------
    # Apply filters to get the filtered DataFrame
    # -----------------------------------------------------
    filtered_df = df.copy()

    # Scene filter
    if state.scene_filter != "All":
        filtered_df = filtered_df[filtered_df["scene_name"] == state.scene_filter]

    # Asset type + poly range
    filtered_df = apply_filters(
        filtered_df,
        asset_type=state.asset_type,
        poly_range=(state.poly_min, state.poly_max)
    )

    # File size filter
    filtered_df = filtered_df[
        filtered_df["file_size_mb"].fillna(0).between(state.file_min, state.file_max)
    ]

    # Heavy-only toggle
    if state.heavy_only:
        filtered_df = filtered_df[filtered_df["poly_count"] > 500_000]

    # -----------------------------------------------------
    # Compute suggestions
    # -----------------------------------------------------
    suggestions = compute_suggestions(filtered_df)

    # -----------------------------------------------------
    # Build UI Layout
    # -----------------------------------------------------
    return ui.page(
        ui.row(
            ui.column(
                filters_panel(state, df),
                width=3
            ),
            ui.column(
                file_size_treemap(filtered_df),
                width=9
            )
        ),

        ui.row(
            ui.column(
                asset_table_grouped(filtered_df),
                width=8
            ),
            ui.column(
                suggestions_panel(suggestions),
                width=4
            )
        )
    )
