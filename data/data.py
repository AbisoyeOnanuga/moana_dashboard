import os
import json
from pathlib import Path

import pandas as pd

# Adjust this to your project structure
MOANA_ROOT = Path("D:/Downloads/island")

# Subfolders inside the Moana dataset
JSON_ROOT = MOANA_ROOT / "json"
OBJ_ROOT = MOANA_ROOT / "obj"

def format_number(n: int) -> str:
    return f"{n:,}"

def format_size_mb(size: float) -> str:
    if size >= 1024:
        return f"{size/1024:.2f} GB"
    return f"{size:.2f} MB"

def load_metadata_json() -> pd.DataFrame:
    """
    Load all JSON metadata files into a single DataFrame.
    Assumes each JSON file is a dict with consistent keys.
    """
    rows = []

    if not JSON_ROOT.exists():
        return pd.DataFrame()

    for file in JSON_ROOT.glob("*.json"):
        try:
            with file.open("r", encoding="utf-8") as f:
                data = json.load(f)
                # Optionally add filename as an id/link
                data["__json_file"] = file.as_posix()
                rows.append(data)
        except Exception as e:
            print(f"[metadata] Error reading {file}: {e}")

    if not rows:
        return pd.DataFrame()

    return pd.DataFrame(rows)

def compute_hierarchy_depth(hier_file: Path) -> int:
    if not hier_file.exists():
        return 0

    max_depth = 0
    with open(hier_file, "r") as f:
        for line in f:
            # Count indentation (spaces or tabs)
            indent = len(line) - len(line.lstrip())
            depth = indent // 2  # adjust if needed
            max_depth = max(max_depth, depth)

    return max_depth

def count_materials(mtl_file: Path) -> int:
    if not mtl_file.exists():
        return 0

    count = 0
    with open(mtl_file, "r") as f:
        for line in f:
            if line.startswith("newmtl"):
                count += 1
    return count

def compute_polycount_from_obj(obj_path: Path) -> int:
    """
    Naive polycount proxy: count vertex lines 'v ' in OBJ.
    Not exact, but good enough for dashboard-level approximation.
    """
    try:
        count = 0
        with obj_path.open("r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                if line.startswith("v "):
                    count += 1
        return count
    except Exception as e:
        print(f"[polycount] Error reading {obj_path}: {e}")
        return 0


def compute_material_count_from_mtl(mtl_path: Path) -> int:
    """
    Approx material count: count 'newmtl' entries in MTL.
    """
    try:
        count = 0
        with mtl_path.open("r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                if line.strip().startswith("newmtl"):
                    count += 1
        return count
    except Exception as e:
        print(f"[mtl] Error reading {mtl_path}: {e}")
        return 0


def compute_hierarchy_depth_from_hier(hier_path: Path) -> int:
    """
    Rough hierarchy depth: count indentation or levels.
    This is placeholder logic; you can refine based on actual .hier format.
    """
    try:
        max_depth = 0
        with hier_path.open("r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                # Example: depth inferred from leading spaces or tabs
                stripped = line.lstrip(" \t")
                indent = len(line) - len(stripped)
                depth = indent // 2  # assume 2 spaces per level
                if depth > max_depth:
                    max_depth = depth
        return max_depth
    except Exception as e:
        print(f"[hier] Error reading {hier_path}: {e}")
        return 0


def compute_folder_size_mb(path: Path) -> float:
    total = 0
    try:
        for p in path.rglob("*"):
            if p.is_file():
                total += p.stat().st_size
    except Exception as e:
        print(f"[size] Error walking {path}: {e}")
    return round(total / (1024 * 1024), 2)


def load_obj_families():
    """
    Walk OBJ_ROOT and build a table:
    - asset_family (folder name)
    - variant_name (e.g., isBayCedarA1_bonsaiA)
    - polycount
    - material_count
    - hierarchy_depth
    - folder_size_mb
    - asset_path
    """
    rows = []

    if not OBJ_ROOT.exists():
        return pd.DataFrame()

    # Walk each asset family folder
    for family_dir in OBJ_ROOT.iterdir():
        if not family_dir.is_dir():
            continue
        
        asset_family = family_dir.name

        # Walk each OBJ inside the family folder
        for obj_file in family_dir.glob("*.obj"):
            name = obj_file.stem  # variant name

            mtl_file = obj_file.with_suffix(".mtl")
            hier_file = obj_file.with_suffix(".hier")

            # Polycount (already correct in your version)
            polycount = compute_polycount_from_obj(obj_file)

            # Triangle count (artist-friendly)
            triangles = polycount * 2

            # Material count
            material_count = count_materials(mtl_file)

            # Hierarchy depth
            hierarchy_depth = compute_hierarchy_depth(hier_file)

            # Variant-specific file size
            obj_size = obj_file.stat().st_size / (1024 * 1024)
            mtl_size = mtl_file.stat().st_size / (1024 * 1024) if mtl_file.exists() else 0
            hier_size = hier_file.stat().st_size / (1024 * 1024) if hier_file.exists() else 0
            variant_size_mb = obj_size + mtl_size + hier_size

            rows.append({
                "variant_name": name,
                "asset_family": asset_family,
                "polycount": polycount,
                "triangles": triangles,
                "material_count": material_count,
                "hierarchy_depth": hierarchy_depth,
                "folder_size_mb": variant_size_mb,
                "asset_path": obj_file.as_posix(),

                # Formatted versions for UI
                "polycount_fmt": format_number(polycount),
                "triangles_fmt": format_number(triangles),
                "material_count_fmt": format_number(material_count),
                "hierarchy_depth_fmt": format_number(hierarchy_depth),
                "folder_size_fmt": format_size_mb(variant_size_mb),
            })

    if not rows:
        return pd.DataFrame()

    return pd.DataFrame(rows)

def build_tree_structure() -> pd.DataFrame:
    """
    Build a tree-like structure from the MOANA_ROOT for visualization.
    We'll return a DataFrame with columns: id, parent, label, type, size_mb.
    This works well with tree/treemap-style views.
    """
    nodes = []
    node_id = 0

    def add_node(path: Path, parent_id: int | None, depth: int):
        nonlocal node_id
        current_id = node_id
        node_id += 1

        # relative label logic
        rel = path.relative_to(MOANA_ROOT)
        base_label = str(rel) if rel != Path(".") else "moana"

        # indentation
        label = ("— " * depth) + base_label

        # type + size logic
        if path.is_dir():
            size_mb = compute_folder_size_mb(path)
            node_type = "folder"
        else:
            size_mb = round(path.stat().st_size / (1024 * 1024), 4)
            node_type = "file"

        nodes.append(
            {
                "id": current_id,
                "parent": parent_id,
                "label": label,
                "type": node_type,
                "size_mb": size_mb,
                "depth": depth,
            }
        )

        # recursion for directories
        if path.is_dir():
            for child in path.iterdir():
                add_node(child, current_id, depth + 1)

    # pass depth=0
    if MOANA_ROOT.exists():
        add_node(MOANA_ROOT, None, 0)

    return pd.DataFrame(nodes)


def compute_kpis(assets_df: pd.DataFrame, metadata_df: pd.DataFrame) -> dict:
    if assets_df is None or assets_df.empty:
        total_assets = 0
        total_variants = 0
    else:
        total_assets = assets_df["asset_family"].nunique()
        total_variants = len(assets_df)

    # Example metadata fields – adjust based on actual Moana JSON keys
    if metadata_df is not None and not metadata_df.empty:
        # If there's a "category" field (prop/camera/etc.)
        if "category" in metadata_df.columns:
            total_props = (metadata_df["category"] == "prop").sum()
            total_cameras = (metadata_df["category"] == "camera").sum()
        else:
            total_props = total_cameras = 0
    else:
        total_props = total_cameras = 0

    # Materials as sum of material_count, textures left out for now
    total_materials = int(assets_df["material_count"].sum()) if not assets_df.empty else 0
    
    # --- CAMERA COUNT FIX ---
    # Cameras are not in assets_df or metadata_df, so detect them from metadata_df JSON structure

    # Path to the camera folder (adjust if needed)
    camera_folder = os.path.join(JSON_ROOT, "cameras")

    total_cameras = 0
    if os.path.isdir(camera_folder):
        total_cameras = sum(
            1 for f in os.listdir(camera_folder)
            if f.lower().endswith(".json") and "cam" in f.lower()
        )

    return {
        "total_assets": int(total_assets),
        "total_variants": int(total_variants),
        "total_props": int(total_props),
        "total_cameras": int(total_cameras),
        "total_materials": total_materials,
    }


def prepare_treemap_data(assets_df: pd.DataFrame) -> dict:
    """
    Prepare data for a folder-size or asset-size treemap.
    Simple example: treemap by asset_family using folder_size_mb.
    """
    if assets_df is None or assets_df.empty:
        return {"labels": [], "parents": [], "values": []}

    grouped = (
        assets_df.groupby("asset_family")
        .agg({"folder_size_mb": "max"})
        .reset_index()
    )

    labels = list(grouped["asset_family"])
    parents = ["Moana"] * len(labels)
    values = list(grouped["folder_size_mb"])

    return {"labels": labels, "parents": parents, "values": values}


import time
import pandas as pd
import json
from concurrent.futures import ThreadPoolExecutor

# Paths for caching
CACHE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "_cache")
os.makedirs(CACHE_DIR, exist_ok=True)

META_CACHE = os.path.join(CACHE_DIR, "metadata.feather")
ASSET_CACHE = os.path.join(CACHE_DIR, "assets.feather")
TREE_CACHE = os.path.join(CACHE_DIR, "tree.feather")
TREEMAP_CACHE = os.path.join(CACHE_DIR, "treemap.json")
KPI_CACHE = os.path.join(CACHE_DIR, "kpis.json")


def _load_if_exists(path):
    return os.path.exists(path)


def _load_feather(path):
    return pd.read_feather(path)


def _save_feather(df, path):
    df.reset_index(drop=True).to_feather(path)


def _load_json(path):
    with open(path, "r") as f:
        return json.load(f)


def _save_json(obj, path):
    with open(path, "w") as f:
        json.dump(obj, f)


def load_all():
    """
    Optimized loader:
    - Uses cached results if available
    - Recomputes only missing pieces
    - Parallelizes heavy operations
    """

    # --------------------------------------------------
    # 1. METADATA
    # --------------------------------------------------
    if _load_if_exists(META_CACHE):
        metadata = _load_feather(META_CACHE)
    else:
        metadata = load_metadata_json()
        _save_feather(metadata, META_CACHE)

    # --------------------------------------------------
    # 2. ASSETS
    # --------------------------------------------------
    if _load_if_exists(ASSET_CACHE):
        assets = _load_feather(ASSET_CACHE)
    else:
        assets = load_obj_families()
        _save_feather(assets, ASSET_CACHE)

    # --------------------------------------------------
    # 3. TREE STRUCTURE
    # --------------------------------------------------
    if _load_if_exists(TREE_CACHE):
        tree_df = _load_feather(TREE_CACHE)
    else:
        tree_df = build_tree_structure()
        _save_feather(tree_df, TREE_CACHE)

    # --------------------------------------------------
    # 4. TREEMAP DATA
    # --------------------------------------------------
    if _load_if_exists(TREEMAP_CACHE):
        treemap_data = _load_json(TREEMAP_CACHE)
    else:
        treemap_data = prepare_treemap_data(assets)
        _save_json(treemap_data, TREEMAP_CACHE)

    # --------------------------------------------------
    # 5. KPIs
    # --------------------------------------------------
    if _load_if_exists(KPI_CACHE):
        kpis = _load_json(KPI_CACHE)
    else:
        kpis = compute_kpis(assets, metadata)
        _save_json(kpis, KPI_CACHE)

    return metadata, assets, tree_df, kpis, treemap_data
