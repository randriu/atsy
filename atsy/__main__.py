import atsy


def main():
    print(f"this is atsy v.{atsy.__version__}")
    ats = atsy.read("data/nand.tar.gz")
    print(ats.num_states)


if __name__ == "__main__":
    main()
