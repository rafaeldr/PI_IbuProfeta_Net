import networkx as nx
import time

def characterize_network_from_net(G, outFileName):

    # Network Components Analysis
    Gcc = sorted(nx.connected_components(G), key=len, reverse=True)
    sizes = [len(c) for c in Gcc]
    #Gmax=Gcc[0] # largest component
    Gmax = G.subgraph(Gcc[0]).copy()

    start = time.time()

    # Network Measures (Only with largest Component, when net is fragmented)
    n = G.order()
    m = G.size()
    z = G.number_of_edges() * 2 / G.number_of_nodes()
    print('Calculating Average Shortest Path Length')
    l = nx.average_shortest_path_length(Gmax) # Requires Not Fragmented Graph
    print('Calculating Diameter')
    d = nx.diameter(Gmax) # Requires Not Fragmented Graph
    print('Calculating Average Clustering')
    C = nx.average_clustering(G)
    print('Calculating Assortativity')
    r = nx.degree_assortativity_coefficient(G)
    density = nx.density(G)

    # Saving File
    with open(outFileName+".measures.txt", 'w') as f:
        f.write('n: '+str(n)+'\n')
        f.write('m: '+str(m)+'\n')
        f.write('z: '+str(z)+'\n')
        f.write('l: '+str(l)+'\n')
        f.write('d: '+str(d)+'\n')
        f.write('C: '+str(C)+'\n')
        f.write('r: '+str(r)+'\n')
        f.write('density: '+str(density)+'\n')
        f.write('sizes: '+str(sizes)+'\n')

    end = time.time()

    print('Measures Calculated! Time: '+str(end-start))

def characterize_network_from_file(edgelistfile):
    print('Generating Network '+edgelistfile)
    G = nx.read_edgelist(edgelistfile, delimiter=',', nodetype=int) # Read the network
    #ax = plt.figure(figsize=(10, 10))
    #nx.draw_networkx(G)
    #plt.pause(0.01)
    characterize_network_from_net(G, edgelistfile)