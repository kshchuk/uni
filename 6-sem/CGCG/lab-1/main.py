from balancer import Balancer
from chain import Chain
from graph import Graph
from vertex import Vertex, Point

if __name__ == '__main__':
    graph = Graph()
    graph.load_from_file("graph.json")

    graph.visualize()

    graph = Balancer.balance(graph)

    graph.visualize()

    # chains = Chain.getChains(graph)
    # for chain in chains:
    #    chain.visualize()
