# Asset Visualizations

---

<!-- <|{selected_family}|selector|lov={family_options}|dropdown=True|on_change=on_family_change|label=Asset Family Filter|> -->

## Triangle Count Distribution (per Variant)

<|{tri_data}|chart|type=bar|y=Triangle Count (log scaled)|properties={tri_props}|title=Triangles per variant|layout={layout_log_y}|>

---

## Folder Size Treemap (by Asset Family)

<|{treemap_df}|chart|type=treemap|labels=labels|parents=parents|values=values|title=Moana asset hierarchy|>

---

## Material Count Distribution

<|{mat_data}|chart|type=bar|y=Material Count|properties={mat_props}|title=Materials per variant|>

---

## Polycount Distribution

<|{poly_data}|chart|type=bar|y=Polycount (log scaled)|properties={poly_props}|title=Polycount per variant|layout={layout_log_y}|>

---

## Polycount vs Material Count (per Variant)

<|chart|{scatter_data}|type=scatter|y=Materials|mode=markers|properties={scatter_props}|title=Polycount vs materials|layout={layout_log_x}|>

---

## Heaviest Asset Families (Top 10)

<|chart|type=bar|data={bar_df}|x=Asset Family|y=Size (MB)|text=hover|title=Heaviest Asset Families|xaxis_tickangle=45|>
