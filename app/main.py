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
    return file_hash


def ls_tree(hash):
    directory, file = hash[:2], hash[2:]
    with open(f".git/objects/{directory}/{file}", "rb") as f:
        decompressed = zlib.decompress(f.read())
        matches = re.findall(b" ([^\\x00]*)\\x00", decompressed)[1:]
        print("\n".join(match.split(b" ")[-1].decode("ascii") for match in matches))

def write_tree(path):
    if os.path.isfile(path):
        return hash_object(path)
    entries = sorted(os.listdir(path), key=lambda x: x if os.path.isfile(os.path.join(path, x)) else f"{x}/")
    tree = b""
    for entry in entries:
        if entry == ".git":
            continue
        full_path = os.path.join(path, entry)
        if os.path.isfile(full_path):
            tree += f"100644 {entry}\0".encode()
        else:
            tree += f"40000 {entry}\0".encode()
        hash = int.to_bytes(int(write_tree(full_path), base=16), length=20)
        tree += hash
    tree = f"tree {len(tree)}\0".encode() + tree
    tree_hash = hashlib.sha1(tree).hexdigest()
    directory, file = tree_hash[:2], tree_hash[2:]
    if not os.path.exists(f".git/objects/{directory}"):
        os.mkdir(f".git/objects/{directory}")
    with open(f".git/objects/{directory}/{file}", "wb") as f:
        f.write(zlib.compress(tree))
    return tree_hash

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
            print(hash_object(filename))
        case "ls-tree":
            hash = sys.argv[3]
            ls_tree(hash)
        case "write-tree":
            print(write_tree("."))
        case _:
            raise RuntimeError(f"Unknown command #{command}")


if __name__ == "__main__":
    main()
