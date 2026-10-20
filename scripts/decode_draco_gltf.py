"""Decode a Draco-only embedded CAD glTF before processing it with gltfpack.

Requires DracoPy and numpy. Writes an intermediate .gltf and sibling .bin;
keep both outside the website. The source export is never changed.
"""

import argparse
import base64
import json
from pathlib import Path

import DracoPy
import numpy as np


def decode(source, destination):
    document = json.loads(source.read_text(encoding="utf-8"))
    if document.get("images") or document.get("animations") or document.get("skins"):
        raise ValueError("This converter expects a static CAD export without textures or skins")
    if any("bufferView" in a or "sparse" in a for a in document["accessors"]):
        raise ValueError("This converter expects Draco-only accessors")

    buffers = []
    for buffer in document["buffers"]:
        uri = buffer["uri"]
        if not uri.startswith("data:") or ";base64," not in uri:
            raise ValueError("This converter expects embedded base64 buffers")
        buffers.append(base64.b64decode(uri.split(",", 1)[1]))
    source_views = document["bufferViews"]
    document["bufferViews"] = []
    binary_path = destination.with_suffix(".bin")
    component_types = {5120: "i1", 5121: "u1", 5122: "<i2", 5123: "<u2", 5125: "<u4", 5126: "<f4"}
    written_accessors = set()
    primitive_count = 0

    with binary_path.open("wb") as binary:
        def write_accessor(index, values, target):
            if index in written_accessors:
                raise ValueError("Unexpected shared Draco accessor")
            written_accessors.add(index)
            accessor = document["accessors"][index]
            values = np.asarray(values, dtype=component_types[accessor["componentType"]])
            # Draco can merge identical vertices; the decoded topology is authoritative.
            accessor["count"] = len(values)
            binary.write(b"\0" * (-binary.tell() % 4))
            offset = binary.tell()
            data = values.tobytes()
            binary.write(data)
            accessor["bufferView"] = len(document["bufferViews"])
            accessor.pop("byteOffset", None)
            if "min" in accessor:
                accessor["min"] = np.atleast_1d(values.min(axis=0)).tolist()
                accessor["max"] = np.atleast_1d(values.max(axis=0)).tolist()
            document["bufferViews"].append({
                "buffer": 0, "byteOffset": offset, "byteLength": len(data), "target": target,
            })

        for mesh in document["meshes"]:
            for primitive in mesh["primitives"]:
                extension = primitive.get("extensions", {}).get("KHR_draco_mesh_compression")
                if extension is None:
                    raise ValueError("Expected Draco compression on every primitive")
                view = source_views[extension["bufferView"]]
                start = view.get("byteOffset", 0)
                mesh_data = DracoPy.decode(buffers[view["buffer"]][start:start + view["byteLength"]])
                for name, unique_id in extension["attributes"].items():
                    attribute = mesh_data.get_attribute_by_unique_id(unique_id)
                    write_accessor(primitive["attributes"][name], attribute["data"], 34962)
                write_accessor(primitive["indices"], mesh_data.faces.reshape(-1), 34963)
                del primitive["extensions"]["KHR_draco_mesh_compression"]
                if not primitive["extensions"]:
                    del primitive["extensions"]
                primitive_count += 1
                if primitive_count % 5000 == 0:
                    print(f"Decoded {primitive_count:,} primitives", flush=True)

        document["buffers"] = [{"uri": binary_path.name, "byteLength": binary.tell()}]

    for key in ("extensionsUsed", "extensionsRequired"):
        if key in document:
            document[key] = [e for e in document[key] if e != "KHR_draco_mesh_compression"]
            if not document[key]:
                del document[key]
    destination.write_text(json.dumps(document, separators=(",", ":")), encoding="utf-8")
    print(f"Decoded {primitive_count:,} primitives to {destination}", flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("destination", type=Path)
    arguments = parser.parse_args()
    if arguments.source.resolve() == arguments.destination.resolve():
        parser.error("Destination must differ from the original export")
    decode(arguments.source, arguments.destination)
