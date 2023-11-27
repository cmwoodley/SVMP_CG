

for file in ./proteins/*
	do
	filename="${file##*/}"
	echo $filename
	dirname="${filename%%.*}"
	echo $dirname
	mkdir $dirname
	cd $dirname
	
	grep ZN ../proteins/$filename >> ZN.pdb
	grep ATOM ../proteins/$filename >> clean.pdb

	martinize2 -f clean.pdb -x cg.pdb -o topol.top -scfix -p backbone -dssp dssp -elastic -p all -pf 1000 -ef 400 -el 0.5 -eu 0.9

	python ../add_zn.py ZN.pdb cg.pdb

	echo 0 | gmx genrestr -f ZN.pdb -o posre_ZN.itp -fc 1000 1000 1000

	echo '#include "../martini_v300/martini_v3.0.0.itp"
	#include "../martini_v300/martini_v3.0.0_ions_v1.itp"
	#include "../martini_v300/martini_v3.0.0_solvents_v1.itp"
	#include "molecule_0.itp"
	#ifdef POSRES
	#include "posre_protein.itp"
	#endif

	#ifdef POSRES
	#include "posre_ZN.itp"
	#endif

	[ system ]
	Title of the system

	[ molecules ]
	molecule_0    1
	ZN		1' > topol.top

	python ../insane.py -f cg_ZN.pdb -o cg.gro -pbc cubic -d 2.0 -salt 0.15 -charge auto -sol W -p topol_temp.top

	echo 1 | gmx genrestr -f cg.gro -o posre_protein.itp -fc 1000 1000 1000

	tail -3 topol_temp.top >> topol.top
	rm topol_temp.top

	python ../setup_mdp.py

	bash index.sh
	
	cd ../
	done
