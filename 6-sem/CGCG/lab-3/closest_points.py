from point import Point
from distance import dist


def findClosestPointsBruteForce(points):
    minDist = float("inf")
    closestPoints = []
    for i in range(0, len(points)):
        for j in range(i + 1, len(points)):
            currentDist = dist(points[i], points[j])
            if currentDist < minDist:
                closestPoints = [points[i], points[j]]
                minDist = currentDist
    return closestPoints


def findClosestPointsStrip(strip):
    minDist = float("inf")
    closestPoints = []

    strip = sorted(strip, key=lambda point: point.y)

    for i in range(0, len(strip)):
        for j in range(i + 1, len(strip)):
            if (strip[j].y - strip[i].y) >= minDist:
                break

            currentDist = dist(strip[i], strip[j])
            if currentDist < minDist:
                closestPoints = [strip[i], strip[j]]
                minDist = currentDist

    return closestPoints


def findClosestPointsRecursive(points, n):
    if n <= 3:
        return findClosestPointsBruteForce(points)

    center = n // 2
    centralPoint = points[center]

    leftClosestPoints = findClosestPointsRecursive(points, center)
    minDistLeft = dist(leftClosestPoints[0], leftClosestPoints[1])

    rightClosestPoints = findClosestPointsRecursive(points[center:], n - center)
    minDistRight = dist(rightClosestPoints[0], rightClosestPoints[1])

    if minDistLeft < minDistRight:
        minDist = minDistLeft
        closestPoints = leftClosestPoints
    else:
        minDist = minDistRight
        closestPoints = rightClosestPoints

    strip = []
    for i in range(0, n):
        if abs(points[i].x - centralPoint.x) < minDist:
            strip.append(points[i])

    minDistStrip = float("inf")
    if (len(strip) > 1):
        stripClosestPoints = findClosestPointsStrip(strip)
        minDistStrip = dist(stripClosestPoints[0], stripClosestPoints[1])

    if minDistStrip <= minDist:
        closestPoints = stripClosestPoints

    return closestPoints


def findClosestPair(points):
    points = sorted(points, key=lambda point: point.x)
    return findClosestPointsRecursive(points, len(points))
