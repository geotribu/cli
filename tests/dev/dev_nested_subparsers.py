import argparse

parser = argparse.ArgumentParser()

subparsers = parser.add_subparsers(dest="parser")

host_cmd = subparsers.add_parser("host")

host_subparsers = host_cmd.add_subparsers(dest="parser_host")

host_add_cmd = host_subparsers.add_parser("add")
host_add_cmd.add_argument("ip")

host_remove_cmd = host_subparsers.add_parser("remove")
host_remove_cmd.add_argument("ip")

args = parser.parse_args()
print(args)

if args.parser == "host":
    if args.parser_host == "add":
        print("add host:", args.ip)
    elif args.parser_host == "remove":
        print("remove host:", args.ip)
