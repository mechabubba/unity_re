import re
from uuid import uuid4

class Util:
    @staticmethod
    def map_guids(root, flat=False):
        """
        map the guid's of a project directory. returns a dict tree.

        @warning about the `flat` parameter: _unk_ keys could potentially overlap eachother
        there aren't a lot of them in my project so ignoring the problem and keeping the uid char limit bumped up for now.
        this is potentially solvable with a different uuid standard, or ill have to just introduce manual namespacing
        """
        guids = {}
        unk_uids = []

        guid_re = re.compile(r"guid:\s(.*)") # this is probably faster than a yaml processor... if other properties are needed can implement

        def uid(chr=8):
            """
            get a unique X char id
            """
            while (k := f"{{:0{chr}x}}".format(uuid4().int & ((2 ** (4 * chr)) - 1))) in unk_uids:
                continue
            unk_uids.append(k)
            return k

        def check_guid(meta):
            """
            attempt to get the guid of the provided file.
            """
            with open(meta, "r") as f:
                guid = guid_re.search(f.read())
                if guid is None:
                    print(f"no guid found? @ '{meta}' (this file will be omitted from the tree!)")
                    return None
                return guid.group(1)

        for item in root.iterdir():
            if item.is_dir():
                _guids = Util.map_guids(item)

                meta = item.with_name(item.name + ".meta")
                if meta.exists():
                    guid = check_guid(meta)
                else:
                    guid = uid()

                if guid:
                    guids[guid] = _guids

            elif item.is_file():
                if item.suffix == ".meta":
                    # ignore these... meta files don't have metadata
                    # deciding to search for all files so i can index those without meta files (under what circumstances do these exist???)
                    continue

                meta = item.with_name(item.name + ".meta")
                if meta.exists():
                    guid = check_guid(meta)
                    if guid:
                        guids[guid] = item
                else:
                    guids[f"_unk_{uid()}_"] = item

        if flat:
            # flatten that john for search time reasons
            def flatten(d):
                """
                flatten flattens!
                """
                neu = {}
                for k, v in d.items():
                    if isinstance(v, dict):
                        fl = flatten(v)
                        for _k, _v in fl.items():
                            neu[_k] = _v
                    else:
                        neu[k] = v
                return neu

            guids = flatten(guids)

        return guids
