import sys
from pathlib import Path
import trimesh

def main():
    if len(sys.argv) < 2:
        print("Usage: python obj_to_glb.py <path/to/file.obj>")
        raise SystemExit(2)

    obj_path = Path(sys.argv[1]).expanduser().resolve()
    if not obj_path.exists():
        print(f"ERR: OBJ not found: {obj_path}")
        raise SystemExit(1)

    glb_path = obj_path.with_suffix(".glb")
    mesh = trimesh.load_mesh(obj_path, process=False)
    mesh.export(glb_path)
    print(f"OK -> {glb_path}")

if __name__ == "__main__":
    main()
