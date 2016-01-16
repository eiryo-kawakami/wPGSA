import os, sys, commands, re

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
bowtie2_indexes  = os.path.join(tool_dir,'bowtie2/indexes/'+refdb)
fastq_dump       = os.path.join(tool_dir,'sratoolkit/bin/fastq-dump')
fastqc           = os.path.join(tool_dir,'FastQC/fastqc')
#Trimmomatic_dir = os.path.join(tool_dir,'Trimmomatic-0.33')
bowtie2dir       = os.path.join(tool_dir,'bowtie2')
#tophat2         = os.path.join(tool_dir,'tophat/tophat2')
bowtie2          = os.path.join(tool_dir,'bowtie2/bowtie2')
samtools         = os.path.join(tool_dir,'samtools-1.2/samtools')
#bam2rc          = '%s/exec_bam2readcount.R' % (tool_dir)
get_srafile      = os.path.join(tool_dir,'get_srafile.sh')

sra_accessions_tab = os.path.join(project_root,'table/SRA_Accessions.tab') # original: ftp.ncbi.nlm.nih.gov/sra/reports/Metadata/SRA_Accessions.tab

def disk_space_check():
	msg = 'checking disk space...'
	print msg
	cmd = 'lfs quota -u eiryo-kawakami ./'
	disk_info = commands.getoutput(cmd)
	using_space = int(re.findall(r'^\s*[0-9]+',disk_info)[0].replace(' ',''))
	if using_space > 500000000:
		cmd = 'wait'
		os.system(cmd)

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
	else:
		##SRA to FASTQ ##
		msg = '%s : SRA to FASTQ...' % (SRR_ID)
		print msg
		cmd = '%s --gzip %s.sra' % (fastq_dump,SRR_ID)
		#print cmd
		os.system(cmd)

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


def merge_bam_files(SRR_list,GSM_ID):
	msg = 'merge bam files...'
	print msg
	bam_list = ' '.join([SRR_id+'.bam' for SRR_id in SRR_list[GSM_ID]])
	cmd = '%s merge %s.bam %s' % (samtools,GSM_ID,bam_list)
	os.system(cmd)

def exec_macs2_peakcall(sample_BAM,control_BAM):
	msg = 'calling peak: %s.bam compaired with %s.bam' % (sample_BAM,control_BAM)
	print msg

