import os,re,argparse,commands,glob

## ssh key location, must be absolute path ##
sshkey = '/home/eiryo-kawakami/.ssh/id_rsa' # FIXME

## tools ##
project_root     = os.path.join(os.environ['HOME'],'repos/PGSEA/')
print project_root
tool_dir         = os.path.join(project_root,'tools')

edirect          = os.path.join(tool_dir,'edirect')
esearch          = os.path.join(edirect,'esearch')
efetch           = os.path.join(edirect,'efetch')
xtract           = os.path.join(edirect,'xtract')
#bowtie2_indexes  = os.path.join(tool_dir,'bowtie2/indexes/'+refdb)
fastq_dump       = os.path.join(tool_dir,'sratoolkit.2.5.7-centos_linux64/bin/fastq-dump.2.5.7')
fastqc           = os.path.join(tool_dir,'FastQC/fastqc')
#Trimmomatic_dir = os.path.join(tool_dir,'Trimmomatic-0.33')
bowtiedir = os.path.join(tool_dir,'bowtie-1.1.2')
bowtie = os.path.join(tool_dir,'bowtie-1.1.2/bowtie')
bowtie2dir       = os.path.join(tool_dir,'bowtie2')
bowtie2          = os.path.join(tool_dir,'bowtie2/bowtie2')
samtools         = os.path.join(tool_dir,'samtools-1.2/samtools')
get_srafile      = os.path.join(tool_dir,'get-dra_SRR.sh')

#sra_accessions_tab = os.path.join(project_root,'table/SRA_Accessions.tab') # original: ftp.ncbi.nlm.nih.gov/sra/reports/Metadata/SRA_Accessions.tab
gsm_srr_tab = os.path.join(project_root,'tools/GSM_SRR.tab')

def get_SRR_ID(GSM_ID):
	msg = '%s : get SRR ID...' % (GSM_ID)
	print msg
	cmd = '%s -db sra -query %s | %s -format docsum | %s -pattern DocumentSummary -element Runs' % (esearch,GSM_ID,efetch,xtract)
	DocSum = commands.getoutput(cmd)
	print DocSum
	SRRs = re.findall('(SRR\\d+)', DocSum)
	print SRRs
	return SRRs

def get_SRX_ID(GSM_ID):
	msg = '%s : get SRX ID...' % (GSM_ID)
	print msg
	cmd = '%s -db gds -query %s | %s -format docsum | %s -pattern ExtRelation -element RelationType,TargetObject' % (esearch,GSM_ID,efetch,xtract)
	DocSum = commands.getoutput(cmd)
	print DocSum
	SRRs = re.findall('(SRX\\d+)', DocSum)
	print SRRs
	return SRRs

def get_SRR_ID_from_table(GSM_ID):
	msg = '%s : get SRR ID...' % (GSM_ID)
	print msg
	SRRs = []
	with open(gsm_srr_tab,'r') as fi:
		line = fi.readline()
		line = fi.readline()
		while line:
			itemList = line[:-1].split('\t')
			if itemList[0] == GSM_ID:
				SRRs = itemList[1].split(',')
			line = fi.readline()
	return SRRs

''' ##obsolete##
def is_paired_end(SRR_ID):
	ncbi_info_url = "\"http://trace.ncbi.nlm.nih.gov/Traces/sra/sra.cgi?cmd=viewer&m=data&s=viewer&run=\""+SRR_ID
	sep = "\"<td>PAIRED\""
	cmd = '`curl %s | grep -A10 Layout |grep %s |wc -l`' % (ncbi_info_url,sep)
	is_pairend = os.system(cmd)
	return is_pairend

def eval_platform(SRR_ID):
	ncbi_info_url = "\"http://trace.ncbi.nlm.nih.gov/Traces/sra/sra.cgi?cmd=viewer&m=data&s=viewer&run=\""+SRR_ID
	sep = "\"<td>ABI Solid\""
	cmd = '`curl %s | grep -A10 Platform |grep %s |wc -l`' % (ncbi_info_url,sep)
	platform = os.system(cmd)
	return platform
''' ##obsolete##

def get_sra_file(SRX_ID,sample_dir):
	## generate filepath and retrieve file from SRA disk node t347 ##
	cmd = 'sh %s %s %s' % (get_srafile, SRX_ID, sample_dir)
	os.system(cmd)

def exec_fastq_dump(SRR_ID,is_pairend,platform):
	file_name=glob.glob(SRR_ID+'*')

	if 'fastq.bz2' in file_name[0]:
		is_sra='no'
	else:
		is_sra='yes'
		if platform=='1':
			if is_pairend=='1':
				##SRA to FASTQ ##
				msg = '%s : SRA to FASTQ...' % (SRR_ID)
				print msg
				cmd = '%s --split-files --dumpcs %s.sra' % (fastq_dump,SRR_ID)
				os.system(cmd)
				cmd = 'rm %s.sra' % (SRR_ID)
				os.system(cmd)

			else:
				##SRA to FASTQ ##
				msg = '%s : SRA to FASTQ...' % (SRR_ID)
				print msg
				cmd = '%s --dumpcs %s.sra' % (fastq_dump,SRR_ID)
				os.system(cmd)
				cmd = 'rm %s.sra' % (SRR_ID)
				os.system(cmd)

		else:
			if is_pairend=='1':
				##SRA to FASTQ ##
				msg = '%s : SRA to FASTQ...' % (SRR_ID)
				print msg
				cmd = '%s --split-files --gzip  %s.sra' % (fastq_dump,SRR_ID)
				os.system(cmd)
				cmd = 'rm %s.sra' % (SRR_ID)
				os.system(cmd)

			else:
				##SRA to FASTQ ##
				msg = '%s : SRA to FASTQ...' % (SRR_ID)
				print msg
				cmd = '%s --gzip %s.sra' % (fastq_dump,SRR_ID)
				os.system(cmd)
				cmd = 'rm %s.sra' % (SRR_ID)
				os.system(cmd)
	return is_sra

def exec_FASTQC(SRR_ID,is_pairend,platform,is_sra):
	msg = '%s : FASTQC...' % (SRR_ID)
	print msg
	if is_sra=='yes':
		if platform=='1':
			if is_pairend =='1':
				cmd = '%s %s_1.fastq' % (fastqc,SRR_ID)
				os.system(cmd)
				cmd = '%s %s_2.fastq' % (fastqc,SRR_ID)
				os.system(cmd)
			else:
				cmd = '%s %s.fastq' % (fastqc,SRR_ID)
				os.system(cmd)
		else:
			if is_pairend =='1':
				cmd = '%s %s_1.fastq.gz' % (fastqc,SRR_ID)
				os.system(cmd)
				cmd = '%s %s_2.fastq.gz' % (fastqc,SRR_ID)
				os.system(cmd)
			else:
				cmd = '%s %s.fastq.gz' % (fastqc,SRR_ID)
				os.system(cmd)
	else:
		if is_pairend =='1':
			cmd='bzip2 -d %s_1.fastq.bz2' % (SRR_ID)
			os.system(cmd)
			cmd='bzip2 -d %s_2.fastq.bz2' % (SRR_ID)
			os.system(cmd)
			cmd = '%s %s_1.fastq' % (fastqc,SRR_ID)
			os.system(cmd)
			cmd = '%s %s_2.fastq' % (fastqc,SRR_ID)
			os.system(cmd)
		else:
			cmd='bzip2 -d %s.fastq.bz2' % (SRR_ID)
			os.system(cmd)
			cmd = '%s %s.fastq' % (fastqc,SRR_ID)
			os.system(cmd)

def exec_bowtie(SRR_ID,is_pairend,bowtie_indexes):
	##Bowtie for ABI Solid##
	msg = '%s : bowtie...' % (SRR_ID)
	print msg
	options = '-S -C -p 4 %s' % (bowtie_indexes)
	if is_pairend =='1':
		cmd = 'export PATH=$PATH:%s && %s %s -1 %s_1.fastq -2 %s_2.fastq %s.sam 2> bowtieReport.txt' % (bowtiedir,bowtie,options,SRR_ID,SRR_ID,SRR_ID)
	else:
		cmd = 'export PATH=$PATH:%s && %s %s %s.fastq %s.sam 2> bowtieReport.txt' % (bowtiedir,bowtie,options,SRR_ID,SRR_ID)
	os.system(cmd)

	if is_pairend =='1':
		cmd = 'rm %s_1.fastq' % (SRR_ID)
		os.system(cmd)
		cmd = 'rm %s_2.fastq' % (SRR_ID)
		os.system(cmd)
	else:
		cmd = 'rm %s.fastq' % (SRR_ID)
		os.system(cmd)

def exec_bowtie2(SRR_ID,is_pairend,bowtie2_indexes,is_sra):
	##Bowtie2 ##
	msg = '%s : bowtie2...' % (SRR_ID)
	print msg
	options = '-p 4 -N 1 -x %s' % (bowtie2_indexes)
	if is_sra=='yes':
		if is_pairend =='1':
			cmd = 'export PATH=$PATH:%s && %s %s -1 %s_1.fastq.gz -2 %s_2.fastq.gz -S %s.sam 2> bowtieReport.txt' % (bowtie2dir,bowtie2,options,SRR_ID,SRR_ID,SRR_ID)
		else:
			cmd = '%s %s -U %s.fastq.gz -S %s.sam 2> bowtieReport.txt' % (bowtie2,options,SRR_ID,SRR_ID)
			print cmd
		os.system(cmd)

		if is_pairend =='1':
			cmd = 'rm %s_1.fastq.gz' % (SRR_ID)
			os.system(cmd)
			cmd = 'rm %s_2.fastq.gz' % (SRR_ID)
			os.system(cmd)
		else:
			cmd = 'rm %s.fastq.gz' % (SRR_ID)
			os.system(cmd)
	else:
		if is_pairend =='1':
			cmd = 'export PATH=$PATH:%s && %s %s -1 %s_1.fastq -2 %s_2.fastq -S %s.sam 2> bowtieReport.txt' % (bowtie2dir,bowtie2,options,SRR_ID,SRR_ID,SRR_ID)
		else:
			cmd = '%s %s -U %s.fastq -S %s.sam 2> bowtieReport.txt' % (bowtie2,options,SRR_ID,SRR_ID)
			print cmd
		os.system(cmd)

		if is_pairend =='1':
			cmd = 'rm %s_1.fastq' % (SRR_ID)
			os.system(cmd)
			cmd = 'rm %s_2.fastq' % (SRR_ID)
			os.system(cmd)
		else:
			cmd = 'rm %s.fastq' % (SRR_ID)
			os.system(cmd)

def convert_sam2bam(SRR_ID):
	##Convert Sam to Bam ##
	msg = '%s : samtools...' % (SRR_ID)
	print msg
	cmd = '%s view -bS %s.sam > %s.bam' % (samtools,SRR_ID,SRR_ID)
	os.system(cmd)
	cmd = 'rm %s.sam' % (SRR_ID)
	os.system(cmd)

def merge_bam_files(SRRs,GSM_ID):
	msg = 'merge bam files...'
	print msg
	if len(SRRs) > 1:
		bam_list = ' '.join([SRR_id+'.bam' for SRR_id in SRRs])
		cmd = '%s merge %s.bam %s' % (samtools,GSM_ID,bam_list)
		os.system(cmd)
		for i in range(len(SRRs)):
			cmd = 'rm %s.bam' % (SRRs[i])
			os.system(cmd)
	else:
		cmd = 'mv %s.bam %s.bam' % (SRRs[0],GSM_ID)
		os.system(cmd)

def start():
	argparser = argparse.ArgumentParser(description='Batch process ChIP-seq analysis based on a input table.')
	argparser.add_argument('--Genome', nargs=1, dest='Genome', metavar='Genome', help='reference genome used in mapping. eg) mm9, hg19')
	argparser.add_argument('--GSM_ID', nargs=1, dest='GSM_ID', metavar='GSM_ID', help='GSM_ID to analyze')
	argparser.add_argument('--project_root', nargs=1, dest='project_root', metavar='project_root', help='project root folder')
	argparser.add_argument('--bioproject', nargs=1, dest='bioproject', metavar='bioproject', help='bioproject ID')

	args = argparser.parse_args()
	Genome = args.Genome[0]
	GSM_ID = args.GSM_ID[0]
	project_root = args.project_root[0]
	bioproject = args.bioproject[0]

	sample_dir = os.path.join(project_root,Genome,bioproject)

	os.chdir(sample_dir)

	SRRs = get_SRR_ID(GSM_ID)
	if len(SRRs) == 0:
		SRRs = get_SRR_ID_from_table(GSM_ID)
	SRXs = get_SRX_ID(GSM_ID)

	bowtie_indexes = os.path.join(tool_dir,'bowtie-1.1.2/indexes/'+Genome+'_color')
	bowtie2_indexes  = os.path.join(tool_dir,'bowtie2/indexes/'+Genome)
	mergeSRRs=[]
	if len(SRXs) > 0:
		for SRX_ID in SRXs:
			get_sra_file(SRX_ID,sample_dir)
			if len(SRRs) > 0:
				for SRR_ID in SRRs:
					SRRfile=glob.glob(SRR_ID+'*')
					print SRRfile
					if len(SRRfile) > 0:
						cmd = 'sh %s/is_paired_end.sh %s' % (project_root,SRR_ID)
						is_pairend = commands.getoutput(cmd)
						cmd = 'sh %s/eval_platform.sh %s' % (project_root,SRR_ID)
						platform = commands.getoutput(cmd)
						print 'platform %s' % (platform)
						is_sra=exec_fastq_dump(SRR_ID,is_pairend,platform)
						exec_FASTQC(SRR_ID,is_pairend,platform,is_sra)
						if platform == "1":
							exec_bowtie(SRR_ID,is_pairend,bowtie_indexes)
						else:
							exec_bowtie2(SRR_ID,is_pairend,bowtie2_indexes,is_sra)
						convert_sam2bam(SRR_ID)
						mergeSRRs.append(SRR_ID)

		if len(mergeSRRs) > 0:
			merge_bam_files(mergeSRRs,GSM_ID)
			msg = '%s finished' % (GSM_ID)
		else:
			msg = '%s no sra file' % (GSM_ID)
		print msg
	else:

		msg = '%s no sra file' % (GSM_ID)

		print msg

if __name__ == "__main__":
	try:
		start()
	except KeyboardInterrupt:
		pass
	except IOError as e:
		if e.errno == errno.EPIPE:
			pass
		else:
			raise
