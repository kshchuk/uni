import json

import networkx as nx
from matplotlib import pyplot as plt

from vertex import Vertex, Point
from edge import Edge


class Graph:
    def __init__(self):
        self.vertices = []
        self.edges = {}

    def addVertex(self, vertex: Vertex) -> None:
        if vertex not in self.vertices:
            self.vertices.append(vertex)
            self._sortVertices()

    def addVertices(self, vertices: list[Vertex]) -> None:
        for vertex in vertices:
            self.addVertex(vertex)

    def addEdge(self, v1: Vertex, v2: Vertex, weight: int = 1) -> None:
        if v1 not in self.vertices:
            self.vertices.append(v1)
            self._sortVertices()
        if v2 not in self.vertices:
            self.vertices.append(v2)
            self._sortVertices()

        self.edges[(v1, v2)] = Edge(v1, v2, weight)
        v1.addOutVertex(v2, weight)
        v2.addInVertex(v1, weight)

    def addEdges(self, edges: list[Edge]) -> None:
        for edge in edges:
            self.addEdge(edge.v1, edge.v2, edge.weight)

    def checkRegularity(self) -> bool:
        for i in range(1, len(self.vertices) - 1):
            vertex = self.vertices[i]
            if len(vertex.inVertices) == 0 or len(vertex.outVertices) == 0:
                return False
        return True

    def regularize(self) -> None:
        for i in range(1, len(self.vertices) - 1):
            vertex = self.vertices[i]
            if len(vertex.inVertices) == 0:
                v1 = vertex
                v2 = vertex.mostLeftOutVertex()
                while v2 is not None:
                    self.addEdge(v1, v2)
                    v1 = v2
                    v2 = v1.mostLeftOutVertex()
            if len(vertex.outVertices) == 0:
                v1 = vertex
                v2 = vertex.mostLeftInVertex()
                while v2 is not None:
                    self.addEdge(v2, v1)
                    v1 = v2
                    v2 = v1.mostLeftInVertex()

    def save_to_file(self, filename: str) -> None:
        graph_dict = {
            "vertices": [(vertex.location.x, vertex.location.y) for vertex in self.vertices],
            "edges": [(self.vertices.index(edge[0]), self.vertices.index(edge[1])) for edge in self.edges.keys()]
        }
        with open(filename, 'w') as f:
            json.dump(graph_dict, f)

    def load_from_file(self, filename: str) -> None:
        with open(filename, 'r') as f:
            graph_dict = json.load(f)
        vertices = [Vertex(location=Point(x, y)) for x, y in graph_dict["vertices"]]
        edges = [Edge(vertices[i], vertices[j], 1) for i, j in graph_dict["edges"]]
        self.addVertices(vertices)
        self.addEdges(edges)

    def visualize(self, point: Point = None):
        G = nx.DiGraph()
        labels = {}
        edge_labels = {}

        for vertex in self.vertices:
            G.add_node(vertex.key, pos=(vertex.location.x, vertex.location.y))
            labels[vertex.key] = str(vertex.key)

        for edge in self.edges.values():
            G.add_edge(edge.v1.key, edge.v2.key)
            edge_labels[(edge.v1.key, edge.v2.key)] = str(edge.weight)

        if point is not None:
            G.add_node('Point', pos=(point.x, point.y))
            labels['Point'] = 'p'

        pos = nx.get_node_attributes(G, 'pos')
        nx.draw(G, pos, labels=labels, with_labels=True, node_size=500, node_color='skyblue')
        nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_color='red')
        plt.show()

    def __str__(self):
        return '\n'.join([str(edge) for edge in self.edges.values()])

    def _sortVertices(self):
        self.vertices.sort()
        for i, vertex in enumerate(self.vertices):
            if not vertex.hasImmutableKey:
                vertex.id = i

