import argparse
from scipy.spatial.distance import pdist
from scipy.cluster.hierarchy import linkage, dendrogram

def read_wPGSA_result(wPGSA_result_file,threshold):
	TF={}
	tp={}
	TF_array_list=[]
	tp_array={}
	tp_array_list=[]
	with open(wPGSA_result_file,'r') as fi:
		line = fi.readline()
		itemList=line[:-1].split('\t')
		j=0
		for i in range(4,len(itemList)):
			tp[i-4]=itemList[i]
			tp_array[i-4]=[]
		line=fi.readline()
		while line:
			itemList=line[:-1].split('\t')
			TF_array=[]
			flag=0
			for i in range(4,len(itemList)):
				value=float(itemList[i])
				if value>=threshold:
					flag=1
			if flag==1:
				for i in range(4,len(itemList)):
					value=float(itemList[i])
					TF_array.append(value)
					tp_array[i-4].append(value)
				TF_array_list.append(TF_array)
				TF[j]=itemList[0]
				j+=1
			line=fi.readline()
	for i in range(len(tp_array)):
		tp_array_list.append(tp_array[i])

	return TF,tp,TF_array_list,tp_array_list

def exec_cluster(array_list,metric,method):
	lkg=linkage(pdist(array_list,metric=metric),method=method,metric=metric)
	print lkg

def start():
	argparser = argparse.ArgumentParser(description='Estimates relative activities of transcriptional regulators from given transcriptome data.')
	argparser.add_argument('--wPGSA-file', nargs=1, dest='wPGSA_result_file', metavar='wPGSA_result_file', help='wPGSA result file used as a clustering')
	argparser.add_argument('--threshold', nargs=1, dest='threshold', metavar='threshold', help='threshold for the visualization')

	args = argparser.parse_args()

	wPGSA_result_file = args.wPGSA_result_file[0]
	threshold=float(args.threshold[0])

	metric='correlation'
	method='average'

	TF,tp,TF_array_list,tp_array_list=read_wPGSA_result(wPGSA_result_file,threshold)
	exec_cluster(TF_array_list,metric,method)


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
