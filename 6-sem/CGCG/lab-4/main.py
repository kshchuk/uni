# Динамічна підтримка опуклої оболонки (Overmars, van Leeuwen).

import matplotlib.pyplot as plt

from convex_hull import DynamicConvexHull
from node import Classification, Point


points = [Point(-1, -1),
          Point(0, 0),
          Point(6, 10),
          Point(3, 6),
          Point(-5, -3),
          Point(7, 7)]

pointsDelete = [Point(5, -3),
                Point(6, 10)]

dynamicConvexHull = DynamicConvexHull()

for point in points:
    figure, axes = plt.subplots(nrows=1, ncols=1, figsize=(10, 10))
    axes.set_title("Add " + str(point))
    dynamicConvexHull.insert(point)
    dynamicConvexHull.plot(figure, axes)
    plt.show()

for point in pointsDelete:
    figure, axes = plt.subplots(nrows=1, ncols=1, figsize=(10, 10))
    axes.set_title("Delete " + str(point))
    dynamicConvexHull.delete(point)
    dynamicConvexHull.plot(figure, axes)
    plt.show()
