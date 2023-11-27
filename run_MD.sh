for file in ./proteins/*
	do
	filename="${file##*/}"
	echo $filename
	dirname="${filename%%.*}"
	echo $dirname
	cd $dirname
    for i in {0..9}
            do
            gmx grompp -f minim.mdp -c cg.gro -n index.ndx -p topol.top -o em.tpr -maxwarn 4
            gmx mdrun -s em.tpr -deffnm em$i -v

            gmx grompp -f nvt.mdp -c em$i.gro -n index.ndx -p topol.top -o nvt.tpr -maxwarn 4
            gmx mdrun -s nvt.tpr -deffnm nvt$i -v

            gmx grompp -f npt.mdp -c nvt$i.gro -t nvt$i.cpt -n index.ndx -p topol.top -o npt.tpr -maxwarn 4
            gmx mdrun -s npt.tpr -deffnm npt$i -v

            gmx grompp -f md.mdp -c npt$i.gro -t npt$i.cpt -n index.ndx -p topol.top -o md.tpr -maxwarn 4
            gmx mdrun -s md.tpr -deffnm md$i -v
            done

    cd ../
    done