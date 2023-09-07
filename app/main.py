import sys
import os
import zlib


def main():
    # You can use print statements as follows for debugging, they'll be visible when running tests.
    # print("Logs from your program will appear here!")

    # Uncomment this block to pass the first stage
    command = sys.argv[1]
    if command == "init":
        os.mkdir(".git")
        os.mkdir(".git/objects")
        os.mkdir(".git/refs")
        with open(".git/HEAD", "w") as f:
            f.write("ref: refs/heads/master\n")
        print("Initialized git directory")
    elif command.startswith("cat-file"):
        hash = sys.argv[3]
        directory, file = hash[:2], hash[2:]
        with open(f".git/objects/{directory}/{file}", "rb") as f:
            decompressed = zlib.decompress(f.read())
            x = decompressed.find(b" ")
            # fmt = decompressed[:x]
            y = decompressed.find(b"\x00", x)
            # size = int(decompressed[x:y].decode("ascii"))
            print(decompressed[y + 1 :].decode("ascii"), end="")
    else:
        raise RuntimeError(f"Unknown command #{command}")


if __name__ == "__main__":
    main()
