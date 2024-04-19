from graph import Graph
from vertex import Vertex
from edge import Edge


class Balancer:
    @staticmethod
    def balance(graph: Graph) -> Graph:
        # assume that edges' weights are initialized to 1 and vertices are sorted

        for i in range(1, len(graph.vertices) - 1):
            vertex = graph.vertices[i]
            win: int = vertex.WinWeightSum()
            v1: Vertex = vertex.mostLeftOutVertex()
            d1: Edge = graph.edges[(vertex, v1)]
            vout: int = len(vertex.outVertices)
            if win > vout:
                newWeight = win - vout + 1
                d1.weight = newWeight
                v1.modifyInWeight(vertex, newWeight)
                vertex.modifyOutWeight(d1, newWeight)

        for i in range(len(graph.vertices) - 2, 0, -1):
            vertex = graph.vertices[i]
            wout: int = vertex.WoutWeightSum()
            win: int = vertex.WinWeightSum()
            v2: Vertex = vertex.mostLeftInVertex()
            d2: Edge = graph.edges[(v2, vertex)]
            if wout > win:
                newWeight = wout - win + d2.weight
                d2.weight = newWeight
                v2.modifyOutWeight(vertex, newWeight)
                vertex.modifyInWeight(d2, newWeight)

        return graph
