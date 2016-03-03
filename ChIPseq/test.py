import glob

SRRfiles=glob.glob('SRR*.*')
print SRRfiles

if len(SRRfiles) == 0:
	print 'hoge'
