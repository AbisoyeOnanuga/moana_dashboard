import os
import json
from pathlib import Path
import datetime
import pandas as pd

# Adjust this to your project structure
MOANA_ROOT = Path("D:/Downloads/island")
EXPORTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "exports")
os.makedirs(EXPORTS_DIR, exist_ok=True)

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
    Parallelized over JSON files for faster ingestion.
    """
    rows = []

    if not JSON_ROOT.exists():
        return pd.DataFrame()

    json_files = list(JSON_ROOT.glob("*.json"))
    if not json_files:
        return pd.DataFrame()

    def _read_single_metadata(file: Path):
        try:
            with file.open("r", encoding="utf-8") as f:
                data = json.load(f)
                if not isinstance(data, dict):
                    # Skip non-dict JSON structures for now
                    return None
                data["__json_file"] = file.as_posix()
                return data
        except Exception as e:
            print(f"[metadata] Error reading {file}: {e}")
            return None

    # Parallel JSON parsing
    from concurrent.futures import ThreadPoolExecutor

    with ThreadPoolExecutor() as pool:
        for result in pool.map(_read_single_metadata, json_files):
            if result is not None:
                rows.append(result)

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
    - folder_size_mb (per variant: obj + mtl + hier)
    - asset_path

    Parallelized over OBJ files for faster ingestion.
    """
    from concurrent.futures import ThreadPoolExecutor

    if not OBJ_ROOT.exists():
        return pd.DataFrame()

    # Collect all OBJ files and their families first (cheap)
    obj_tasks = []
    for family_dir in OBJ_ROOT.iterdir():
        if not family_dir.is_dir():
            continue
        asset_family = family_dir.name
        for obj_file in family_dir.glob("*.obj"):
            obj_tasks.append((asset_family, obj_file))

    if not obj_tasks:
        return pd.DataFrame()

    def _process_single_obj(task):
        asset_family, obj_file = task
        obj_file = Path(obj_file)
        try:
            name = obj_file.stem  # variant name

            mtl_file = obj_file.with_suffix(".mtl")
            hier_file = obj_file.with_suffix(".hier")

            # Polycount
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

            return {
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
            }
        except Exception as e:
            print(f"[assets] Error processing {obj_file}: {e}")
            return None

    rows = []
    # Parallel OBJ/MTL/HIER processing
    with ThreadPoolExecutor() as pool:
        for result in pool.map(_process_single_obj, obj_tasks):
            if result is not None:
                rows.append(result)

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
import json
import hashlib
from concurrent.futures import ThreadPoolExecutor

# Paths for caching
CACHE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "_cache")
os.makedirs(CACHE_DIR, exist_ok=True)

META_CACHE = os.path.join(CACHE_DIR, "metadata.feather")
ASSET_CACHE = os.path.join(CACHE_DIR, "assets.feather")
TREE_CACHE = os.path.join(CACHE_DIR, "tree.feather")
TREEMAP_CACHE = os.path.join(CACHE_DIR, "treemap.json")
KPI_CACHE = os.path.join(CACHE_DIR, "kpis.json")
MANIFEST_CACHE = os.path.join(CACHE_DIR, "manifest.json")  # for change detection


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


def _compute_dir_hash(path: Path) -> str:
    """
    Compute a simple hash based on file paths + mtimes under a directory.
    This is coarse but safe: if anything changes, the hash changes.
    """
    if not path.exists():
        return ""

    hasher = hashlib.sha1()
    for p in sorted(path.rglob("*")):
        if p.is_file():
            rel = p.relative_to(path).as_posix().encode("utf-8")
            mtime = str(p.stat().st_mtime).encode("utf-8")
            hasher.update(rel + b"|" + mtime)
    return hasher.hexdigest()


def _load_manifest():
    if not os.path.exists(MANIFEST_CACHE):
        return {}
    try:
        with open(MANIFEST_CACHE, "r") as f:
            return json.load(f)
    except Exception:
        return {}


def _save_manifest(manifest: dict):
    with open(MANIFEST_CACHE, "w") as f:
        json.dump(manifest, f)


def clear_cache():
    """
    Remove all cached artifacts.
    Safe to call when the dataset has changed or you want a full rebuild.
    """
    for path in [
        META_CACHE,
        ASSET_CACHE,
        TREE_CACHE,
        TREEMAP_CACHE,
        KPI_CACHE,
        MANIFEST_CACHE,
    ]:
        if os.path.exists(path):
            try:
                os.remove(path)
            except OSError:
                # Non-fatal: if something can't be removed, we just leave it.
                pass

def _write_export_json(obj, filename):
    """Write a JSON file into the exports directory."""
    path = os.path.join(EXPORTS_DIR, filename)
    with open(path, "w") as f:
        json.dump(obj, f, indent=2)

def export_maya_metadata(assets_df, metadata_df):
    """
    Create a unified metadata export for Maya and PBRT/Maya pipeline tools.
    Produces:
        - exports/maya_metadata.json (consolidated)
        - exports/assets.json
        - exports/metadata.json
        - exports/elements.json
        - exports/primitives.json
        - exports/cameras.json
        - exports/lights.json
    """

    # ------------------------------------------------------------
    # 1. ASSETS (from OBJ/MTL/HIER)
    # ------------------------------------------------------------
    assets = assets_df.to_dict(orient="records") if assets_df is not None else []

    _write_export_json(assets, "assets.json")

    # ------------------------------------------------------------
    # 2. METADATA (from JSON_ROOT)
    # ------------------------------------------------------------
    metadata = metadata_df.to_dict(orient="records") if metadata_df is not None else []
    _write_export_json(metadata, "metadata.json")

    # ------------------------------------------------------------
    # 3. PBRT ELEMENT JSON (json/<element>/<element>.json)
    # ------------------------------------------------------------
    elements = {}
    if JSON_ROOT.exists():
        for element_dir in JSON_ROOT.iterdir():
            if element_dir.is_dir():
                element_json = element_dir / f"{element_dir.name}.json"
                if element_json.exists():
                    try:
                        with open(element_json, "r") as f:
                            elements[element_dir.name] = json.load(f)
                    except Exception as e:
                        print(f"[export] Error reading element JSON {element_json}: {e}")

    _write_export_json(elements, "elements.json")

    # ------------------------------------------------------------
    # 4. PBRT PRIMITIVE JSON (nested inside element JSON)
    # ------------------------------------------------------------
    primitives = {}
    for elem_name, elem_dict in elements.items():
        if "instancedPrimitiveJsonFiles" in elem_dict:
            for prim_name, prim_info in elem_dict["instancedPrimitiveJsonFiles"].items():
                prim_file = prim_info.get("jsonFile")
                if prim_file:
                    try:
                        with open(os.path.join(JSON_ROOT, prim_file), "r") as f:
                            primitives[f"{elem_name}/{prim_name}"] = json.load(f)
                    except Exception:
                        pass

    _write_export_json(primitives, "primitives.json")

    # ------------------------------------------------------------
    # 5. CAMERAS
    # ------------------------------------------------------------
    cameras = {}
    cam_dir = JSON_ROOT / "cameras"
    if cam_dir.exists():
        for cam_file in cam_dir.glob("*.json"):
            try:
                with open(cam_file, "r") as f:
                    cameras[cam_file.stem] = json.load(f)
            except Exception:
                pass

    _write_export_json(cameras, "cameras.json")

    # ------------------------------------------------------------
    # 6. LIGHTS
    # ------------------------------------------------------------
    lights = {}
    lights_file = JSON_ROOT / "lights" / "lights.json"
    if lights_file.exists():
        try:
            with open(lights_file, "r") as f:
                lights = json.load(f)
        except Exception:
            pass

    _write_export_json(lights, "lights.json")

    # ------------------------------------------------------------
    # 7. CONSOLIDATED EXPORT
    # ------------------------------------------------------------
    consolidated = {
        "timestamp": datetime.datetime.now().isoformat(),
        "paths": {
            "MOANA_ROOT": MOANA_ROOT.as_posix(),
            "JSON_ROOT": JSON_ROOT.as_posix(),
            "OBJ_ROOT": OBJ_ROOT.as_posix(),
        },
        "assets": assets,
        "metadata": metadata,
        "elements": elements,
        "primitives": primitives,
        "cameras": cameras,
        "lights": lights,
    }

    _write_export_json(consolidated, "maya_metadata.json")

    print("[export] Maya metadata export complete.")

def load_all(force: bool = False):
    """
    Advanced, production-grade loader with caching and simple change detection.

    - Uses cached results if available and the dataset hash hasn't changed.
    - Recomputes only missing or invalidated pieces.
    - `force=True` forces a full rebuild and cache overwrite.

    Returns:
        metadata (DataFrame),
        assets (DataFrame),
        tree_df (DataFrame),
        kpis (dict),
        treemap_data (dict).
    """

    # --------------------------------------------------
    # 0. CHANGE DETECTION (JSON_ROOT + OBJ_ROOT)
    # --------------------------------------------------
    json_hash = _compute_dir_hash(JSON_ROOT)
    obj_hash = _compute_dir_hash(OBJ_ROOT)

    current_manifest = {
        "json_hash": json_hash,
        "obj_hash": obj_hash,
    }

    old_manifest = _load_manifest()
    dataset_changed = (
        old_manifest.get("json_hash") != json_hash
        or old_manifest.get("obj_hash") != obj_hash
    )

    # If forced or dataset changed, we clear all caches
    if force or dataset_changed:
        clear_cache()
        # Recreate cache dir because clear_cache may remove it
        os.makedirs(CACHE_DIR, exist_ok=True)
        # We'll recompute everything and then save a new manifest.

    # --------------------------------------------------
    # 1. METADATA
    # --------------------------------------------------
    if os.path.exists(META_CACHE):
        metadata = _load_feather(META_CACHE)
    else:
        metadata = load_metadata_json()
        if metadata is None:
            metadata = pd.DataFrame()
        _save_feather(metadata, META_CACHE)

    # --------------------------------------------------
    # 2. ASSETS
    # --------------------------------------------------
    if os.path.exists(ASSET_CACHE):
        assets = _load_feather(ASSET_CACHE)
    else:
        assets = load_obj_families()
        if assets is None:
            assets = pd.DataFrame()
        _save_feather(assets, ASSET_CACHE)

    # --------------------------------------------------
    # 3. TREE STRUCTURE
    # --------------------------------------------------
    if os.path.exists(TREE_CACHE):
        tree_df = _load_feather(TREE_CACHE)
    else:
        tree_df = build_tree_structure()
        if tree_df is None:
            tree_df = pd.DataFrame()
        _save_feather(tree_df, TREE_CACHE)

    # --------------------------------------------------
    # 4. TREEMAP DATA
    # --------------------------------------------------
    if os.path.exists(TREEMAP_CACHE):
        treemap_data = _load_json(TREEMAP_CACHE)
    else:
        treemap_data = prepare_treemap_data(assets)
        _save_json(treemap_data, TREEMAP_CACHE)

    # --------------------------------------------------
    # 5. KPIs
    # --------------------------------------------------
    if os.path.exists(KPI_CACHE):
        kpis = _load_json(KPI_CACHE)
    else:
        kpis = compute_kpis(assets, metadata)
        _save_json(kpis, KPI_CACHE)

    # --------------------------------------------------
    # 6. SAVE MANIFEST (for future change detection)
    # --------------------------------------------------
    _save_manifest(current_manifest)

    # 7. EXPORT MAYA METADATA (only when rebuild happens)
    if force or dataset_changed:
        export_maya_metadata(assets, metadata)

    return metadata, assets, tree_df, kpis, treemap_data
