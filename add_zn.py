#!/usr/bin/env python

import argparse

parser = argparse.ArgumentParser()

parser.add_argument("ZN",type=str)
parser.add_argument("cg",type=str)
args = parser.parse_args()

with open(args.ZN,"r") as f:
    ZN = f.readlines()

ZN = [x for x in ZN if "HETATM" in x]

with open(args.cg,"r") as f:
    cg = f.readlines()

for i,line in enumerate(cg):
    if line.find("TER") != -1: 
        coord_end = i
        break

mod = cg[:i]
mod += [ZN[0][:11]+" TD"+ZN[0][14:]]
mod += cg[i:]

with open("./cg_ZN.pdb", "w") as f:
    for line in mod:
        f.writelines(line)
