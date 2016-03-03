#!/bin/bash
# requirements:
#  RSA public key (created without password) must be registered to authorized_keys in t347 node (SRA disk attached node).
#  Once you created ssh key, try:
#    cat $HOME/.ssh/id_rsa_pub | ssh t347 sh -c 'cat >> $HOME/.ssh/authorized_keys'
#
# usage:
#   chmod u+x filepath_gen.sh
#   filepath_gen.sh <SRA Run ID> <SRA Accession table> <ssh auth key>
# example:
#   filepath_gen.sh DRR000001 SRA_Accessions.tab $HOME/.ssh/id_rsa
#
# To get accessions table, try:
#   lftp -c "open ftp.ncbi.nlm.nih.gov/sra/reports/Metadata && pget -n 8 SRA_Accessions.tab"

# for script debug
set -uxe

get_filepath(){
  id=${1}
  sra_acc_tab=${2}
  cat ${sra_acc_tab} | awk -F '\t' --assign id="${id}" 'match($1, "^" id "$") {
    OFS="/"
    prefix="t347:/usr/local/ftp/public/ddbj_database/dra/sralite/ByExp/litesra"
    print prefix, substr($11,1,3), substr($11,1,6), $11, $1, $1 ".sra"
  }'
}

# arguments for this script
id=${1}
sra_acc_tab=${2}

# get .sra filepath
filepath=`get_filepath ${id} ${sra_acc_tab}`

# copy .sra file to current working dir
sshkey=${3}
rsync -avr -vv -e "ssh -i ${sshkey}" ${filepath} ${id}.sra
