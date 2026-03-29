
from collections import deque,defaultdict
import networkx as nx
import matplotlib.pyplot as plt
import pandas as pd
def topoSort_as_full_list(edges):
    # Step 1: get all unique tweet IDs
    tweet_ids = set()
    for u, v in edges:
        tweet_ids.add(u)
        tweet_ids.add(v)
    
    tweet_ids = list(tweet_ids)
    
    # Step 2: create mapping from ID → index and index → ID
    id_to_index = {tid: i for i, tid in enumerate(tweet_ids)}
    index_to_id = {i: tid for i, tid in enumerate(tweet_ids)}
    
    V = len(tweet_ids)
    
    # Step 3: build adjacency list and indegree array
    adj = [[] for _ in range(V)]
    indegree = [0] * V
    
    for u, v in edges:
        u_idx = id_to_index[u]
        v_idx = id_to_index[v]
        adj[u_idx].append(v_idx)
        indegree[v_idx] += 1
    
    # Step 4: Kahn's algorithm
    queue = deque()
    for i in range(V):
        if indegree[i] == 0:
            queue.append(i)
    
    topo = []
    while queue:
        node = queue.popleft()
        topo.append(index_to_id[node])  # convert back to original tweet ID
        
        for neighbor in adj[node]:
            indegree[neighbor] -= 1
            if indegree[neighbor] == 0:
                queue.append(neighbor)
    
    return topo




def topological_sort_threadwise(edges):
    # Build the graph
    graph = defaultdict(list)
    in_degree = defaultdict(int)
    nodes = set()
    
    for u, v in edges:
        graph[u].append(v)
        in_degree[v] += 1
        nodes.add(u)
        nodes.add(v)
    
    # Find all nodes with 0 in-degree
    zero_in_degree = deque([node for node in nodes if in_degree[node] == 0])
    
    visited = set()
    result = []

    # Process each disconnected component
    while zero_in_degree:
        topo_list = []
        queue = deque([zero_in_degree.popleft()])
        while queue:
            node = queue.popleft()
            if node in visited:
                continue
            visited.add(node)
            topo_list.append(node)
            for neighbor in graph[node]:
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)
        if topo_list:
            result.append(topo_list)

        # Add any new zero in-degree nodes for other components
        for node in nodes:
            if node not in visited and in_degree[node] == 0:
                zero_in_degree.append(node)

    if len(visited) != len(nodes):
        print("Cycle detected! Cannot perform valid topological sort.")
    else:
        print("No cycle detected. Topological sort is valid.")
    
    return result



def visualization(df):
        G = nx.DiGraph()

        for _, row in df.iterrows():
            
            tweet_id = row["tweet_id"]
            ref_id = row["referenced_tweets_id"]
            
            G.add_node(tweet_id)

            if pd.notna(ref_id):
                G.add_edge(ref_id, tweet_id)

        plt.figure(figsize=(18,16))

        pos = nx.spring_layout(G)

        nx.draw(
            G,
            pos,
            with_labels=True,
            node_size=2000,
            node_color="lightblue",
            font_size=10,
            arrows=True
        )

        plt.title("Tweet Reference Graph")

        plt.savefig("tweet_graph.png")


        if nx.is_directed_acyclic_graph(G):
            order = list(nx.topological_sort(G))
        else:
            print("Graph has cycles! Cannot perform topological sort.")

        print(order)

        print("Graph saved as tweet_graph.png")



