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

	# Single file processing
	drugbank_file = r"..\DataSources\DrugBank\5.1.10.xml" 
	# Generates DrugBank Edge List
	db1 = db.DrugBank(drugbank_file,"5.1.10")
	db1.preProcess()
	db1.export()

	# Load Pre-processed Edge Lists (Version According "Matching" Procedure)
	edgelistDrugBank = db1.edgelistfile
	#edgelistDrugBank = r"..\Exported\DrugBank\exp_5.1.10_interactions.csv" 

	# Network Analysis
	G = nx.read_edgelist(edgelistDrugBank, delimiter=',', nodetype=int) # Read the network

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