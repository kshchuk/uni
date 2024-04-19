from graph import Graph


class Chain(Graph):
    def __init__(self):
        super().__init__()

    @staticmethod
    def getChains(graph: Graph) -> list['Chain']:
        chains = []
        chain = Chain()
        for i in range(0, len(graph.vertices) - 1):
            v1 = graph.vertices[i]
            v1.hasImmutableKey = True   # mark to save the order of vertices
            v2 = v1.mostLeftOutVertex()

            while v2 is not None:
                v1 = v2
                v2 = v1.mostLeftOutVertex()
                if v2 is not None:
                    v2.hasImmutableKey = True
                    chain.addEdge(v1, v2)
                    newWeight = --graph.edges[(v1, v2)].weight
                    v1.modifyOutWeight(v2, newWeight)
                    v2.modifyInWeight(v1, newWeight)
                else:
                    chain.addVertex(v1)
                    chains.append(chain)
                    chain = Chain()

        return chains

    @staticmethod
    def localizePoint(chains: list['Chain'], point: 'Point') -> list['Chain']:
        """
        Localize the point in the chains
        :param chains: chains to localize the point
        :param point: point to localize
        :return: two chains between which the point is localized
        """
        for i in range(0, len(chains) - 1):
            chain_1 = chains[i]
            chain_2 = chains[i + 1]
            pointChainSide_1 = 'None'
            pointChainSide_2 = 'None'
            for j in range(0, len(chain_1.vertices) - 1):
                v1 = chain_1.vertices[j]
                v2 = chain_1.vertices[j + 1]


