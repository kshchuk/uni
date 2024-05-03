from balancer import Balancer
from chain import Chain
from graph import Graph
from vertex import Point
from polygon import Polygon

point = Point(0, 0)


if __name__ == '__main__':
    graph = Graph()
    graph.load_from_file("graph_1.json")

    if not graph.checkRegularity():
        graph.regularize()

    graph.visualize(point)
    graph = Balancer.balance(graph)
    graph.visualize(point)

    chains = Chain.getChains(graph)
    for chain in chains:
        chain.visualize()

    Chain1, Chain2 = Chain.localizePoint(chains, point)

    Chain1.visualize()
    Chain2.visualize()

    polygon = Polygon()
    polygon.buildPolygon(Chain1, Chain2)
    polygon.visualize(point)



