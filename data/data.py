import os
import json
import pandas as pd

MOANA_ROOT = "D:/Downloads/island/"

def load_metadata():
    metadata_path = os.path.join(MOANA_ROOT, "json")
    rows = []

    for file in os.listdir(metadata_path):
        if file.endswith(".json"):
            with open(os.path.join(metadata_path, file)) as f:
                data = json.load(f)
                rows.append(data)

    return pd.DataFrame(rows)


def load_assets():
    assets_path = os.path.join(MOANA_ROOT, "obj")
    rows = []

    for root, dirs, files in os.walk(assets_path):
        for file in files:
            if file.endswith((".obj", ".fbx", ".usd", ".gltf")):
                rows.append({
                    "name": file,
                    "path": os.path.join(root, file),
                    "folder": os.path.basename(root),
                    "type": detect_asset_type(file),
                })

    return pd.DataFrame(rows)


def detect_asset_type(filename):
    if "LOD" in filename:
        return "LOD"
    if filename.endswith(".usd"):
        return "USD"
    if filename.endswith(".fbx"):
        return "FBX"
    return "Unknown"


def build_tree_structure():
    tree = []

    for root, dirs, files in os.walk(MOANA_ROOT):
        rel = os.path.relpath(root, MOANA_ROOT)
        tree.append({
            "name": rel,
            "children": dirs + files
        })

    return tree


def compute_kpis(asset_df, metadata_df):
    return {
        "total_assets": len(asset_df),
        "total_characters": len(metadata_df[metadata_df["category"] == "character"]),
        "total_props": len(metadata_df[metadata_df["category"] == "prop"]),
        "total_environments": len(metadata_df[metadata_df["category"] == "environment"]),
    }


def load_all():
    metadata = load_metadata()
    assets = load_assets()
    tree = build_tree_structure()
    kpis = compute_kpis(assets, metadata)

    return metadata, assets, tree, kpis
