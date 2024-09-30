import networkx as nx
import numpy as np
import os
import pickle
import LinkPrediction as lp
import time

class EvaluateLP:


	'''
	Constructor
	G_old -> Graph in which LP was applied
	G_new -> Graph evolved in time, where LP will be evaluated
	'''
	def __init__(self, G_old, G_new, df_LP_old, limit_to_top = 'new_edges') -> None:
		self.G_old = G_old
		self.G_new = G_new
		self.df_LP_old = df_LP_old
		self.process(limit_to_top)
		
	def process(self, limit_to_top = 'new_edges'):

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
		
		if limit_to_top == 'full':
			limit_to_top = len(self.df_LP_old)
		elif limit_to_top == 'new_edges':
			limit_to_top = len(edges_new)
		elif limit_to_top == '1%':
			limit_to_top = int(len(self.df_LP_old)*0.01)
			print('Top 1% Search')
		elif limit_to_top == '5%':
			limit_to_top = int(len(self.df_LP_old)*0.05)
			print('Top 5% Search')
		
		print('')
		print('######### Link Prediction Evaluation Module #########')
		print('')
		print('New edges exhibited by the model: '+str(len(edges_new)))
		print('Limit used as TOP rank search: '+str(limit_to_top))
		print('Full space of search: '+str(len(self.df_LP_old)))
		print('')
		# Foreach algorithm in df_LP_old check between edges_new
		algs = int(self.df_LP_old.shape[1]/3)
		for alg in range(int(self.df_LP_old.shape[1]/3)):
			# Some arithmethic to get the right columns
			col = 3*alg
			print('Evaluating Predictions for Algorithm '+str(alg+1)+' of '+
		          str(int(self.df_LP_old.shape[1]/3))+': '+self.df_LP_old.columns[col+2])

			counter = 0
			match = 0
			start = time.time()
			acc = 0

			max_score = self.df_LP_old.iloc[:,(col+2)].max()
			min_score = self.df_LP_old.iloc[:,(col+2)].min()

			if limit_to_top>=len(edges_new):
				for edge in edges_new:
					counter += 1
					if (counter % 10 == 0): print('Edge: {}/{} \r'.format(counter, len(edges_new)), end="")
				
					id_LP_edge = np.where(self.df_LP_old.iloc[0:limit_to_top,col].isin([edge[0],edge[1]]) & 
										  self.df_LP_old.iloc[0:limit_to_top,(col+1)].isin([edge[0],edge[1]]))[0]
					if len(id_LP_edge) > 0:
						int(id_LP_edge[0]) # should be only one
						match = match + 1
						# Get the LP score
						score_LP = self.df_LP_old.iloc[id_LP_edge[0],(col+2)]
						score_LP = (score_LP - min_score) / (max_score - min_score)
						acc += score_LP
			else:
				dfTopSearch = self.df_LP_old.iloc[0:limit_to_top,:]
				for row in range(dfTopSearch.shape[0]):
					counter += 1
					if (counter % 10 == 0): print('Edge: {}/{} \r'.format(counter, limit_to_top), end="")
					edge_go = (dfTopSearch.iloc[row,col], dfTopSearch.iloc[row,(col+1)])
					edge_come = (dfTopSearch.iloc[row,col+1], dfTopSearch.iloc[row,(col)])
					if (edge_go in edges_new) or (edge_come in edges_new):
						match = match + 1
						# Get the LP score
						score_LP = dfTopSearch.iloc[row,(col+2)]
						score_LP = (score_LP - min_score) / (max_score - min_score)
						acc += score_LP
			print()
			print('')
			print('Total matches: '+str(match))
			print('Accumulated score: '+str(acc))
			if limit_to_top>=len(edges_new):
				print('Average score: '+str(acc/len(edges_new)))
			else:
				print('Average score: '+str(acc/limit_to_top))
			print('')
			end = time.time()
			print('Link Evaluation Ended! Time: '+str(end-start))
			print('')
			# if limit_to_top < len(edges_new) # Choose search space


def main():
	
	version_old = "5.1.1"
	version_new = "5.1.2"
	print('Version OLD: '+str(version_old))
	print('Version NEW: '+str(version_new))
	
	G_old = pre_load_net(version_old)
	df_LP_old = pre_load_lp(version_old, G_old)

	G_new = pre_load_net(version_new)

	limit_list = [10, 100, 1000, '1%', '5%', 'new_edges', 'full']
	for l in limit_list:
		print('#############################################')
		print('Limit to TOP: '+str(l))
		print('#############################################')
		EvaluateLP(G_old, G_new, df_LP_old, l)

	print('Done!!!')

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