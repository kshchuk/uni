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
        common_edges = set(chain_1.edges.keys()).intersection(chain_2.edges.keys())
        for edge in common_edges:
            v1, v2 = edge.v1, edge.v2
            self.addEdge(v1, v2, chain_1.edges[edge].weight)
