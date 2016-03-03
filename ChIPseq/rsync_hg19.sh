#!/bin/sh
rsa='/Users/eiryokawakami/.ssh/id_rsa' ##遺伝研スパコン公開鍵へのpath
ddbj_usrID='eiryo-kawakami' ##遺伝研ユーザー名

if [ -z `pgrep rsync` ]; then
	rsync -auvr --include='*/' --include='*.txt' --include='*.zip' --include='*.html' --include='*.r' --include='*.bed' --include='*.xls' --include='*.narrowPeak' --include='GSM*.bam' --exclude='*' -e "ssh -i $rsa" ddbj:/home/$ddbj_usrID/repos/PGSEA/hg19/ /Volumes/Public/ChIPdata/hg19/
fi
