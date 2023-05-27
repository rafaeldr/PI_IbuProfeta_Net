import networkx as nx
import numpy as np
import pandas as pd
import seaborn as sn
import matplotlib.pyplot as plt
import time
import os
  
class LinkPrediction:

	has_community_info = False
	dfResult = pd.DataFrame()
	dfCorrelation = pd.DataFrame()
	skipAlgorithms = []
	dict_id_to_name = dict()
	has_changed = True
	__edges_rank_order = pd.DataFrame() # Obfuscation
	
	def __init__(self, G, base_exp_path = r"..\Exported\DrugBank\exp_") -> None:
		self.G = G
		self.base_exp_path = base_exp_path
		print(self.G)
		self.expected_preds = int(((self.G.number_of_nodes()*(self.G.number_of_nodes()-1))/2)-self.G.number_of_edges())
		print("Expected Edge Predictions (per Algorithm): "+str(self.expected_preds))

	def prepare_communities(self, comm):
		self.Gcomm = self.G.copy()
		add_community_info(self.Gcomm, comm)
		self.has_community_info = True
		
	def predict(self):
		self.check_previous_processed()
		
		start = time.time()
		if 'Resource Allocation Index' not in self.skipAlgorithms:
			self.has_changed = True
			self.resource_allocation_index()
			self.export()
		if 'Jaccard Coefficient' not in self.skipAlgorithms:
			self.has_changed = True
			self.jaccard_coefficient()
			self.export()
		if 'Adamic Adar Index' not in self.skipAlgorithms:
			self.has_changed = True
			self.adamic_adar_index()
			self.export()
		if 'Preferential Attachment' not in self.skipAlgorithms:
			self.has_changed = True
			self.preferential_attachment()
			self.export()
		if 'Common Neighbor Centrality' not in self.skipAlgorithms:
			self.has_changed = True
			self.common_neighbor_centrality()
			self.export()
		if self.has_community_info:
			if 'Within Inter Cluster' not in self.skipAlgorithms:
				self.has_changed = True
				self.within_inter_cluster()
				self.export()
			if 'Community Common Neighbor' not in self.skipAlgorithms:
				self.has_changed = True
				self.community_common_neighbor()
				self.export()
			if 'Community Resource Allocation' not in self.skipAlgorithms:
				self.has_changed = True
				self.community_resource_allocation()
				self.export()
		end = time.time()
		print('Link Prediction Ended! Time: '+str(end-start))

	def correlation_analysis(self):
		print('Calculating Correlation Analysis')
		start = time.time()
		cov_matrix = self.dfCorrelation.cov()
		corr_matrix_pearson = self.dfCorrelation.corr() # Pearson
		corr_matrix_spearman = self.dfCorrelation.corr(method='spearman')
		corr_matrix_kendall = self.dfCorrelation.corr(method='kendall')
		self.plot_matrix(cov_matrix, 'Covariance Matrix')
		self.plot_matrix(corr_matrix_pearson, 'Pearson Correlation Matrix')
		self.plot_matrix(corr_matrix_spearman, 'Spearman Correlation Matrix')
		self.plot_matrix(corr_matrix_kendall, 'Kendall Correlation Matrix')

		end = time.time()
		print('Correlation Analysis Calculated! Time: '+str(end-start))

	def plot_matrix(self, matrix, title = ''):
		plt.figure()
		plt.title(title)
		sn.heatmap(matrix, annot=True)
		plt.show(block=False)
		plt.pause(0.01)		

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
		[result, result_correlation] = self.process_lp_result(result_raw)
		self.combine_dataframe(result, result_correlation, alg_name)

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
		[result, result_correlation] = self.process_lp_result(result_raw)
		self.combine_dataframe(result, result_correlation, alg_name)


	# Adamic Adar Index
	"""	Obs: Same as before. """
	def adamic_adar_index(self):
		alg_name = 'Adamic Adar Index'
		print('Processing Link Prediction - Algorithm '+alg_name)
		result_raw = nx.adamic_adar_index(self.G)
		[result, result_correlation] = self.process_lp_result(result_raw)
		self.combine_dataframe(result, result_correlation, alg_name)


	# Preferential Attachment
	""" Obs: Same as before. """
	def preferential_attachment(self):
		alg_name = 'Preferential Attachment'
		print('Processing Link Prediction - Algorithm '+alg_name)
		result_raw = nx.preferential_attachment(self.G)
		[result, result_correlation] = self.process_lp_result(result_raw)
		self.combine_dataframe(result, result_correlation, alg_name)


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
		[result, result_correlation] = self.process_lp_result(result_raw)
		self.combine_dataframe(result, result_correlation, alg_name)

		
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
			[result, result_correlation] = self.process_lp_result(result_raw)
			self.combine_dataframe(result, result_correlation, alg_name)


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
			[result, result_correlation] = self.process_lp_result(result_raw)
			self.combine_dataframe(result, result_correlation, alg_name)


	# Community Resource Allocation | ** Expect Community Information **
	""" Obs: Same as before. """
	def community_resource_allocation(self):
		if self.has_community_info:
			alg_name = 'Community Resource Allocation'
			print('Processing Link Prediction - Algorithm '+alg_name)
			result_raw = nx.ra_index_soundarajan_hopcroft(self.Gcomm)
			[result, result_correlation] = self.process_lp_result(result_raw)
			self.combine_dataframe(result, result_correlation, alg_name)

	def process_lp_result(self, result_raw):
		''' List and sort data for result presentation and correlation analysis '''
		result = list(result_raw)
		result_correlation = result.copy()
		result.sort(key=lambda x: (x[-1], -x[0], -x[1]), reverse = True) # sort by last tuple element (in list)
		result_correlation.sort(key=lambda x: (x[0], x[1])) # For correlation
		if self.__edges_rank_order.empty:
			# Keep edges rank order for validation
			temp = [[result_correlation[i][0], result_correlation[i][1]] for i in range(len(result_correlation))]
			self.__edges_rank_order = pd.DataFrame(temp, columns = ['a', 'b'])
		else:
			# Check if edges rank order is the same
			temp = [[result_correlation[i][0], result_correlation[i][1]] for i in range(len(result_correlation))]
			dfTemp = pd.DataFrame(temp, columns = ['a', 'b'])
			if not self.__edges_rank_order.equals(dfTemp):
				print('Unexpected error: edges rank order is not the same')
				exit(1)
		result_correlation = [result_correlation[i][2] for i in range(len(result_correlation))]
		return [result, result_correlation]

	def combine_dataframe(self, result, result_correlation, col_name):
		dfTemp = pd.DataFrame(result, columns = ['a', 'b', col_name])
		dfTempCorrelation = pd.DataFrame(result_correlation, columns = [col_name])
		self.dfResult = pd.concat([self.dfResult, dfTemp], axis = 1)
		self.dfCorrelation = pd.concat([self.dfCorrelation, dfTempCorrelation], axis=1)

	def export(self):
		if self.has_changed:
			# Export Link Prediction Results
			self.dfResult.to_csv(self.base_exp_path+"_linkprediction.csv", index = False)
			self.dfCorrelation.to_csv(self.base_exp_path+"_linkprediction_precorrelation.csv", index = False)

	def plot_lp_analysis(self):
		fig_combined = plt.figure()
		plt.ylabel("Prediction Value Normalized")
		plt.xlabel("Rank")
		plt.title("Combined Rank Plot LP Values")
		for alg in range(int(self.dfResult.shape[1]/3)):
			# Some arithmethic to get the right columns
			col = 3*alg
			
			print('LP Analysis for Algorithm: '+self.dfResult.columns[col+2])
			print('Mean: '+str(self.dfResult.iloc[:,(col+2)].mean()))
			print('Median: '+str(self.dfResult.iloc[:,(col+2)].median()))
			print('Max: '+str(self.dfResult.iloc[:,(col+2)].max()))
			print('Min: '+str(self.dfResult.iloc[:,(col+2)].min()))
			print('Std: '+str(self.dfResult.iloc[:,(col+2)].std()))

			# Rank Plot Prediction Values
			result_plot = self.dfResult.iloc[:,(col+2)]
			plt.figure()
			plt.plot(result_plot)
			plt.title("Rank Plot LP Values - "+self.dfResult.columns[col+2])
			plt.xlim([0, len(result_plot)])
			plt.show(block=False)
			plt.pause(0.01)

			# Normalize and Plot Together
			rescale = lambda y: (y - np.min(y)) / (np.max(y) - np.min(y))
			result_plot = rescale(result_plot)
			plt.figure(fig_combined.number)
			plt.plot(result_plot)
			plt.xlim([0, len(result_plot)])
		plt.show(block=False)
		plt.pause(0.01)

	def check_previous_processed(self):
		lpFile = self.base_exp_path+"_linkprediction.csv"
		corrFile = self.base_exp_path+"_linkprediction_precorrelation.csv"
		if os.path.isfile(lpFile) and os.path.isfile(corrFile):
			self.dfResult = pd.read_csv(lpFile)
			self.dfCorrelation = pd.read_csv(corrFile)
			self.has_changed = False
			
			# Check if files are consistent
			if self.dfResult.shape[0] == self.expected_preds and self.dfCorrelation.shape[0] == self.expected_preds:
				self.skipAlgorithms = list(self.dfCorrelation.columns)
				# Check if both files have the same columns
				temp = list(self.dfResult.columns)
				temp = [temp[i] for i in range(len(self.dfResult.columns)) if (i+1)%3 == 0]
				if temp != self.skipAlgorithms:
					# files are not consistent
					self.dfResult = pd.DataFrame()
					self.dfCorrelation = pd.DataFrame()
					self.skipAlgorithms = []
					self.has_changed = True
			else: # if file exists but is not consistent
				self.dfResult = pd.DataFrame()
				self.dfCorrelation = pd.DataFrame()
				self.has_changed = True
		# return True if both files exist

	def export_with_names(self, limit = 1000):
		self.generate_id_to_name()
		limit = limit if limit < self.dfResult.shape[0] else self.dfResult.shape[0]
		dfExport = self.dfResult[0:limit].copy()
		dfExport = self.rewrite_names(dfExport)
		dfExport.to_excel(self.base_exp_path+"_results.xlsx", index = False)

	def generate_id_to_name(self):
		if self.dict_id_to_name == {}:
			drug_file = self.base_exp_path+"_drugs.csv"
			if os.path.isfile(drug_file):
				dfDrugs = pd.read_csv(drug_file)
				for index, row in dfDrugs.iterrows():
					self.dict_id_to_name[row['drugbank-id']] = row['name']

	def rewrite_names(self, df):
		for i in range(len(df)): # row
			for j in range(len(df.iloc[i])): # column
				if (j+1)%3 != 0:
					df.iloc[i,j] = self.dict_id_to_name[df.iloc[i,j]]
		return df


# Static functions

def add_community_info(G, communities):
	for c, v_set in enumerate(communities):
		for v in v_set:
			G.nodes[v]['community'] = c