#!/usr/bin/env python

import numpy as np
import os
with open("./cg.gro","r") as f:
    cg = f.readlines()

resid = np.array([x[:5] for x in cg[2:-2]])
resn = np.array([x[5:10] for x in cg[2:-2]])
name = np.array([x[10:15] for x in cg[2:-2]])
atomID = np.array([x[15:20] for x in cg[2:-2]])
coords = np.array([[float(x[20:-1][:8]),float(x[20:-1][8:16]),float(x[20:-1][16:])] for x in cg[2:-2]])

ZN_coords = coords[np.where(resn == " ZN  ")[0]][0]
ZN_index = int(atomID[np.where(resn == " ZN  ")[0]][0])

HIS_id = np.where(resn == "HIS  ")[0]

close_atoms = []
for i in HIS_id:
    temp_coords = np.square(coords[i] - ZN_coords)
    if np.sqrt(sum(temp_coords)) < 0.5:
        close_atoms += [i]

SC2_list = [int(atomID[x]) for x in close_atoms if name[x] == " SC2 "]
other_list = [int(atomID[x]) for x in close_atoms if atomID[x] not in SC2_list]

index_cmd = ["gmx make_ndx -f cg.gro -o index.ndx << EOD\n",
             "1 | 13\n",
             "name 22 protein_ION\n",
             "14 | 15 | 16\n",
             "name 23 solute\n",
             "a {}\n".format(int(ZN_index))]

for i in SC2_list:
    index_cmd.append("a {}\n".format(i))

for i in other_list:
    index_cmd.append("a {}\n".format(i))

index_cmd += ["q\n","EOD\n"]

with open("index.sh","w") as f:
    for line in index_cmd:
        f.writelines(line)

#### Generate Instructions for pull groups

n_groups = len(SC2_list)+1#+other_list)+1
n_coords = n_groups-1

pull_code = ["; Pull code\n",
            "pull = yes\n",
            "pull-ngroups = {}\n".format(n_groups),
            "pull-ncoords = {}\n".format(n_coords),
            "pull-group1-name = a_{}\n".format(ZN_index) ]
for i,index in enumerate(SC2_list):#+other_list):
    pull_code.append("pull-group{}-name = a_{}\n".format(i+2, index))

pull_code+=["\n","\n"]


for i,index in enumerate(SC2_list):
    pull_code += ["pull-coord{}-type = umbrella\n".format(i+1),
                "pull-coord{}-geometry = distance ; simple distance increase\n".format(i+1),
                "pull-coord{}-groups = 1 {}\n".format(i+1, i+2 ),
                "pull-coord{}-dim = Y Y Y\n".format(i+1),
                "pull-coord{}-rate = 0.00 ; not pull, just distance restraint at a reference\n".format(i+1),
                ";distance bw 2 groups\n",
                "pull-coord{}-k = 10000 ; kJ mol^-1 nm^-2\n".format(i+1),
                "pull-coord{}-start = yes ; define initial COM distance > 0\n".format(i+1),
                "\n"]


##### Constrain distances between other beads in HIS residues

#for i,index in enumerate(other_list):
#    pull_code += ["pull-coord{}-type = umbrella\n".format(i+len(SC2_list)+1),
#                "pull-coord{}-geometry = distance ; simple distance increase\n".format(i+len(SC2_list)+1),
#                "pull-coord{}-groups = 1 {}\n".format(i+len(SC2_list)+1, i+2 ),
#                "pull-coord{}-dim = Y Y Y\n".format(i+len(SC2_list)+1),
#                "pull-coord{}-rate = 0.00 ; not pull, just distance restraint at a reference\n".format(i+len(SC2_list)+1),
#                ";distance bw 2 groups\n",
#                "pull-coord{}-k = 1000 ; kJ mol^-1 nm^-2\n".format(i+len(SC2_list)+1),
#                "pull-coord{}-start = yes ; define initial COM distance > 0\n".format(i+len(SC2_list)+1),
#                "\n"]
    

##### Generate minimisation input mdp

with open("../template_mdp_files/minim_template.mdp","r") as f:
    mdp = f.readlines()

mdp+=pull_code

with open("./minim.mdp","w") as f:
    for line in mdp:
        f.writelines(line)

#### Generate equilibration input mdp

with open("../template_mdp_files/nvt_template.mdp","r") as f:
    mdp = f.readlines()

mdp+=pull_code

with open("./nvt.mdp","w") as f:
    for line in mdp:
        f.writelines(line)

with open("../template_mdp_files/npt_template.mdp","r") as f:
    mdp = f.readlines()

mdp+=pull_code

with open("./npt.mdp","w") as f:
    for line in mdp:
        f.writelines(line)

#### Generate MD input mdp

with open("../template_mdp_files/md_template.mdp","r") as f:
    mdp = f.readlines()

mdp+=pull_code

with open("./md.mdp","w") as f:
    for line in mdp:
        f.writelines(line)
