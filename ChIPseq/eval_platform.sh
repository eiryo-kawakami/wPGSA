#! /bin/sh

SRR_ID=$1

main(){
	platform=`curl -s "http://trace.ncbi.nlm.nih.gov/Traces/sra/sra.cgi?cmd=viewer&m=data&s=viewer&run="$SRR_ID| grep -A10 Layout |grep "<td>ABI Solid"|wc -l` # platform=0: Illumina, 1: ABI SOLiD

	echo $platform
}

main $*