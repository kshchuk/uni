from chain import Chain
from graph import Graph


class Polygon(Graph):
    def __init__(self):
        super().__init__()

    def buildPolygon(self, chain_1: Chain, chain_2: Chain) -> None:
        """Build a polygon from two chains

        Complexity:
            - Average:     O(min(len(chain_1), len(chain_2))
            - Worst case:  O(len(chain_1) * len(chain_2))

        :param chain_1: the first chain
        :param chain_2: the second chain"""
        non_common_edges = []
        for edge in chain_1.edges:
            if edge not in chain_2.edges:
                non_common_edges.append(edge)
        for edge in chain_2.edges:
            if edge not in chain_1.edges:
                non_common_edges.append(edge)

        for edge in non_common_edges:
            self.addEdge(edge[0], edge[1])

