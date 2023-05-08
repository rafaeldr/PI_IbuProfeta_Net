import networkx as nx
import pandas as pd
import seaborn as sn
import matplotlib.pyplot as plt
  
class LinkPrediction:

	has_community_info = False
	dfResult = pd.DataFrame()
	dfCorrelation = pd.DataFrame()

	
	def __init__(self, G) -> None:
		self.G = G
		print(self.G)
		self.expected_preds = int(((self.G.number_of_nodes()*(self.G.number_of_nodes()-1))/2)-self.G.number_of_edges())
		print("Expected Edge Predictions (per Algorithm): "+str(self.expected_preds))

	def prepare_communities(self, comm):
		self.Gcomm = self.G.copy()
		add_community_info(self.Gcomm, comm)
		self.has_community_info = True
		
	def predict(self):
		self.resource_allocation_index()
		self.jaccard_coefficient()
		self.adamic_adar_index()
		self.preferential_attachment()
		self.common_neighbor_centrality()
		if self.has_community_info:
			self.within_inter_cluster()
			self.community_common_neighbor()
			self.community_resource_allocation()

	def correlation_analysis(self):
		corr_matrix = self.dfCorrelation.corr()
		sn.heatmap(corr_matrix, annot=True)
		plt.show()
		print('done')

	# Resource Allocation Index
	"""
	T. Zhou, L. Lu, Y.-C. Zhang.
	Predicting missing links via local information.
	Eur. Phys. J. B 71 (2009) 623. https://arxiv.org/pdf/0901.0553.pdf
	"""
	def resource_allocation_index(self):
		alg_name = 'Resource Allocation Index'
		print('Processing Link Prediction - Algorithm '+alg_name)
		result_raw = nx.resource_allocation_index(self.G)
		[result, result_correlation] = process_lp_result(result_raw)
		self.processing_dataframe(result, result_correlation, alg_name)

	# Jaccard Coefficient
	"""
	D. Liben-Nowell, J. Kleinberg.
	The Link Prediction Problem for Social Networks (2004).
	http://www.cs.cornell.edu/home/kleinber/link-pred.pdf
	"""
	def jaccard_coefficient(self):
		alg_name = 'Jaccard Coefficient'
		print('Processing Link Prediction - Algorithm '+alg_name)
		result_raw = nx.jaccard_coefficient(self.G)
		[result, result_correlation] = process_lp_result(result_raw)
		self.processing_dataframe(result, result_correlation, alg_name)


	# Adamic Adar Index
	"""	Obs: Same as before. """
	def adamic_adar_index(self):
		alg_name = 'Adamic Adar Index'
		print('Processing Link Prediction - Algorithm '+alg_name)
		result_raw = nx.adamic_adar_index(self.G)
		[result, result_correlation] = process_lp_result(result_raw)
		self.processing_dataframe(result, result_correlation, alg_name)


	# Preferential Attachment
	""" Obs: Same as before. """
	def preferential_attachment(self):
		alg_name = 'Preferential Attachment'
		print('Processing Link Prediction - Algorithm '+alg_name)
		result_raw = nx.preferential_attachment(self.G)
		[result, result_correlation] = process_lp_result(result_raw)
		self.processing_dataframe(result, result_correlation, alg_name)


	# Common Neighbor Centrality
	"""
	Ahmad, I., Akhtar, M.U., Noor, S. et al. 
	Missing Link Prediction using Common Neighbor and Centrality based Parameterized Algorithm. 
	Sci Rep 10, 364 (2020). https://doi.org/10.1038/s41598-019-57304-y	
	Default: alpha=0.8
	"""
	def common_neighbor_centrality(self):
		alg_name = 'Common Neighbor Centrality'
		print('Processing Link Prediction - Algorithm '+alg_name)
		result_raw = nx.common_neighbor_centrality(self.G)
		[result, result_correlation] = process_lp_result(result_raw)
		self.processing_dataframe(result, result_correlation, alg_name)

		
	# Within Inter Cluster | ** Expect Community Information **
	"""
	Jorge Carlos Valverde-Rebaza and Alneu de Andrade Lopes.
	Link prediction in complex networks based on cluster information.
	In Proceedings of the 21st Brazilian conference on Advances in Artificial Intelligence (SBIA 12)
	https://doi.org/10.1007/978-3-642-34459-6_10
	Default: delta=0.001, community='community'
	"""
	def within_inter_cluster(self):
		if self.has_community_info:
			alg_name = 'Within Inter Cluster'
			print('Processing Link Prediction - Algorithm '+alg_name)
			result_raw = nx.within_inter_cluster(self.Gcomm)
			[result, result_correlation] = process_lp_result(result_raw)
			self.processing_dataframe(result, result_correlation, alg_name)


	# Community Common Neighbor | ** Expect Community Information **
	"""
	Sucheta Soundarajan and John Hopcroft.
	Using community information to improve the precision of link prediction methods.
	In Proceedings of the 21st international conference companion on World Wide Web (WWW 12 Companion).
	ACM, New York, NY, USA, 607-608. http://doi.acm.org/10.1145/2187980.2188150
	"""
	def community_common_neighbor(self):
		if self.has_community_info:
			alg_name = 'Community Common Neighbor'
			print('Processing Link Prediction - Algorithm '+alg_name)
			result_raw = nx.cn_soundarajan_hopcroft(self.Gcomm)
			[result, result_correlation] = process_lp_result(result_raw)
			self.processing_dataframe(result, result_correlation, alg_name)


	# Community Resource Allocation | ** Expect Community Information **
	""" Obs: Same as before. """
	def community_resource_allocation(self):
		if self.has_community_info:
			alg_name = 'Community Resource Allocation'
			print('Processing Link Prediction - Algorithm '+alg_name)
			result_raw = nx.ra_index_soundarajan_hopcroft(self.Gcomm)
			[result, result_correlation] = process_lp_result(result_raw)
			self.processing_dataframe(result, result_correlation, alg_name)


	def processing_dataframe(self, result, result_correlation, col_name):
		dfTemp = pd.DataFrame(result, columns = ['a', 'b', col_name])
		dfTempCorrelation = pd.DataFrame(result_correlation, columns = [col_name])
		self.dfResult = pd.concat([self.dfResult, dfTemp], axis = 1)
		self.dfCorrelation = pd.concat([self.dfCorrelation, dfTempCorrelation], axis=1)


	def export(self, base_exp_path):
		# Export Link Prediction Results
		self.dfResult.to_csv(base_exp_path+"_linkprediction.csv", index = False)
		self.dfCorrelation.to_csv(base_exp_path+"_linkprediction_precorrelation.csv", index = False)


# Static functions

def process_lp_result(result_raw):
	''' List and sort data for result presentation and correlation analysis '''
	result = list(result_raw)
	result_correlation = result.copy()
	result.sort(key=lambda x: (x[-1], -x[0], -x[1]), reverse = True) # sort by last tuple element (in list)
	result_correlation.sort(key=lambda x: (x[0], x[1])) # For correlation
	result_correlation = [result_correlation[i][2] for i in range(len(result_correlation))]
	return [result, result_correlation]


def add_community_info(G, communities):
	for c, v_set in enumerate(communities):
		for v in v_set:
			G.nodes[v]['community'] = c