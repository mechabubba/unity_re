import re
from unityparser import UnityDocument
from util import Util

# used by unity-included legacy shaders, there may be more
# actual shader used is defined by fileID
# probably needs some more research
UNITY_BUILTIN_GUIDS = [
    "0000000000000000e000000000000000",
    "0000000000000000f000000000000000",
]

def handle_find_shaders(args):
    targets = []
    root = args.target.parent if not args.target.is_dir else args.target

    if args.target.is_dir():
        if not args.recurse:
            print("no")
            sys.exit(1)
        # get a list of shit to search for
        targets.extend(list(root.rglob("*.mat")))
        targets.extend(list(root.rglob("*.unity")))
    else:
        targets.append(args.target)
    
    guids = Util.map_guids(root, flat=True)
    find_shaders(targets, guids, root)

def find_shaders(targets, guids, root):
    shader_def = re.compile(r"(.*[Ss]hader.*)") # this may not be representative of all shader entries, requires more research
    total = set()

    for target in targets:
        doc = UnityDocument.load_yaml(target)
        if target.suffix == ".unity":
            # whatever
            entries = doc.filter(class_names=("MonoBehaviour",))
        else:
            entries = doc.entries
        shaders = set()

        for entry in entries:
            props = entry.get_serialized_properties_dict()
            for key in props:
                name = shader_def.match(key)
                if name is not None:
                    if not isinstance(props[key], dict):
                        # false alarm
                        continue

                    file_guid = props[key]["guid"]
                    if file_guid in guids:
                        shaders.add(str(guids[file_guid].relative_to(root.parent)))
                    elif file_guid in UNITY_BUILTIN_GUIDS:
                        # shrug
                        shaders.add(f"Legacy Shader (fileID: {props[key]["fileID"]})")
                    elif file_guid is None:
                        print("shader found with no guid? &{entry.anchor} in {target}")
                        shaders.add("None?")
                    else:
                        shaders.add(f"Unknown shader ({file_guid})")

        if bool(shaders):
            print(target)
            print("\n".join(sorted(shaders)))
            print()

        total = shaders | total

    print("Total unique shaders;")
    print("\n".join(sorted(total)))
    return total
