import os,re,

def get_SRR_ID(GSM_ID):
	msg = '%s : get SRR ID...' % (sampleID)
	print msg
	cmd = '%s -db sra -query %s | %s -format docsum | %s -pattern DocumentSummary -element Runs' % (esearch,sampleID,efetch,xtract)
	DocSum = commands.getoutput(cmd)
	print DocSum
	SRRs = re.findall('(SRR\\d+)', DocSum)
	return SRRs

def is_paired_end(SRR_ID):
	ncbi_info_url = "http://trace.ncbi.nlm.nih.gov/Traces/sra/sra.cgi?cmd=viewer&m=data&s=viewer&run="+SRR_ID
	sep = "<td>PAIRED"
	cmd = 'curl %s | grep -A10 Layout |grep %s |wc -l' % (ncbi_info_url,sep)
	is_pairend = commands.getoutput(cmd)
	return is_pairend

def get_sra_file(SRR_ID,is_pairend):
	## generate filepath and retrieve file from SRA disk node t347 ##
	cmd = '%s %s %s %s' % (get_srafile, SRR_ID, sra_accessions_tab, sshkey)
	os.system(cmd)

	if is_pairend=='yes':
		##SRA to FASTQ ##
		msg = '%s : SRA to FASTQ...' % (SRR_ID)
		print msg
    
		cmd = '%s --split-files --gzip  %s.sra' % (fastq_dump,SRR_ID)
		#print cmd
		os.system(cmd)

		cmd = 'rm %s.sra' % (SRR_ID)

	else:
		##SRA to FASTQ ##
		msg = '%s : SRA to FASTQ...' % (SRR_ID)
		print msg
		cmd = '%s --gzip %s.sra' % (fastq_dump,SRR_ID)
		#print cmd
		os.system(cmd)

		cmd = 'rm %s.sra' % (SRR_ID)

def exec_FASTQC(SRR_ID,is_pairend):
	msg = '%s : FASTQC...' % (sampleID)
	print msg
	if is_pairend =='yes':
		cmd = '%s %s_1.fastq.gz' % (fastqc,SRR_ID)
		os.system(cmd)
		cmd = '%s %s_2.fastq.gz' % (fastqc,SRR_ID)
		os.system(cmd)
	else:
		cmd = '%s %s.fastq.gz' % (fastqc,SRR_ID)
		#print cmd
		os.system(cmd)

def exec_bowtie2(SRR_ID,is_pairend):
	##Bowtie2 ##
	msg = '%s : bowtie2...' % (file_name)
	print msg
	options = '-p 4 -x %s' % (bowtie2_indexes)
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
	bam_list = ' '.join([SRR_id+'.bam' for SRR_id in SRRs)
	cmd = '%s merge %s.bam %s' % (samtools,GSM_ID,bam_list)
	os.system(cmd)

def start():
	argparser = argparse.ArgumentParser(description='Batch process ChIP-seq analysis based on a input table.')
	argparser.add_argument('--Genome', nargs=1, dest='Genome', metavar='Genome', help='reference genome used in mapping. eg) mm9, hg19')
	argparser.add_argument('--GSM_ID', nargs=1, dest='GSM_ID', metavar='GSM_ID', help='GSM_ID to analyze')
	argparser.add_argument('--project_root', nargs=1, dest='project_root', metavar='project_root', help='project root folder')

	args = argparser.parse_args()
	Genome = args.Genome[0]
	GSM_ID = args.GSM_ID[0]
	project_root = args.project_root[0]

	SRRs = get_SRR_ID(GSM_ID)

	for SRR_ID in SRRs:
		is_pairend = is_paired_end(SRR_ID)
		get_sra_file(SRR_ID,is_pairend)
		exec_FASTQC(SRR_ID,is_pairend)
		exec_bowtie2(SRR_ID,is_pairend)
		convert_sam2bam(SRR_ID)

	merge_bam_files(SRRs,GSM_ID)

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
