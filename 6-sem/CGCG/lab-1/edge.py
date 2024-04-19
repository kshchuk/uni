from vertex import Vertex


class Edge:
    def __init__(self, v1: Vertex, v2: Vertex, weight: int):
        self.v1 = v1
        self.v2 = v2
        self.weight = weight

    def __str__(self):
        return f"{self.v1} -- {self.weight} -- {self.v2}"
