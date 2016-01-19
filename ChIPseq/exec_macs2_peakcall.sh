project_root=$1
Genome=$2
bioproject=$3
sample_GSM=$4
control_GSM=$5

cd $project_root/$Genome/$bioproject/

case "$Genome" in
	mm10 | mm9 | mm8) macsg=mm;;
	hg19 | hg18) macsg=hs;;
	ce10 | ce6) macsg=ce;;
	dm3 | dm2) macsg=dm;;
	sacCer2 | sacCer3) macsg=12100000;;
esac

Logfile="$project_root/$Genome/$bioproject/$sample_GSM.macs2.log.txt"

while :; do
	if [ -e $project_root/$Genome/$bioproject/$sample_GSM.bam ]; then
		if [ -e $project_root/$Genome/$bioproject/$control_GSM.bam ]; then
			nQ=`qstat|tail -n +3| awk '{print $5}'|cut -c1|grep -cv -e "r"`

			if [ $nQ -le 10 -a $Sz -lt $HDsize ]; then
			qsub -N "chP$Genome" -o $Logfile -e $Logfile -pe def_slot 4 macs2 callpeak -t `$project_root/$Genome/$bioproject/$sample_GSM.bam` -c `$project_root/$Genome/$bioproject/$control_GSM.bam` -g $macsg -n $sample_GSM
			sleep 1
			break
			fi
		fi
	fi
done
exit