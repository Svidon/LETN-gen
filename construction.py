import networkx as nx
import numpy as np
import pandas as pd


def load_data(path,sep=" "):
    """load the cvs file representing the temporal graph

    Parameters:
    path (string): path of the input dataset

    Returns:
    np.array: a np array with the loaded data

    """
    data = pd.read_csv(filepath_or_buffer=path,sep=sep,names=["t","a","b"])
    return(data.astype('int'))


def individuals(data):
    res = []
    res.extend(np.unique(data.a))
    res.extend(np.unique(data.b))
    return(np.unique(res))


def build_graphs(data,gap=19,with_labels=False,meta_path=None):
    graphs = []
    G=nx.Graph()
    nodes = individuals(data)
    G.add_nodes_from(nodes)
    if(with_labels):
        G = add_labels(G,meta_path)
    splitted_data = split_input_data(data,gap)
    for t in splitted_data:
        g = G.copy()
        for _,i,j in t:
            if not i == j:
                g.add_edge(i,j)
        graphs.append(g)  
    return(graphs)


def split_input_data(data, gap=19):
    times = [int(x/(gap+1)) for x in data.t]
    data.t = times
    splitted_data = []
    c = 0 

    for i in range(max(times)+1):
        tmp = data[data.t == i].to_numpy()
        if tmp.shape[0] == 0:
            tmp = [[i,0,0]]

        splitted_data.append(tmp)
    return splitted_data


def load_metadata(path_meta):
    """load the metadata of the temporal graph

    Parameters:
    path_meta (string): path of the meta data

    Returns:
    dict: a dictionary whit key = node and value = attributes

    """
    data = dict()
    with open(path_meta) as f:
        for line in f:
            tmp = line.split()[0:2]

            data[int(tmp[0])] = tmp[1]        

    return(data)


def add_labels(G, meta_path):
    """Summary or Description of the Function

    Parameters:
    argument1 (int): Description of arg1

    Returns:
    int:Returning value

    """
    if isinstance(meta_path, dict):
        meta = meta_path
    else:
        meta = load_metadata(meta_path) #dictionary
    
    for n in G.nodes():
        G.nodes()[n]["label"] = meta[n]
    
    return(G)