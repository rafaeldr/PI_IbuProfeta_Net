import networkx as nx
import numpy as np
import matplotlib.pyplot as plt
import time
import powerlaw

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
    characterize_network_from_net(G, edgelistfile)

def plot_degree_analysis(G):
    degree_sequence = sorted((d for n, d in G.degree()), reverse=True)
    degrees = [G.degree(n) for n in G.nodes()]
    dmax = max(degree_sequence)
    
    # Degree Histogram Individually
    plt.figure()
    unique_degrees = np.unique(degree_sequence, return_counts=True)
    rescale = lambda y: (y - np.min(y)) / (np.max(y) - np.min(y))
    my_cmap = plt.get_cmap("coolwarm")
    plt.bar(*unique_degrees, width=3, color = my_cmap(rescale(unique_degrees[1])))
    plt.title("Degree Histogram")
    plt.xlabel("Degree")
    plt.ylabel("# of Nodes")
    plt.xlim([0, dmax])
    plt.show(block=False)
    plt.pause(0.01)

    # Degree Histogram Individually
    plt.figure()
    plt.bar(*unique_degrees, width=3, color = my_cmap(rescale(unique_degrees[1])))
    plt.title("Degree Histogram Log-Lin")
    plt.xlabel("Degree")
    plt.ylabel("# of Nodes")
    plt.xscale('log')
    plt.show(block=False)
    plt.pause(0.01)
    
    # Degree Histogram Individually (with bins)
    plt.figure()
    counts, bins = np.histogram(degrees, 50)
    plt.stairs(counts, bins)
    #plt.hist(degrees, 50)
    plt.title("Degree Histogram (50-bins)")
    plt.xlabel("Degree")
    plt.ylabel("# of Nodes")
    plt.xlim([0, dmax])
    plt.show(block=False)
    plt.pause(0.01)

    # Degree Rank Plot
    plt.figure()
    plt.plot(degree_sequence, "b-", marker="o")
    plt.title("Degree Rank Plot")
    plt.ylabel("Degree")
    plt.xlabel("Rank")
    plt.xlim([0, len(degree_sequence)])
    plt.show(block=False)
    plt.pause(0.01)

def check_free_scale(G):
    degree_sequence = sorted((d for n, d in G.degree()), reverse=True)
    #fit = powerlaw.Fit(degree_sequence) 
    fit = powerlaw.Fit(degree_sequence, xmin=1)
    print('Power-law check: ')
    print('alpha= '+str(fit.alpha)+'; sigma: '+str(fit.sigma))

    plt.figure()
    fig = fit.plot_pdf(color='b', linewidth=2)
    fit.power_law.plot_pdf(color='g', linestyle='--', ax=fig)
    plt.show(block=False)
    plt.pause(0.01)
    
    # Small-worldness (Hard Computation)  > 1 day
    skip = True
    if not skip:
        start = time.time()
        nx.sigma(G) # check computational complexity
        nx.omega(G)
        print('Small-worldness check:')
        print('sigma: '+str(nx.sigma(G)))
        print('omega: '+str(nx.omega(G)))
        end = time.time()
        print('Small-worldness Calculated! Time: '+str(end-start))

    