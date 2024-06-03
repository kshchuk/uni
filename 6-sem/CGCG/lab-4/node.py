from enum import Enum

import numpy


class Point:
    i = 0

    def __init__(self, x_, y_):
        self.x = x_
        self.y = y_
        self.id = Node.i
        Node.i += 1

    def __repr__(self):
        return str(f"({self.x}; {self.y})")

    def __lt__(self, other):
        return self.x < other.x or (self.x == other.x and self.y < other.y)


class NodeData:
    def __init__(self, key=None):
        self.left_most_right: Node = None
        self.left_most_right_point: Point = key
        self.points_array = []
        self.separating_index = 0
        self.convex_hull = []
        self.graph_hull = []
        self.convex_hull.append(key)

    def __lt__(self, other):
        return self.left_most_right_point < other.left_most_right_point

    def __repr__(self):
        return str(f"{self.left_most_right_point}; {self.points_array}; {self.separating_index}")


class NodeColor(Enum):
    RED = 1
    BLACK = 2


class Classification(Enum):
    CONVEX = 1
    CONCAVE = 2
    SUPPORTING = 3
    ERROR = -1


class Node:
    i = 0

    def __init__(self, data):
        self.data: NodeData = data
        self.parent: Node = None
        self.left: Node = None
        self.right: Node = None
        self.color = NodeColor.RED
        self.id = Node.i
        Node.i += 1

    def __lt__(self, other):
        return self.data < other.data

    def __repr__(self):
        return str(f"{self.id}: {self.data}")

    def plot(self, figure, axes, TNULL, lower=False):
        if self is None or self == TNULL:
            return figure, axes

        if self.left == TNULL:
            point_x, point_y = self.data.left_most_right_point.x, self.data.left_most_right_point.y
            point_id = self.data.left_most_right_point.id
            if lower:
                point_y *= -1
            axes.scatter([point_x], [point_y], color="red")
            axes.annotate(f"({point_id}); ({point_x}; {point_y})", (point_x, point_y),
                          xytext=(point_x - 0.025, point_y + 0.1))
            return figure, axes

        chain = self.data.graph_hull
        if self.parent == TNULL:
            chain = self.data.points_array
        color = numpy.random.rand(3, )

        for i in range(1, len(chain)):
            if lower:
                axes.plot([chain[i - 1].x, chain[i].x], [-1 * chain[i - 1].y, -1 * chain[i].y], color=color)
            else:
                axes.plot([chain[i - 1].x, chain[i].x], [chain[i - 1].y, chain[i].y], color=color)

        if self.left != TNULL:
            self.left.data.graph_hull = chain[:self.data.separating_index + 1] + self.left.data.points_array

        if self.right != TNULL:
            self.right.data.graph_hull = self.right.data.points_array + chain[self.data.separating_index + 1:]

        self.left.plot(figure, axes, TNULL, lower)
        return self.right.plot(figure, axes, TNULL, lower)

    def graph_viz(self, TNULL, string_mutable):
        if self is None or self == TNULL:
            return

        string_mutable[0] += f"\"{self}\""

        if self.color == NodeColor.RED:
            string_mutable[0] += " [color = \"red\"]"
        string_mutable[0] += "\n"

        if self.left != TNULL:
            string_mutable[0] += f"\"{self}\" -> \"{self.left}\" [label = \"left\"]\n"
        if self.right != TNULL:
            string_mutable[0] += f"\"{self}\" -> \"{self.right}\" [label = \"right\"]\n"

        self.left.graph_viz(TNULL, string_mutable)
        self.right.graph_viz(TNULL, string_mutable)
