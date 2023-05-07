import networkx as nx
import pandas as pd
  
class LinkPrediction:

	def __init__(self, G) -> None:
		self.G = G


	# Resource Allocation Index
	"""
	T. Zhou, L. Lu, Y.-C. Zhang.
	Predicting missing links via local information.
	Eur. Phys. J. B 71 (2009) 623. https://arxiv.org/pdf/0901.0553.pdf
	"""
	def resource_allocation_index(self):
		nx.resource_allocation_index(self.G)


	# Jaccard Coefficient
	"""
	D. Liben-Nowell, J. Kleinberg.
	The Link Prediction Problem for Social Networks (2004).
	http://www.cs.cornell.edu/home/kleinber/link-pred.pdf
	"""
	def jaccard_coefficient(self):
		result = nx.jaccard_coefficient(self.G)
		result = list(result)
		result_correlation = result.copy()
		result.sort(key=lambda x: (x[-1], -x[0], -x[1]), reverse = True) # sort by last tuple element (in list)
		result_correlation.sort(key=lambda x: (x[0], x[1])) # For correlation
		print('done')
		# return


	# Adamic Adar Index
	"""	Obs: Same as before. """
	def adamic_adar_index(self):
		nx.adamic_adar_index(self.G)


	# Preferential Attachment
	""" Obs: Same as before. """
	def preferential_attachment(self):
		nx.preferential_attachment(self.G)


	# Common Neighbor Centrality
	"""
	Ahmad, I., Akhtar, M.U., Noor, S. et al. 
	Missing Link Prediction using Common Neighbor and Centrality based Parameterized Algorithm. 
	Sci Rep 10, 364 (2020). https://doi.org/10.1038/s41598-019-57304-y	
	Default: alpha=0.8
	"""
	def common_neighbor_centrality(self):
		nx.common_neighbor_centrality(self.G)

		
	# Within Inter Cluster
	"""
	Jorge Carlos Valverde-Rebaza and Alneu de Andrade Lopes.
	Link prediction in complex networks based on cluster information.
	In Proceedings of the 21st Brazilian conference on Advances in Artificial Intelligence (SBIA 12)
	https://doi.org/10.1007/978-3-642-34459-6_10
	Default: delta=0.001, community='community'
	"""
	def within_inter_cluster(self):
		nx.within_inter_cluster(self.G)


	# Community Common Neighbor (expect community information)
	"""
	Sucheta Soundarajan and John Hopcroft.
	Using community information to improve the precision of link prediction methods.
	In Proceedings of the 21st international conference companion on World Wide Web (WWW 12 Companion).
	ACM, New York, NY, USA, 607-608. http://doi.acm.org/10.1145/2187980.2188150
	"""
	def community_common_neighbor(self):
		nx.cn_soundarajan_hopcroft(self.G)


	# Community Resource Allocation
	""" Obs: Same as before. """
	def community_resource_allocation(self):
		nx.ra_index_soundarajan_hopcroft(self.G)