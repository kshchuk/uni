from enum import Enum

from graph import Graph
from vertex import Vertex, Point


class Chain(Graph):
    def __init__(self):
        super().__init__()

    @staticmethod
    def getChains(graph: Graph) -> list['Chain']:
        chains = []
        chain = Chain()
        for i in range(0, len(graph.vertices) - 1):
            vertex = graph.vertices[i]
            vertex.hasImmutableKey = True  # mark to save the order of vertices

            while vertex.WoutWeightSum() != 0:
                v1 = vertex
                v2 = vertex.mostLeftOutVertex()
                while v2 is not None:
                    v2.hasImmutableKey = True
                    chain.addEdge(v1, v2)
                    newWeight = graph.edges[(v1, v2)].weight - 1
                    graph.edges[(v1, v2)].weight = newWeight
                    v1.modifyOutWeight(v2, newWeight)
                    v2.modifyInWeight(v1, newWeight)

                    v1 = v2
                    v2 = v1.mostLeftOutVertex()
                    if v2 is None:
                        chains.append(chain)
                        chain = Chain()
                        graph.visualize()

        return chains

    @staticmethod
    def localizePoint(chains: list['Chain'], point: Point, mid_index=0) -> tuple['Chain', 'Chain']:
        """
        Localize the point in the chains using Binary Search
        :param chains: chains to localize the point
        :param point: point to localize
        :param mid_index: the index of the middle chain
        :return: the chains between which the point is localized
        """
        if mid_index == 0:
            mid_index = len(chains) // 2

        if len(chains) == 1:
            return chains[0], chains[0]

        if len(chains) == 2:
            return chains[0], chains[1]

        mid_chain = chains[mid_index]
        side, _, _ = Chain._getPosRelToChain(mid_chain, point)
        if side == Chain._Side.ON:
            return mid_chain, mid_chain

        if side == Chain._Side.LEFT:
            return Chain.localizePoint(chains[:mid_index + 1], point, len(chains[:mid_index + 1]) // 2)
        else:
            return Chain.localizePoint(chains[mid_index:], point, len(chains[mid_index:]) // 2)

    class _Side(Enum):
        LEFT = 0
        RIGHT = 1
        ON = 2

    @staticmethod
    def _getPosRelToChain(chain: 'Chain', point: Point) -> tuple[_Side, Vertex, Vertex]:
        """
        Get the position of the point relative to the chain (Left, Right or On the chain)
        :param chain: chain to localize the point
        :param point: point to localize
        :return: the position of the point relative to the chain
        """
        vertices = chain.vertices.copy()
        mid_index = len(vertices) // 2
        v1, v2 = Chain._getPosRelToVerticesRecursive(vertices, point, mid_index)
        if v1 == v2:
            return Chain._Side.ON, v1, v2

        d = ((point.x - v1.location.x) * (v2.location.y - v1.location.y) -
             (point.y - v1.location.y) * (v2.location.x - v1.location.x))

        if d > 0:
            return Chain._Side.RIGHT, v1, v2
        if d < 0:
            return Chain._Side.LEFT, v1, v2
        return Chain._Side.ON, v1, v2

    @staticmethod
    def _getPosRelToVerticesRecursive(vertices: list[Vertex], point: Point, mid_index) -> tuple[Vertex, Vertex]:
        """
        Get the position of the point relative to the vertices using Binary Search

        :param vertices: vertices to localize the point
        :param point: point to localize
        :param mid_index: the index of the middle vertex
        :return: the vertices between which the point is localized
        """
        if len(vertices) == 1:
            return vertices[0], vertices[0]  # the point is localized on the vertex

        if len(vertices) == 2:
            return vertices[0], vertices[1]

        mid_vertex = vertices[mid_index]
        if mid_vertex.location.y == point.y:
            return mid_vertex, mid_vertex

        if mid_vertex.location.y < point.y:
            return Chain._getPosRelToVerticesRecursive(vertices[mid_index:], point,
                                                       len(vertices[mid_index:]) // 2)
        else:
            return Chain._getPosRelToVerticesRecursive(vertices[:mid_index], point,
                                                       len(vertices[:mid_index]) // 2)
