#!/usr/bin/python
# coding: UTF-8

import argparse
import os, sys, commands, re, time
import threading

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
fastq_dump       = os.path.join(tool_dir,'sratoolkit/bin/fastq-dump')
fastqc           = os.path.join(tool_dir,'FastQC/fastqc')
#Trimmomatic_dir = os.path.join(tool_dir,'Trimmomatic-0.33')
bowtie2dir       = os.path.join(tool_dir,'bowtie2')
#tophat2         = os.path.join(tool_dir,'tophat/tophat2')
bowtie2          = os.path.join(tool_dir,'bowtie2/bowtie2')
samtools         = os.path.join(tool_dir,'samtools-1.2/samtools')
#bam2rc          = '%s/exec_bam2readcount.R' % (tool_dir)
get_srafile      = os.path.join(tool_dir,'get_srafile.sh')
python_path      = os.path.join(os.environ['HOME'],'Python-2.7.2')

sra_accessions_tab = os.path.join(project_root,'table/SRA_Accessions.tab') # original: ftp.ncbi.nlm.nih.gov/sra/reports/Metadata/SRA_Accessions.tab

def make_resultDir(project_root,Genome,bioProject):
	cmd = 'mkdir -p %s/%s/%s 2>/dev/null' % (project_root,Genome,bioProject)
	os.system(cmd)

def check_disk_space():
	msg = 'checking disk space...'
	print msg
	cmd = "`whoami`"
	userID = commands.getoutput(cmd)
	cmd = 'lfs quota -u %s ./' % (userID)
	disk_info = commands.getoutput(cmd)
	using_space = int(re.findall(r'^\s*[0-9]+',disk_info)[0].replace(' ',''))
	
	return using_space

def read_input_info(input_info):
	column = {}
	sample_list = {}
	control_list = {}
	with open(input_info,'r') as fi:
		line = fi.readline()
		itemList = line[:-1].split('\t')
		for i in range(len(itemList)):
			column[itemList[i]] = i
		line = fi.readline()
		while line:
			itemList = line[:-1].split('\t')
			if itemList[column['bioproject']] != 'No_info':
				if itemList[column['sample_GSM']] != '' and itemList[column['control_GSM']] != '':
					bioProject = itemList[column['bioproject']]
					sample_GSM = itemList[column['sample_GSM']]
					control_GSM = itemList[column['control_GSM']]
					if bioProject not in control_list:
						control_list[bioProject] = []
					control_list[bioProject].append(control_GSM)
					if control_GSM not in sample_list:
						sample_list[control_GSM] = []
					sample_list[control_GSM].append(sample_GSM)
			line = fi.readline()

	return control_list,sample_list

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

def merge_bam_files(SRR_list,GSM_ID):
	msg = 'merge bam files...'
	print msg
	bam_list = ' '.join([SRR_id+'.bam' for SRR_id in SRR_list[GSM_ID]])
	cmd = '%s merge %s.bam %s' % (samtools,GSM_ID,bam_list)
	os.system(cmd)

def exec_macs2_peakcall(sample_GSM,control_GSM,Genome):
	msg = 'calling peak: %s.bam compaired with %s.bam' % (sample_GSM,control_GSM)
	print msg
	cmd = 'export PYTHONPATH=%s:$PYTHONPATH' % (python_path)
	os.system(cmd)
	cmd = '%s callpeak -t %s.bam -c %s.bam -f BAM -g %s -n %s' % (macs2,sample_GSM,control_GSM,Genome,sample_GSM)
	os.system(cmd)

def transfer_files(project_root,bioProject,Genome,local_strage):
	msg = 'transfering result files...'
	print msg
	cmd = '' #file transfer to local strage
	os.system(cmd)
	cmd = 'rm -rf %s/%s/%s' % (project_root,Genome,bioProject)
	os.system(cmd)

def start():
	argparser = argparse.ArgumentParser(description='Batch process ChIP-seq analysis based on a input table.')
	argparser.add_argument('--Genome', nargs=1, dest='Genome', metavar='Genome', help='reference genome used in mapping. eg) mm9, hg19')
	argparser.add_argument('--input_info', nargs=1, dest='input_info', metavar='input_info', help='input table for sample-input correspondence')
	#argparser.add_argument('--local_strage', nargs=1, dest='local_strage', metavar='local_strage', help='local strage address for transfering result files')

	args = argparser.parse_args()
	Genome = args.Genome[0]
	input_info = args.input_info[0]
	#local_strage = args.local_strage[0]

	cmd = 'mkdir -p %s/%s 2>/dev/null' % (project_root,Genome)
	os.system(cmd)

	bowtie2_indexes  = os.path.join(tool_dir,'bowtie2/indexes/'+Genome)

	control_list,sample_list = read_input_info(input_info)

	for bioProject in control_list:
		make_resultDir(project_root,Genome,bioProject)
		cmd = 'cd %s/%s/%s' % (project_root,Genome,bioProject)
		os.system(cmd)
		control_GSMs = ' '.join(control_list[bioProject])
		sample_array = []
		for control_GSM in control_list[bioProject]:
			sample_array.extend(sample_list[control_GSM])
		print sample_array
		sample_GSMs = ' '.join(sample_array)
		cmd = 'sh seq_exec_sra2bam.sh %s %s %s \"%s\" \"%s\"' % (project_root,Genome,bioProject,sample_GSMs,control_GSMs)
		print cmd
		os.system(cmd)
		for control_GSM in control_list[bioProject]:
			for sample_GSM in sample_list[control_GSM]:
				cmd = 'sh %s/exec_macs2_peakcall.sh %s %s %s %s %s' % (project_root,project_root,Genome,bioproject,sample_GSM,control_GSM)
				os.system(cmd)

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
