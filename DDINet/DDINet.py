import DrugBank as db
import networkx as nx
import pandas as pd
import os
#import matplotlib.pyplot as plt
import NetMeasures as netM
import glob

def main():
	isExist = os.path.exists(r"..\Exported")
	if not isExist: os.makedirs(r"..\Exported")
	isExist = os.path.exists(r"..\Exported\DrugBank")
	if not isExist: os.makedirs(r"..\Exported\DrugBank")

	# Single file processing mode
	version = "5.1.10"
	drugbank_file = os.path.join(r"..\DataSources\DrugBank", "{}.xml".format(version))
	
	# Generates DrugBank Edge List
	edgelistDrugBank = os.path.join(r"..\Exported\DrugBank", "exp_{}_interactions.csv".format(version))
	if not os.path.isfile(edgelistDrugBank):
		db1 = db.DrugBank(drugbank_file,"5.1.10")
		db1.preProcess()
		db1.export()
		edgelistDrugBank = db1.edgelistfile

	# Network Analysis
	G = nx.read_edgelist(edgelistDrugBank, delimiter=',', nodetype=int) # Read the network

	# Network Measures
	netMeasuresDrugBank = os.path.join(r"..\Exported\DrugBank", "exp_{}_interactions.csv.measures.txt".format(version))
	if not os.path.isfile(netMeasuresDrugBank):
		netM.characterize_network_from_net(G, edgelistDrugBank)


	print('done!')


# Batch Generates Edge List (DrugBank Files)
def batchDrugBank():
	pathDrugBank = r"..\DataSources\DrugBank\*.xml" # Names are expected to contain only the version number
	for file in glob.glob(pathDrugBank):
		print('Generating Edge List for file: '+file)
		db1 = db.DrugBank(file,os.path.splitext(os.path.basename(file))[0])
		db1.preProcess()
		db1.export()
		del db1

# Batch Network Analysis (DrugBank Files)
def batchDBNetMeasure():
	pathDrugBankEdgeList = r"..\Exported\DrugBank\*.csv"
	for edgelistfile in glob.glob(pathDrugBankEdgeList):
		print('Calculating Network Measures for file: '+edgelistfile)
		netM.characterize_network_from_file(edgelistfile)

if __name__ == '__main__':
	main()