project_root=$1
Genome=$2
bioproject=$3
sample_GSMs="$4"
control_GSMs="$5"
userID=`whoami`
HDsize=`lfs quota -u $userID ~/|tail -n 1|awk '{print $3}'`
nslot=4
prevT=`date +%s`
intT=1800

Logfile="$project_root/$Genome/$bioproject/$bioproject.log.txt"

for GSM in `echo $control_GSMs`; do
	Logfile="$project_root/$Genome/$bioproject/$GSM.log.txt"
	while :; do
		nQ=`qstat|tail -n +3| awk '{print $5}'|cut -c1|grep -cv -e "r"`
		curT=`date +%s`
		let difT=$curT-$prevT

		if [ $difT -gt $intT ]; then
			prevT=$curT
			Sz=`lfs quota -u $userID ~/|tail -n 1|awk '{print $1}'`
			if [ $Sz -lt $HDsize ]; then
				intT=1800
				let Dif=$HDsize-$Sz
				if [ $Dif -gt 10 ]; then
					intT=10800
				fi
			else
				intT=100
			fi
		fi
		
		if [ $nQ -le 10 -a $Sz -lt $HDsize ]; then
			qsub -N "chP$Genome" -o $Logfile -e $Logfile -pe def_slot 4 $project_root/sra2bam.py $GSM $Genome $project_root
			sleep 1
			break
		fi
	done
done

for GSM in `echo $sample_GSMs`; do
	Logfile="$project_root/$Genome/$bioproject/$GSM.log.txt"
	while :; do
		nQ=`qstat|tail -n +3| awk '{print $5}'|cut -c1|grep -cv -e "r"`
		curT=`date +%s`
	    let difT=$curT-$prevT

		if [ $difT -gt $intT ]; then
			prevT=$curT
			Sz=`lfs quota -u $userID ~/|tail -n 1|awk '{print $1}'`
			if [ $Sz -lt $HDsize ]; then
				intT=1800
				let Dif=$HDsize-$Sz
				if [ $Dif -gt 10 ]; then
					intT=10800
				fi
			else
				intT=100
			fi
		fi
		
		if [ $nQ -le 10 -a $Sz -lt $HDsize ]; then
			qsub -N "chP$Genome" -o $Logfile -e $Logfile -pe def_slot 4 $project_root/sra2bam.py $GSM $Genome $project_root
			sleep 1
			break
		fi
	done
done
exit
