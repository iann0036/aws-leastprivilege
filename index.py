import argparse
from rolegen import RoleGen, InvalidArguments, InvalidTemplate


def main(args):
    rolegen = RoleGen(args)
    rolegen.generate()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument("-i", "--input-filename",
                        action="store", dest="input_file")
    parser.add_argument("--stack-name", action="store", dest="stack_name")
    parser.add_argument("--skip-update-policy", action="store_true", dest="skip_update_policy", default=False)
    parser.add_argument("--region", action="store", dest="region")

    args = parser.parse_args()
    try:
        main(args)
    except InvalidArguments as e:
        print("ERROR: {}\n".format(e))
        parser.print_usage()
    except InvalidTemplate as e:
        print("ERROR: {}\n".format(e))
        parser.print_usage()
