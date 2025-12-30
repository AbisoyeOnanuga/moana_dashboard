#from taipy import Gui
from taipy.gui import Gui as ui
import pandas as pd

from data_loader import load_metadata
from pages.dashboard_page import create_dashboard_page

# ---------------------------------------------------------
# Load metadata
# ---------------------------------------------------------

df = load_metadata("../data/moana_metadata.csv")

# ---------------------------------------------------------
# Initial State
# ---------------------------------------------------------

class State:
    asset_type = "All"
    poly_min = 0
    poly_max = int(df["poly_count"].max() or 1_000_000)

    file_min = 0
    file_max = int(df["file_size_mb"].max() or 1000)

    scene_filter = "All"
    heavy_only = False

state = State()

# ---------------------------------------------------------
# Build the dashboard page
# ---------------------------------------------------------

page = create_dashboard_page(state, df)

# ---------------------------------------------------------
# Run the app
# ---------------------------------------------------------

app = ui(page, css_file="theme.css")
app.run(title="Moana Technical Artist Dashboard", dark_mode=False)
