from vertex import Vertex
from edge import Edge


class Graph:
    def __init__(self):
        self.vertices = []
        self.edges = {}

    def __init__(self, vertices):
        self.vertices: list[Vertex] = vertices
        self.edges = {}

        self._sortVertices()

    def addVertex(self, vertex: Vertex) -> None:
        if vertex not in self.vertices:
            self.vertices.append(vertex)
            self._sortVertices()

    def addEdge(self, v1: Vertex, v2: Vertex, weight: int = 1) -> None:
        if v1 not in self.vertices:
            self.vertices.append(v1)
            self._sortVertices()
        if v2 not in self.vertices:
            self.vertices.append(v2)
            self._sortVertices()

        self.edges[(v1, v2)] = Edge(v1, v2, weight)
        v1.addInVertex(v2, weight)
        v2.addOutVertex(v1, weight)

    def checkRegularity(self) -> bool:
        for vertex in self.vertices:
            if len(vertex.inVertices) == 0 or len(vertex.outVertices) == 0:
                return False
        return True

    def __str__(self):
        return '\n'.join([str(edge) for edge in self.edges.values()])

    def _sortVertices(self):
        self.vertices.sort()
        for i, vertex in enumerate(self.vertices):
            if not vertex.hasImmutableKey:
                vertex.id = i
