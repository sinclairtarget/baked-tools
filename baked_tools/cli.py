import argparse

from . import MAINTAINER


def run():
    parser = argparse.ArgumentParser(f"""
Baked command-line tool for Shotgrid. For more help, contact {MAINTAINER}.
    """)
    subparsers = parser.add_subparsers(title="Subcommands")

    subparsers.add_parser(
        "upload", help="Upload media to Shotgrid"
    )

    args = parser.parse_args()

    print("Hello, world!")
