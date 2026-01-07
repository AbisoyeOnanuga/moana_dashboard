# Asset Visualizations

---

## Triangle Count Distribution (per Variant)

<|{tri_data}|chart|type=bar|properties={tri_props}|title=Triangles per variant|layout={layout_log_y}|>

---

## Folder Size Treemap (by Asset Family)

<|{treemap_df}|chart|type=treemap|labels=labels|parents=parents|values=values|title=Moana asset hierarchy|>

---

## Material Count Distribution

<|{mat_data}|chart|type=bar|properties={mat_props}|title=Materials per variant|>

---

## Polycount Distribution

<|{poly_data}|chart|type=bar|properties={poly_props}|title=Polycount per variant|layout={layout_log_y}|>

---

## Polycount vs Material Count (per Variant)

<|{scatter_data}|chart|type=scatter|mode=markers|properties={scatter_props}|title=Polycount vs materials|layout={layout_log_x}|>

---

## Heaviest Asset Families (Top 10)

<|chart|type=bar|data={bar_df}|x=family|y=size|text=hover|title=Heaviest Asset Families|x_title="Asset Family"|y_title="Size (MB)"|xaxis_tickangle=45|>
