import networkx as nx
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
		
		pass



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