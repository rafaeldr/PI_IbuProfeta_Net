import networkx as nx
import numpy as np
import os
import pickle
import LinkPrediction as lp

class EvaluateLP:


	'''
	Constructor
	G_old -> Graph in which LP was applied
	G_new -> Graph evolved in time, where LP will be evaluated
	'''
	def __init__(self, G_old, G_new, df_LP_old) -> None:
		self.G_old = G_old
		self.G_new = G_new
		self.df_LP_old = df_LP_old
		self.process()
		
	def process(self):

		# Remove nodes from G_new that ARE NOT in G_old
		nodes_new = set(self.G_new.nodes)
		nodes_old = set(self.G_old.nodes)
		nodes_to_remove = nodes_new - nodes_old
		self.G_new.remove_nodes_from(nodes_to_remove)

		# Remove edges from G_new that ARE in G_old
		edges_new = set(self.G_new.edges)
		edges_old = set(self.G_old.edges)
		edges_to_remove = edges_new.intersection(edges_old)
		self.G_new.remove_edges_from(edges_to_remove)
		# Left only edges that are new in G_new

		edges_new = set(self.G_new.edges)

		print('stop')
		# Foreach algorithm in df_LP_old check between edges_new
		algs = int(self.df_LP_old.shape[1]/3)
		for alg in range(int(self.df_LP_old.shape[1]/3)):
			# Some arithmethic to get the right columns
			col = 3*alg

			for edge in edges_new:
				id_LP_edge = np.where(self.df_LP_old.iloc[:,col].isin([edge[0],edge[1]]) & self.df_LP_old.iloc[:,(col+1)].isin([edge[0],edge[1]]))[0]
				if len(id_LP_edge) > 0:
					int(id_LP_edge[0]) # should be only one



def main():
	
	version_old = "5.0.2"
	version_new = "5.1.10"
	
	G_old = pre_load_net(version_old)
	df_LP_old = pre_load_lp(version_old, G_old)

	G_new = pre_load_net(version_new)

	eval_LP = EvaluateLP(G_old, G_new, df_LP_old)

	print('test')

def pre_load_net(version):
	edgelistDrugBank = os.path.join(r"..\Exported\DrugBank", "exp_{}_interactions.csv".format(version))
	G = nx.read_edgelist(edgelistDrugBank, delimiter=',', nodetype=int) # Read the network
	return G

def pre_load_lp(version, G):
	commFile = os.path.join(r"..\Exported\DrugBank", "exp_{}_communities.bin".format(version))
	with open(commFile, 'rb') as file:
		comm = pickle.load(file)
	base_exp_path = r"..\Exported\DrugBank\exp_"+version
	lp1 = lp.LinkPrediction(G, base_exp_path)
	lp1.prepare_communities(comm)
	lp1.predict()
	return lp1.dfResult

if __name__ == '__main__':

	main()