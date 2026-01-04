from taipy.gui import Gui

from pages.home.home import home_md
from pages.table.table import table_md
from pages.tree.tree import tree_md
from pages.visualization import visualization
from pages.detail.detail import detail_md

stylekit = {
    "color_primary": "rgb(60, 120, 200)",
    "color_secondary": "rgb(200, 160, 100)",
    "font_family": "'Segoe UI', sans-serif",
}

pages = {
    "/": home_md,
    "Table": table_md,
    "Tree": tree_md,
    "Visualization": visualization.visualization_md,
    "Detail": detail_md,
}

gui = Gui(pages=pages, css_file="styles.css")

if __name__ == "__main__":
    gui.run(title="Moana Project Profiler", stylekit=stylekit)
