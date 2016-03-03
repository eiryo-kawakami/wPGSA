#! /bin/sh

SRR_ID=$1

main(){
	is_pairend=`curl -s "http://trace.ncbi.nlm.nih.gov/Traces/sra/sra.cgi?cmd=viewer&m=data&s=viewer&run="$SRR_ID| grep -A10 Layout |grep "<td>PAIRED"|wc -l` # is_pairend=0: SINGLE, 1: PAIRED

	echo $is_pairend
}

main $*