# Asset Variant Detail

## Select Variant

<|{selected_variant}|selector|lov={list(assets["variant_name"])}|dropdown=True|on_change=on_change_variant|label=Variant|>

<br/>

<|layout|columns=1 1 1|
<|card|
**Asset Family**  
<|{detail_state["asset_family"]}|text|>
|>
<|card|
**Polycount (approx.)**  
<|{detail_state["polycount"]}|text|>
|>
<|card|
**Triangles (approx.)**  
<|{detail_state["triangles"]}|text|>
|>
|>

<br/>

<|layout|columns=1 1 1|
<|card|
**Materials (approx.)**  
<|{detail_state["material_count"]}|text|>
|>
<|card|
**Hierarchy Depth (approx.)**  
<|{detail_state["hierarchy_depth"]}|text|>
|>
<|card|
**Folder Size (MB)**  
<|{detail_state["folder_size_mb"]}|text|>
|>
|>

<br/>

**OBJ Path**  
<|{detail_state["asset_path"]}|text|>
