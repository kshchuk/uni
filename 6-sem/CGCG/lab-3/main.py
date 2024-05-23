# Найближча пара множини точок на площині – метод «розділяй і владарюй».

import matplotlib.pyplot as plt
from point import Point
from closest_points import findClosestPair
from distance import dist

points = [Point(8, 11), Point(6, 6), Point(8, 1), Point(1, 3), Point(2, 16),
          Point(15, 7), Point(7, 5), Point(4, 10), Point(9, 2), Point(11, 11),
          Point(5, 8)]

closestPoints = findClosestPair(points)
minDist = dist(closestPoints[0], closestPoints[1])

fig, ax = plt.subplots(figsize=(8, 8))
for point in points:
    if point in closestPoints:
        ax.scatter(*[point.x, point.y], color='red')
    else:
        ax.scatter(*[point.x, point.y], color='blue')

closestPointsX = (closestPoints[0].x, closestPoints[1].x)
closestPointsY = (closestPoints[0].y, closestPoints[1].y)
plt.plot(closestPointsX, closestPointsY, color="red")

centerX = sum(closestPointsX) / 2
centerY = sum(closestPointsY) / 2
plt.text(centerX, centerY + 1, "%.2f" % minDist)

plt.show()
