# Asset Visualizations

---

<|{selected_family}|selector|lov={family_options}|dropdown=True|on_change=on_family_change|label=Asset Family Filter|>

---

## Triangle Count Distribution (per Variant)

<|{viz_state.tri_data}|chart|type=bar|properties={viz_state.tri_props}|title="Triangles per variant"|layout={layout_log_y}|>

---

## Folder Size Treemap (by Asset Family)

<|{treemap_df}|chart|type=treemap|labels=labels|parents=parents|values=values|title="Moana asset hierarchy"|>

---

## Material Count Distribution

<|{viz_state.mat_data}|chart|type=bar|properties={viz_state.mat_props}|title="Materials per variant"|>

---

## Polycount Distribution

<|{viz_state.poly_data}|chart|type=bar|properties={viz_state.poly_props}|title="Polycount per variant"|layout={layout_log_y}|>

---

## Polycount vs Material Count (per Variant)

<|{viz_state.scatter_data}|chart|type=scatter|mode=markers|properties={viz_state.scatter_props}|title="Polycount vs materials"|layout={layout_log_x}|>

---

## Heaviest Asset Families (Top 10)

<|chart|type=bar|data={bar_df}|x=family|y=size|text=label|title=Heaviest Asset Families|x_title="Asset Family"|y_title="Size (MB)"|xaxis_tickangle=45|>
