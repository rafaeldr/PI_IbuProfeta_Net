import DrugBank as db
import networkx as nx
import pandas as pd
import numpy as np
import os
import time
import NetMeasures as netM
import LinkPrediction as lp
import glob
import pickle
import matplotlib.pyplot as plt

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
		db1 = db.DrugBank(drugbank_file,version)
		db1.preProcess()
		db1.export()
		edgelistDrugBank = db1.edgelistfile

	# Network Analysis
	G = nx.read_edgelist(edgelistDrugBank, delimiter=',', nodetype=int) # Read the network

	# Plot Degree Distribution Analysis
	netM.plot_degree_analysis(G)

	# Network Measures
	netMeasuresDrugBank = os.path.join(r"..\Exported\DrugBank", "exp_{}_interactions.csv.measures.txt".format(version))
	if not os.path.isfile(netMeasuresDrugBank):
		netM.characterize_network_from_net(G, edgelistDrugBank)

	# FOR TESTING SIMULATIONS
	#G = nx.karate_club_graph() # TEST  (Requires manual adjustment for communities bin file)
		
	# Calculate Communities
	commFile = os.path.join(r"..\Exported\DrugBank", "exp_{}_communities.bin".format(version))
	if not os.path.isfile(commFile):
		print("Calculating Community Detection Info")
		start = time.time()
		comm = nx.community.greedy_modularity_communities(G)
		with open(commFile, 'wb') as file: # binary file
			pickle.dump(comm,file)
		end = time.time()
		print('Communities Calculated! Time: '+str(end-start))
	else:
		print("Importing Community Detection Info")
		with open(commFile, 'rb') as file:
			comm = pickle.load(file)
	
	
	# Link Prediction Phase
	print("Initializing Link Prediction")
	base_exp_path = r"..\Exported\DrugBank\exp_"+version
	lp1 = lp.LinkPrediction(G, base_exp_path)
	lp1.prepare_communities(comm)
	lp1.predict()
	
	lp1.export()
	lp1.correlation_analysis()
	lp1.export_with_names()

	input('Close all figures to proceed...')
	plt.show(block=True) # Deals with block = False (otherwise figures become unresponsive)
	input('Press any key to finish...')


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
	pathDrugBankEdgeList = r"..\Exported\DrugBank\*interactions.csv"
	for edgelistfile in glob.glob(pathDrugBankEdgeList):
		print('Calculating Network Measures for file: '+edgelistfile)
		netM.characterize_network_from_file(edgelistfile)


if __name__ == '__main__':

	main()