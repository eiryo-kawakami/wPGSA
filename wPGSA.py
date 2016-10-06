#!/usr/bin/env python
# coding: UTF-8

import argparse
import sys, math, numpy
import scipy as sp
from scipy import stats
import pandas as pd
from rpy2.robjects import r
import rpy2.robjects as robjects
import errno

__version__ = "1.1.0"

def get_progressbar_str(progress):
	MAX_LEN = 30
	BAR_LEN = int(MAX_LEN * progress)
	return ('[' + '=' * BAR_LEN +
			('>' if BAR_LEN < MAX_LEN else '') +
			' ' * (MAX_LEN - BAR_LEN) +
			'] %.1f%%' % (progress * 100.))

def read_logFC(logFC_file):
	exp_value = {}
	tp_list = []
	df = pd.read_csv(logFC_file,delimiter='\t',index_col=0)
	tp_list = df.columns
	#print tp_list
	gene_symbols = df.index
	#print gene_symbols
	for tp in tp_list:
		exp_value[tp] = {}
		for gene_symbol in gene_symbols:
			try:
				if not math.isnan(df.ix[gene_symbol,tp]):
					exp_value[tp][gene_symbol] = float(df.ix[gene_symbol,tp])
			except TypeError:
				pass
			except ValueError:
				pass

	return exp_value, tp_list

def read_network(network_file):
	positive = {}
	experiment = {}
	with open(network_file, 'r') as fi:
		line = fi.readline()
		line = fi.readline()
		while line:
			itemList = line.rstrip('\n\r').split('\t')
			TF = itemList[0]
			gene_symbol = itemList[2]
			if int(itemList[4]) >= 0:
				if TF not in positive:
					positive[TF] = {}
				positive[TF][gene_symbol] = float(itemList[3])
				if TF not in experiment:
					experiment[TF] = float(itemList[4])
			line = fi.readline()

	return positive, experiment

def wPGSA(tp_list,exp_value,positive,experiment):
	result = {}
	result["p_value"] = {}
	result["q_value"] = {}
	result["t_score"] = {}

	x = 1.0
	total_num = len(tp_list) * len(experiment)

	for tp in tp_list:
		positive_vector = {}
		experiment_vector = {}
		exp_vector = []
		for gene_symbol in exp_value[tp]:
			exp_vector.append(exp_value[tp][gene_symbol])
			for TF in experiment:
				if TF not in positive_vector:
					positive_vector[TF] = []
				if TF not in experiment_vector:
					experiment_vector[TF] = []
				experiment_vector[TF].append(experiment[TF])
				if gene_symbol in positive[TF]:
					positive_vector[TF].append(positive[TF][gene_symbol])
				else:
					positive_vector[TF].append(0.0)

		mean = numpy.mean(exp_vector)
		var = numpy.var(exp_vector)
		std = numpy.std(exp_vector)
		gene_size = len(exp_vector)

		TF_list = []

		for TF in experiment_vector:
			TF_list.append(TF)

		result["t_score"][tp] = []
		result["p_value"][tp] = []

		for TF in experiment_vector:
			value_list = []
			size = len(positive[TF])
			target_vector = numpy.array(exp_vector)*numpy.array(positive_vector[TF])/numpy.array(experiment_vector[TF])
			total_weight = sum(numpy.array(positive_vector[TF])/numpy.array(experiment_vector[TF]))
			target_mean = sum(target_vector)/total_weight
			target_var = 0
			for i in range(len(positive_vector[TF])):
				target_var += positive_vector[TF][i] * (exp_vector[i]-target_mean)**2 / experiment_vector[TF][i]
			target_var = target_var / total_weight
			target_std = numpy.sqrt(target_var)

			SE = numpy.sqrt(var/size+target_var/size)
			df = (size - 1) * (var + target_var)**2 / (var**2 + target_var**2)

			t_score = (target_mean - mean) / SE
			result["t_score"][tp].append(t_score)
			p_value = sp.stats.t.sf(abs(t_score),df)
			result["p_value"][tp].append(p_value)

			progress = x / total_num
			sys.stderr.write('\r\033[K' + get_progressbar_str(progress))
			sys.stderr.flush()

			x += 1


		R_p_list = robjects.FloatVector(result["p_value"][tp])
		r.assign('R_p_list', R_p_list)
		r.assign('list_len', len(R_p_list))
		result["q_value"][tp] = r('p.adjust(R_p_list, method="BH", n=list_len)')

	return result,TF_list

def write_result(result,TF_list,tp_list,experiment,output):
	for data in result:
		with open(output+'_TF_wPGSA_'+data+'.txt','w') as fo:
			fo.write("TF\tNumber_of_ChIPexp\t"+data+"_mean")
			for tp in tp_list:
				fo.write("\t"+tp)
			fo.write('\n')
			for i in range(len(TF_list)):
				# data values list contains all velues for one TF
				data_values = []
				for tp in tp_list:
					data_values.append(result[data][tp][i])
				# if all the values are not NaN
				if not numpy.isnan(data_values).any():
					fo.write(TF_list[i]+'\t'+str(int(experiment[TF_list[i]])))
					if data == "t_score":
						mean = 0
						for tp in tp_list:
							mean += result[data][tp][i]
						mean = mean / len(tp_list)
					else:
						mean = 1
						for tp in tp_list:
							mean *= result[data][tp][i]
						mean = mean ** (1.0/len(tp_list))
					fo.write('\t'+str(mean))
					for tp in tp_list:
						fo.write("\t"+str(result[data][tp][i]))
					fo.write('\n')

def start():
    argparser = argparse.ArgumentParser(description='Estimates relative activities of transcriptional regulators from given transcriptome data.')
    argparser.add_argument('--network-file', nargs=1, dest='network_file', metavar='network_file', help='network file used as a reference, shared in /network directory')
    argparser.add_argument('--logfc-file', nargs=1, dest='logfc_file', metavar='logFC_file', help='gene expression data file with the values in the Log2 fold-change, example in /sample_logFC_file')

    args = argparser.parse_args()
    logFC_file = args.logfc_file[0]
    network_file = args.network_file[0]

    exp_value, tp_list = read_logFC(logFC_file)
    positive, experiment = read_network(network_file)
    result,TF_list = wPGSA(tp_list,exp_value,positive,experiment)

    output = logFC_file.replace('.txt','')
    write_result(result,TF_list,tp_list,experiment,output)

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
