import pandas as pd
import argparse, sys
from pathlib import Path

import dnsd_to_yed

title = """\033[38;5;35m______ _   _  _____     _                           _            \n|  _  \ \ | |/  ___|   | |                         | |           \n| | | |  \| |\ `--.  __| |_   _ _ __ ___  _ __  ___| |_ ___ _ __ \n| | | | . ` | `--. \/ _` | | | | '_ ` _ \| '_ \/ __| __/ _ \ '__|\n| |/ /| |\  |/\__/ / (_| | |_| | | | | | | |_) \__ \ ||  __/ |   \n|___/ \_| \_/\____/ \__,_|\__,_|_| |_| |_| .__/|___/\__\___|_|   \n            __            ___________    | |                  \n            \ \          |  ___|  _  \   |_|                  \n  ___________\ \    _   _| |__ | | | |                      \n |____________  )  | | | |  __|| | | |                      \n             / /   | |_| | |___| |/ /                       \n            /_/     \__, \____/|___/                        \n                     __/ |                                  \n                    |___/                                   \033[000m"""
print(title)
print("")

parser = argparse.ArgumentParser(description="This program is intended to fill a gap in the Photon dnsdumpster functionality by downloading the .xlsx file generated with a dnsdumpster search and parsing it into a .graphml format that can be read (and exported as arbitrary other format) by the freeware yEd graph editor from yworks [https://www.yworks.com/products/yed]", epilog="For more information on the graphml standard, see [http://graphml.graphdrawing.org/primer/graphml-primer.html] or [http://graphml.graphdrawing.org/specification.html].")


group = parser.add_mutually_exclusive_group()
group.add_argument("-d", "--domain", metavar="DOMAIN.COM", type=str, dest="domain_flagged",
                    help="Domain to request from DNSdumpster. Explicitly invoking this flag is optional; the same functionality can be invoked flaglessly, i.e., 'dnsd_to_yed.py domain.com'")
group.add_argument("-f", "--file", metavar="FILE.XLSX", type=str,
                    help="Use an extant .xlsx file instead of downloading a new one from dnsdumpster")
group.add_argument("-lD", "--listdomains", metavar="FILE.TXT", type=str,
                    help="Request graphs of multiple domains. Domains should be passed as a textfile list with one requested domain per line.")
group.add_argument("-lF", "--listfiles", metavar="FILE.TXT", type=str,
                    help="Request graphs of multiple extant xlsx files. Filenames should be passed as a textfile with one filename per line.")

parser.add_argument("-x", "--savexlsx", action="store_true",
                    help="Default behaviour is to remove downloaded xlsx files after the graphml file has been created. The -x flag instructs the program to instead retain these files. Xlsx files specified using the -f or -lF flags will not be consumed regardless of the state of this flag.")


parser.add_argument('domain', metavar="DOMAIN.COM", type=str, nargs='*', help="A domain or list of domains.")


print(sys.argv)
try:
    args = parser.parse_args()
except BaseException: 
    sys.exit()

print(args)

def get_all_files(directory='.'):
    dirpath = Path(directory)
    assert dirpath.exists()
    file_list = []
    for x in dirpath.iterdir():
        if x.is_file() and x.suffix == '.xlsx':
            file_list.append(x)
        elif x.is_dir():
            file_list.extend(get_all_files(x))
    return file_list


prerun_files = get_all_files()
domain_list = []

if len(args.domain)>=1 and args.domain_flagged is None: # dnsd_to_yed.py domain1.com [domain2.com ...]
    domain_list = args.domain

elif len(args.domain)==0 and args.domain_flagged is not None: # dnsd_to_yed.py -d domain1.com
    domain_list = list(args.domain_flagged)

elif len(args.domain)>=1 and args.domain_flagged is not None: # eg, dnsd_to_yed.py -d domain1.com domain2.com
    domain_list = [args.domain_flagged]+args.domain

else: #i.e., no arguments were passed to domain
    if args.file is None and args.listdomains is None and args.listfiles is None:
        raise Exception("Interactive input is not yet implemented.")
    else: pass

if args.listdomains is not None:
    if Path(args.listdomains).is_file():
        with open(args.listdomains, "r") as f:
            linesread = f.readlines()
        linesread = [a.strip() for a in linesread]
        domain_list += linesread
        print(domain_list)
    else: 
        raise IOError("The file specified does not exist.")



if len(domain_list)>0:
    for domain in domain_list:
        filename = dnsd_to_yed._download_xlsx.dnsdumpster(domain)
        theFile = pd.read_excel(open(filename, 'rb'), header=0)
        dnsd_to_yed.main._main(theFile)


if args.file is not None:
    if Path(args.file).is_file():
        theFile = pd.read_excel(open(args.file,'rb'), header=0)
        dnsd_to_yed.main._main(theFile)

if args.listfiles is not None:
    print("Reading from list of files")
    if Path(args.listfiles).is_file():
        with open(args.listfiles, "r") as f:
            extant_xlsxs = f.readlines()
        extant_xlsxs = [a.strip() for a in extant_xlsxs]
        print(extant_xlsxs)
        for filename in extant_xlsxs:
            theFile = pd.read_excel(open(filename, 'rb'), header=0)
            dnsd_to_yed.main._main(theFile)

    else: 
        raise IOError("The file specified does not exist.")


postrun_files = get_all_files()
print(prerun_files, postrun_files)

for x in postrun_files:
    if x not in prerun_files:
        if not args.savexlsx:
            x.unlink()
            print(x.name +" deleted")



