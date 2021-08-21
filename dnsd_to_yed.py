import pandas as pd
import argparse

import _download_xlsx, main

title = """\033[38;5;35m______ _   _  _____     _                           _            \n|  _  \ \ | |/  ___|   | |                         | |           \n| | | |  \| |\ `--.  __| |_   _ _ __ ___  _ __  ___| |_ ___ _ __ \n| | | | . ` | `--. \/ _` | | | | '_ ` _ \| '_ \/ __| __/ _ \ '__|\n| |/ /| |\  |/\__/ / (_| | |_| | | | | | | |_) \__ \ ||  __/ |   \n|___/ \_| \_/\____/ \__,_|\__,_|_| |_| |_| .__/|___/\__\___|_|   \n            __            ___________    | |                  \n            \ \          |  ___|  _  \   |_|                  \n  ___________\ \    _   _| |__ | | | |                      \n |____________  )  | | | |  __|| | | |                      \n             / /   | |_| | |___| |/ /                       \n            /_/     \__, \____/|___/                        \n                     __/ |                                  \n                    |___/                                   \033[000m"""
print(title)
print("")

parser = argparse.ArgumentParser(description="this is the top of the helptext before the help strings for the different options are listed")              ##
group = parser.add_mutually_exclusive_group()               ##
group.add_argument("-v", "--verbosity", type=int,           ##
                    help="increase output verbosity")       ##
group.add_argument("-v", "--verbosity", type=int,           ## these are all fairly obviously
                    help="increase output verbosity")       ## placeholders. Fix
                                                            ##
parser.add_argument("-v", "--verbose", action="store_true", ##
                    help="increase output verbosity")       ##
parser.add_argument("-v", "--verbosity", type=int,          ##
                    help="increase output verbosity")       ##

filename = _download_xlsx.dnsdumpster("google.com")
theFile = pd.read_excel(open(filename, 'rb'), header=0)
main.__main__(theFile)
