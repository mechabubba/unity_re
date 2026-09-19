from unityparser import UnityDocument

def handle_uid_discontinuities(args):
    if args.target.is_dir():
        print("error: one file at a time")
        sys.exit(1)
    uid_discontinuities(args.target)

def uid_discontinuities(target):
    doc = UnityDocument.load_yaml(target)

    last = 0
    discontinuities = []

    for entry in doc.entries:
        now = int(entry.anchor)
        if (last + 1) != now:
            discontinuities.append((last, now))
        last = now

    if not discontinuities:
        print("no discontinuities :)")
    else:
        for d in discontinuities:
            print(f"{d[0]} > {d[1]}")
