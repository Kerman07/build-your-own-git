import hashlib
import os
import re
import sys
import zlib


def initialize_git_directory():
    if not os.path.exists(".git"):
        os.mkdir(".git")
        os.mkdir(".git/objects")
        os.mkdir(".git/refs")
        with open(".git/HEAD", "w") as f:
            f.write("ref: refs/heads/master\n")
        print("Initialized git directory")
    else:
        print(".git directory already exists")


def cat_file(hash):
    directory, file = hash[:2], hash[2:]
    with open(f".git/objects/{directory}/{file}", "rb") as f:
        decompressed = zlib.decompress(f.read())
        x = decompressed.find(b" ")
        # fmt = decompressed[:x]
        y = decompressed.find(b"\x00", x)
        # size = int(decompressed[x:y].decode("ascii"))
        print(decompressed[y + 1 :].decode("ascii"), end="")


def hash_object(filename):
    with open(filename, "rb") as f:
        data = f.read()
        result = b"blob " + str(len(data)).encode() + b"\x00" + data
        file_hash = hashlib.sha1(result).hexdigest()
        directory, file = file_hash[:2], file_hash[2:]
        if not os.path.exists(f".git/objects/{directory}"):
            os.mkdir(f".git/objects/{directory}")
        with open(f".git/objects/{directory}/{file}", "wb") as nf:
            nf.write(zlib.compress(result))
    print(file_hash, end="")


def ls_tree(hash):
    directory, file = hash[:2], hash[2:]
    with open(f".git/objects/{directory}/{file}", "rb") as f:
        decompressed = zlib.decompress(f.read())
        matches = re.findall(b" ([^\\x00]*)\\x00", decompressed)[1:]
        print("\n".join(match.split(b" ")[-1].decode("ascii") for match in matches))

def main():
    command = sys.argv[1]
    match command:
        case "init":
            initialize_git_directory()
        case "cat-file":
            hash = sys.argv[3]
            cat_file(hash)
        case "hash-object":
            filename = sys.argv[3]
            hash_object(filename)
        case "ls-tree":
            hash = sys.argv[3]
            ls_tree(hash)
        case _:
            raise RuntimeError(f"Unknown command #{command}")


if __name__ == "__main__":
    main()
