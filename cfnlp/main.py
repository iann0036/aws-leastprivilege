import argparse
from .rolegen import RoleGen, InvalidArguments, InvalidTemplate


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument("-i", "--input-filename", action="store", dest="input_file")
    parser.add_argument("--stack-name", action="store", dest="stack_name")
    parser.add_argument("--include-update-actions", action="store_true", dest="include_update_actions", default=False)
    parser.add_argument("--consolidate-policy", action="store_true", dest="consolidate_policy", default=False)
    parser.add_argument("--profile", action="store", dest="profile")
    parser.add_argument("--region", action="store", dest="region")

    args = parser.parse_args()
    try:
        rolegen = RoleGen(args)
        policy = rolegen.generate()
        print(policy)
    except InvalidArguments as e:
        print("ERROR: {}\n".format(e))
        parser.print_usage()
    except InvalidTemplate as e:
        print("ERROR: {}\n".format(e))
        parser.print_usage()


if __name__ == "__main__":
    main()
