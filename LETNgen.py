import construction as cs
from LETN import *

# given:
# "0b001001001" return ["001","001","001"] EXTENDED TO LABEL (TESTED)

def split_letns(letns, k, length_label):
    splitted_letns = []
    for i in range(0, len(letns), length_label*k):
        splitted_letns.append(letns[i : i + length_label*k])
    return(splitted_letns)

# given
# LETNS, return
# dict 10x _--> 101 100001001001 etc  EXTENDED TO LABEL (TESTED)

def get_dict(LETNS, k, meta=None, return_statistics=False): 
    '''It generates the dictionary. It takes as input k and LETNS, which is a
    dictionary (referring for instance to one hour of the day, or better to
    local_split) with keys the signatures of the original graph and for values
    their nb of occurrences. The dictionary that it creates puts together the
    LETNSs that have the same key. Then it transforms frequencies into
    probabilities.
    New dictionary example:
    key: 11x
    value: [[110,111],[0.7,0.3]]
    '''
    # new_node == 001,01,0001,00001
    if not(meta == None):
        categories = np.sort(list(np.unique(list(meta.values()))) + ["0"])
        number_categories = len(categories)
        length_label = round(number_categories**(1/2) + 0.5)
        meta_binary = list(itertools.product([0, 1], repeat=length_label))
        meta_dict = dict()
        for i in range(number_categories):
            value = "".join(str(e) for e in meta_binary[i])
            meta_dict[value] = categories[i]
    else:
        length_label = 1
    new_node_list = []
    if not(meta == None):
        for cat in meta_dict.keys():
            node = "0"*k*length_label + cat
            new_node_list.append(node)
    else:
        new_node_list.append("0"*k + "1")
    LETNS_list = list(LETNS.keys())
    diz = dict()
    for letns in LETNS_list:
        if not(meta == None):
            lab_ego = letns[2: 2 + length_label]
            letns = letns[2 + length_label :]
        else:
            letns = letns[2:]
            lab_ego = ""
        if len(letns) % (k+1) == 0:
            splitted_letns = split_letns(letns, k+1, length_label)
            if not(meta == None):
               key = lab_ego
            else:
                key = ""
            for letn in splitted_letns:
                if letn not in new_node_list: # per il caso 001 non serve creare la key, che è semplicemente ""
                    key = key + letn[0:k*length_label]+"x"
           
            if key in diz: # append to diz the new pruned signature with its nb. of occurrences
                diz[key][0].append("0b"+ lab_ego + letns)
                diz[key][1].append(LETNS["0b"+ lab_ego + letns])
            else:
                diz[key] = [["0b" + lab_ego + letns],[LETNS["0b" + lab_ego + letns]]]
    statistics = 0
    for key,value in diz.items():
        summ = sum(diz[key][1]) # from frequences to probabilities
        statistics += summ
        c = 0
        for val in value[1]:
            diz[key][1][c] = diz[key][1][c]/summ
            c = c + 1

    if return_statistics:
        return diz, statistics
    else:
        return diz




# from letns to key
# input: 101-011 --> 01x-11x  EXTENDED TO LABEL (TESTED)
def create_key(letns, k, meta=None):
    if not(meta == None):
        categories = np.sort(list(np.unique(list(meta.values()))) + ["0"])
        number_categories = len(categories)
        length_label = round(number_categories**(1/2) + 0.5)
        key = letns[: length_label]
        letns = letns[length_label :]       
    else:
        length_label = 1
        key = ""
    if len(letns) == 0:
        return key
    else:
        key = key + "x".join(split_letns(letns, k, length_label)) + "x"
    return key



# counts letns only for a given node EXTENDED LABEL (TESTED)
def count_LETN_given_node(graphs, k, node, meta=None):
    '''It returns all the letns (at each timestamp) of a given node'''
    v = node
    letn = build_LETN(graphs[: k+1], v) # letn is a nx.graph representing the motif with node v as ego
    if not letn == None:
        if not(meta==None):
            letns, node_encoding = get_LETNS_with_encoding(letn, meta, v) # letns is the corresponding signature and node_encoding tells the node identity
        else:
            letns, node_encoding = get_LETNS_with_encoding(letn, meta) # letns is the corresponding signature and node_encoding tells the node identity
        return (letns[2 :], node_encoding)
    else:
        return None


# get letns and node generating letns EXTENDEND LABEL (NOT TESTED)
def get_LETNS_with_encoding(letn, meta=None, ego_node=None):
    '''It translates the letn (a nx.graph) in signature. It return the signature letns and
    node_encoding, which tells at which node the signature is referring.
    For instance:
    letns,node_encoding = 1011 {'65': '10', '56': '11'}
    means that node n has had an interaction 10 with node 65 and
    an interaction 11 with node 56.
    '''
    nodes = list(letn.nodes())
    nodes_no_ego = []
    ids_no_ego = []
    lenght_LETNS = 0
    #ego = ego_node
    for n in nodes:
        if not ("*" in n):
            nodes_no_ego.append(n)
            if not(n.split("_")[0] in ids_no_ego):
                ids_no_ego.append(n.split("_")[0])
        else:
            #ego = int(n.split("*")[0])
            #print(ego)
            lenght_LETNS = lenght_LETNS + 1

    node_encoding = get_node_encoding(ids_no_ego, nodes_no_ego, lenght_LETNS)
    
    if not(meta == None): #and ego != None:
        node_encoding, ego_encoding = get_node_encoding_labeled(meta, node_encoding, ego_node)

    for k in node_encoding.keys():
        node_encoding[k] = ''.join(str(e) for e in node_encoding[k])

    binary_node_encodings = list(node_encoding.values())
    binary_node_encodings.sort()
    

    letns = '0b'+''.join(e for e in binary_node_encodings)

    if not (meta == None): # and ego != None:
        letns  = '0b'+''.join(str(e) for e in ego_encoding) + letns[2:]

    return(letns, node_encoding)




import random


# given diz and key:
# return a key according to the probablity.
def get_random_letns(diz, key, k, meta=None):   #EXTENDED TO LABEL (NOT TESTED)
    '''It returns a new letns (like 101), given a key (like 10x), according to the probability stored in the dictionary.'''
    
    if not(meta == None):
        categories = np.sort(list(np.unique(list(meta.values()))) + ["0"])
        number_categories = len(categories)
        length_label = round(number_categories**(1/2) + 0.5)
    else:
        length_label = 1

    if (key in diz):
        letns = diz[key][0]
        prob = diz[key][1]
        cumulative = [sum(prob[0 : i+1]) for i in range(len(prob))]
        cumulative = [0] + cumulative
        r = random.random()
        for i in range(len(cumulative) - 1):
            if r >= cumulative[i]  and r < cumulative[i+1]:
                return letns[i]
            
    elif (key[:-(k*length_label + 1)] in diz): # approximate key if the original key is not found
        key = key[:-(k*length_label + 1)]
        letns = diz[key][0]
        prob = diz[key][1]
        cumulative = [sum(prob[0: i+1]) for i in range(len(prob))]
        cumulative = [0] + cumulative
        r = random.random()
        for i in range(len(cumulative) - 1):
            if r >= cumulative[i]  and r < cumulative[i+1]:
                return letns[i]
    else:
        return None





# create edge_list_g2: 
# given letns2 and letns3 merge them to create edge_list in g2
def create_edge_g2(n, letns3, node_encoding, k, meta=None):   #EXTENDED TO LABEL (NOT TESTED)
    '''
    It returns the list of edges to add at the (k+1)-th layer, given node n and the
    egocentric neighborhood letns3.
    Example:
    n = 36
    letns3 = '0b100100100111'
    node_enc = {'99': '10', '56': '10', '65': '11', '32': '10'}
    Returns [(36, 65)]
    '''
    if not(meta == None):
        categories = np.sort(list(np.unique(list(meta.values()))) + ["0"])
        number_categories = len(categories)
        length_label = round(number_categories**(1/2) + 0.5)
        meta_binary = list(itertools.product([0, 1], repeat=length_label))
        meta_dict = dict()
        for i in range(number_categories):
            value = "".join(str(e) for e in meta_binary[i])
            meta_dict[value] = categories[i]
    else:
        length_label = 1

    new_node_list = []
    if not(meta == None):
        for cat in meta_dict.keys():
            node = "0"*k*length_label + cat
            new_node_list.append(node)
        letns3 = letns3[2 + length_label :]
    else:
        new_node_list.append("0"*k + "1")
        letns3 = letns3[2 :]
    
    edges = []

    for split in split_letns(letns3, k+1, length_label):
       
        if split in new_node_list:
            if not (meta==None):
                edges.append((n, split[-length_label:]))
            else:
                edges.append((n,"x"))

        elif split[-length_label :].count("1") > 0:
            # search node correspondency in node_embedding and remove:
            for key, value in node_encoding.items():
                if value == split[: k*length_label]:
                    edges.append((n, int(key)))
                    node_encoding[key] = "USED"

    return edges


# split ("x","a") and ("a","b")  #EXTENDED TO LABEL (TESTED)
def split_stub(e):
    '''Given a list of edges, it discerns between directed edges and stubs'''
    edges = []
    stubs = []
    
    for i,j in e:
        if type(i) == str or type(j)== str:
            stubs.append((i, j))
        else:
            edges.append((i, j))

    return edges,stubs



################ TEST
def get_edges_to_keep(edges,alpha=0.5): #EXTENDED TO LABEL (TESTED)
    '''Given the list of directed edges, it returns only the bidirectional ones
    + a fraction alpha of the others.
    '''

    edges_to_keep = []
    #print('Initial nb of edges:', len(edges))
    for (i, j) in edges:
        if (j, i) in edges:
            if (i, j) not in edges_to_keep and (j, i) not in edges_to_keep:
                edges_to_keep.append((i, j))
                edges.remove((i, j))
                edges.remove((j, i))

    nb_edges = len(edges)
    #print('Bidirectional edges to keep:',len(edges_to_keep))
    #print('Nb of remaining edges:', len(edges))
    nb_edges = int(len(edges)*alpha) # si approssima per difetto, che succede se si approssima per eccesso?
    #print('Nb of remaining edges we want to keep:', nb_edges)

    np.random.shuffle(edges)
    edges_to_keep.extend(edges[0 : nb_edges])
    #print('Total nb of edges to keep:',len(edges_to_keep))

    return edges_to_keep


def get_stub(stubs, edg, meta=None):

    categories = np.sort(list(np.unique(list(meta.values()))) + ["0"])
    number_categories = len(categories)
    length_label = round(number_categories**(1/2) + 0.5)
    meta_binary = list(itertools.product([0, 1], repeat=length_label))
    meta_dict = dict()
    for i in range(number_categories):
        value = "".join(str(e) for e in meta_binary[i])
        meta_dict[categories[i]] = value
    np.random.shuffle(stubs)
    edges = []
    remaining_stub = stubs.copy()
    
    for i in range(len(stubs)-1):
        if stubs[i] in remaining_stub:
           u = stubs[i][0]
           lab_u = meta_dict[meta[u]]
           lab_desired = stubs[i][1]
           for j in range(i+1,len(stubs)):
               if stubs[j] in remaining_stub:
                   v = stubs[j][0]
                   if v != u:
                      lab_v = meta_dict[meta[v]]
                      if lab_v == lab_desired and lab_u == stubs[j][1]:
                          if (u,v) not in edges and (v,u) not in edges and (u,v) not in edg and (v,u) not in edg:
                             edges.append((u,v))
                             remaining_stub.remove(stubs[i])
                             remaining_stub.remove(stubs[j])
                             break
                          
    remaining_stub_2 = remaining_stub.copy()

    for i in range(len(remaining_stub)-1):
        if remaining_stub[i] in remaining_stub_2:
           u = remaining_stub[i][0]
           lab_u = meta_dict[meta[u]]
           lab_desired = remaining_stub[i][1]
           for j in range(i+1,len(remaining_stub)):
               if remaining_stub[j] in remaining_stub_2:
                   v = remaining_stub[j][0]
                   if v != u:
                      lab_v = meta_dict[meta[v]]
                      if lab_v == lab_desired or lab_u == remaining_stub[j][1]:
                          if (u,v) not in edges and (v,u) not in edges and (u,v) not in edg and (v,u) not in edg:
                             edges.append((u,v))
                             remaining_stub_2.remove(remaining_stub[i])
                             remaining_stub_2.remove(remaining_stub[j])
                             break
    
    for i in range(len(remaining_stub_2)):
        u = remaining_stub_2[i][0]
        lab_desired = remaining_stub_2[i][1]
        keys = [key for key, val in meta.items() if meta_dict[val] == lab_desired]
        if len(keys) > 0:
            iter = 0
            found = False
            while iter < len(keys) and found==False:
                node = random.choice(keys)
                iter += 1
                if u != node and (u,node) not in edges and (node, u) not in edges and (u,node) not in edg and (node,u) not in edg:
                    edges.append((u, node))
                    found = True

    return edges



# merge stubs
# take in input [(91, 'x'), (42, 'x'), (60, 'x'), (78, 'x'), (77, 'x'), (21, 'x')]
# return (91,42),(60,21) etc
def merge_stubs(stubs, edg, meta=None):    #EXTENDED TO LABEL (TESTED)
    edges = []

    if not (meta==None):
        edges = get_stub(stubs, edg, meta)
        return edges

    np.random.shuffle(stubs)
    

    node_seq = []
    for i in range(len(stubs)):
        u = stubs[i][0]
        node_seq.append(u)
    flag = True
    while flag:
        if len(node_seq) >= 2:
            u = np.random.choice(node_seq)
            node_seq.remove(u)
            v = np.random.choice(node_seq)
            node_seq.remove(v)
            if not u == v:
                edges.append((u, v))

            else:
                node_seq.append(u)
                node_seq.append(v)
                if len(np.unique(node_seq))==1:
                    flag = False
        else:
            flag = False
    return edges


# merge edges and stubs   #EXTENDED TO LABEL (TESTED)
def get_edges_g2(edges, alpha, meta=None):

    edges_1,stubs = split_stub(edges)
    edges_g2 = get_edges_to_keep(edges_1, alpha)
    edg = edges_g2.copy()
    edges_g2.extend(merge_stubs(stubs, edg, meta))

    return edges_g2



# given node ed edges build graph g3 EXTENDED TO LABEL (not tested)
def build_graph_g2(edges, nodes):

    g2 = nx.Graph()
    g2.add_nodes_from(nodes)
    g2.add_edges_from(edges)

    return g2



# given g0,g1,diz and nodes retrung a nx graph
def generate_graph_g2(nodes, graphs, diz, k, alpha, meta=None):   #EXTENDED TO LABEL (TESTED)
    '''It generates a new temporal layer, given the previous k, the dictionary and the nodes list'''
    #if not(meta == None):
    #   categories = np.sort(list(np.unique(list(meta.values()))) + ["0"])
    #   number_categories = len(categories)
    #   length_label = round(number_categories**(1/2) + 0.5)
    #   meta_binary = list(itertools.product([0, 1], repeat=length_label))
    #   meta_dict = dict()
    #   for i in range(number_categories):
    #       value = "".join(str(e) for e in meta_binary[i])
    #       meta_dict[categories[i]] = value
    edges = []
    for n in graphs[0].nodes(): #build provisional layer
           letns2, node_enc = count_LETN_given_node(graphs, k, n, meta) # letns of the last k layers for node n     
           key = create_key(letns2, k, meta)
           letns3 = get_random_letns(diz, key, k, meta) #i.e. letns3 = '0b100'
           if not letns3 == None:
              edges.extend(create_edge_g2(n, letns3, node_enc, k, meta))
    edges_g2 = get_edges_g2(edges, alpha, meta)
    g2 = build_graph_g2(edges_g2, nodes)
    return g2



#given seed and keys generate temporal graph
def generate_temporal_graph(nb_graphs, graph_seed, diz, k, alpha, meta=None):
    nodes = list(graph_seed[0].nodes())
    tg = graph_seed
    for i in range(nb_graphs - 1):
        graphs_in = tg[i : i+k]
        g_new = generate_graph_g2(nodes, graphs_in, diz, k, alpha, meta)
        tg.append(g_new)
    return tg



# generate a single graph_seed given the previous graphs EXTENDED TO LABELED (TESTED)
def generate_seed_graph(graphs, graphs_seed, k, alpha, meta=None):
    nodes = list(graphs_seed[0].nodes())
    letns = count_LETN(graphs, k, meta)
    letns = {k: v for k, v in sorted(letns.items(), reverse=True, key=lambda item: item[1])}
    LETNS_list = list(letns.keys())
    diz = get_dict(letns, k, meta)
    new_g = generate_graph_g2(nodes, graphs_seed, diz, k, alpha, meta)
    graphs_seed.append(new_g)
    return graphs_seed


# generate k graph seed given g0 EXTENDED TO LABELED (TESTED)
def generate_seed_graphs(g0, graphs, k, alpha, meta=None):
    graphs_seed = [g0]

    for i in range(k-1):
        graphs_seed = generate_seed_graph(graphs, graphs_seed, i+1, alpha, meta)

    return graphs_seed
