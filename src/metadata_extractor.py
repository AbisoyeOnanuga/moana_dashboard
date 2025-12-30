import os
import json
import csv

# ---------------------------------------------------------
# Utility functions
# ---------------------------------------------------------

def read_json(path):
    with open(path, "r") as f:
        return json.load(f)


def count_obj_faces(obj_path):
    """Count faces in an OBJ file by scanning for 'f ' lines."""
    face_count = 0
    try:
        with open(obj_path, "r", errors="ignore") as f:
            for line in f:
                if line.startswith("f "):
                    face_count += 1
    except FileNotFoundError:
        return None
    return face_count


def get_file_size_mb(path):
    """Return file size in MB."""
    if not os.path.isfile(path):
        return None
    return os.path.getsize(path) / (1024 * 1024)

def resolve_obj_path(obj_rel, dataset_root, obj_root, element_name):
    """
    Normalize OBJ paths from the Moana JSON.
    Handles cases where JSON paths already include 'obj/...'.
    """
    # Normalize slashes
    obj_rel = obj_rel.replace("\\", "/")

    # Case 1: JSON already gives a full relative path like "obj/isBeach/file.obj"
    if obj_rel.startswith("obj/"):
        obj_path = os.path.join(dataset_root, obj_rel)

    # Case 2: JSON gives only a filename like "isBeach_main.obj"
    else:
        obj_path = os.path.join(obj_root, element_name, obj_rel)

    # Normalize final path for Windows/Linux
    return os.path.normpath(obj_path)

# ---------------------------------------------------------
# Extraction logic
# ---------------------------------------------------------

def extract_main_geometry(element_name, elem_dict, dataset_root, obj_root):
    """Extract metadata for the main geometry of an element."""
    rows = []

    obj_rel = elem_dict.get("geomObjFile")
    if not obj_rel:
        return rows

    obj_path = resolve_obj_path(obj_rel, dataset_root, obj_root, element_name)
    poly_count = count_obj_faces(obj_path)
    file_size = get_file_size_mb(obj_path)
    instance_count = len(elem_dict.get("instancedCopies", [])) or 1

    rows.append({
        "asset_name": f"{element_name}_main",
        "asset_type": "main",
        "poly_count": poly_count,
        "file_size_mb": file_size,
        "instance_count": instance_count,
        "scene_name": element_name,
        "location": obj_path
    })

    return rows


def extract_variants(element_name, elem_dict, dataset_root, obj_root):
    """Extract metadata for variant geometries."""
    rows = []
    variants = elem_dict.get("variants", {})

    for variant_name, vdict in variants.items():
        obj_rel = vdict.get("geomObjFile")
        if not obj_rel:
            continue

        obj_path = resolve_obj_path(obj_rel, dataset_root, obj_root, element_name)
        poly_count = count_obj_faces(obj_path)
        file_size = get_file_size_mb(obj_path)
        instance_count = len(vdict.get("instancedCopies", [])) or 1

        rows.append({
            "asset_name": f"{element_name}_{variant_name}",
            "asset_type": "variant",
            "poly_count": poly_count,
            "file_size_mb": file_size,
            "instance_count": instance_count,
            "scene_name": element_name,
            "location": obj_path
        })

    return rows


def extract_primitives(element_name, elem_dict, dataset_root, json_root, obj_root):
    """Extract metadata for instanced primitives."""
    rows = []
    primitives = elem_dict.get("instancedPrimitiveJsonFiles", {})

    for prim_name, pinfo in primitives.items():
        prim_json = os.path.join(json_root, element_name, f"{element_name}_{prim_name}.json")
        if not os.path.isfile(prim_json):
            continue

        prim_dict = read_json(prim_json)
        prim_type = pinfo.get("type")

        # Archive primitives contain OBJ references
        if prim_type == "archive":
            for archive_path, instances in prim_dict.items():
                obj_path = resolve_obj_path(archive_path, dataset_root, obj_root, element_name)
                poly_count = count_obj_faces(obj_path)
                file_size = get_file_size_mb(obj_path)
                instance_count = len(instances)

                rows.append({
                    "asset_name": f"{element_name}_{prim_name}",
                    "asset_type": "archive_primitive",
                    "poly_count": poly_count,
                    "file_size_mb": file_size,
                    "instance_count": instance_count,
                    "scene_name": element_name,
                    "location": obj_path
                })

        # Curve primitives have no OBJ
        elif prim_type == "curve":
            rows.append({
                "asset_name": f"{element_name}_{prim_name}",
                "asset_type": "curve_primitive",
                "poly_count": None,
                "file_size_mb": None,
                "instance_count": len(prim_dict),
                "scene_name": element_name,
                "location": None
            })

        # Element primitives reference variants or nested elements
        elif prim_type == "element":
            for variant_name, instances in prim_dict.items():
                rows.append({
                    "asset_name": f"{element_name}_{prim_name}_{variant_name}",
                    "asset_type": "element_primitive",
                    "poly_count": None,
                    "file_size_mb": None,
                    "instance_count": len(instances),
                    "scene_name": element_name,
                    "location": None
                })

    return rows


# ---------------------------------------------------------
# Main dataset walker
# ---------------------------------------------------------

def walk_dataset(dataset_root):
    json_root = os.path.join(dataset_root, "json")
    obj_root = os.path.join(dataset_root, "obj")

    all_rows = []

    for element_name in os.listdir(json_root):
        element_folder = os.path.join(json_root, element_name)
        if not os.path.isdir(element_folder):
            continue

        element_json = os.path.join(element_folder, f"{element_name}.json")
        if not os.path.isfile(element_json):
            continue

        elem_dict = read_json(element_json)

        # Extract all metadata
        all_rows.extend(extract_main_geometry(element_name, elem_dict, dataset_root, obj_root))
        all_rows.extend(extract_variants(element_name, elem_dict, dataset_root, obj_root))
        all_rows.extend(extract_primitives(element_name, elem_dict, dataset_root, json_root, obj_root))

    return all_rows


# ---------------------------------------------------------
# CSV writer
# ---------------------------------------------------------

def write_csv(rows, output_path):
    if not rows:
        print("No metadata extracted.")
        return

    fieldnames = list(rows[0].keys())

    with open(output_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"Metadata written to {output_path}")


# ---------------------------------------------------------
# Entry point
# ---------------------------------------------------------

if __name__ == "__main__":
    dataset_root = "D:/Downloads/island/"   # <-- update this path
    output_path = "../data/moana_metadata.csv"

    rows = walk_dataset(dataset_root)
    write_csv(rows, output_path)
