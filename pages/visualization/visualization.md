# Asset Visualizations

---

## Triangle Count Distribution (per Variant)

<|chart|type=histogram|data={hist_tri_df}|x=triangles|text=hover|nbins=40|title=Triangle Count Distribution|x_title="Triangle Count"|y_title="Number of Variants"|>

---

## Folder Size Treemap (by Asset Family)

<|chart|type=treemap|data={treemap_df}|labels=labels|parents=parents|values=values|title=Folder Size by Asset Family|>

---

## Material Count Distribution

<|chart|type=histogram|data={hist_mat_df}|x=materials|    text=hover|nbins=20|title=Material Count Distribution|x_title="Material Count"|y_title="Number of Variants"|hoverinfo=text|>

---

## Polycount Distribution

<|chart|type=histogram|data={hist_poly_df}|x=polycount|    text=hover|nbins=40|title=Polycount Distribution|x_title="Polycount"|y_title="Number of Variants"|hoverinfo=text|>

---

## Polycount vs Material Count (per Variant)

<|chart|type=scatter|data={scatter_poly_df}|x=polycount|y=materials|text=hover|mode=markers|title=Polycount vs Material Count|x_title="Polycount"|y_title="Material Count"|>

---

## Heaviest Asset Families (Top 10)

<|chart|type=bar|data={bar_df}|x=family|y=size|text=label|title=Heaviest Asset Families|x_title="Asset Family"|y_title="Size (MB)"|xaxis_tickangle=45|>
