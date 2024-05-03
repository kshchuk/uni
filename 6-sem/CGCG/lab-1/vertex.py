
class Point:
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y

    def __str__(self):
        return f"({self.x}, {self.y})"


class Vertex:
    def __init__(self, key: int = -1, location: Point = None):
        self._key = key
        self._immutableKey = False  # If True, the key of this vertex should not be changed while sorting
        self._location = location
        self._inVertices = []  # Vertices this vertex is connected to (OUT)
        self._inWeights = {}  # Weights of the connections
        self._outVertices = []  # Vertices connected to this vertex (IN)
        self._outWeights = {}  # Weights of the connections

    def addInVertex(self, other, weight: int = 1) -> None:
        if other not in self._inVertices:
            self._inVertices.append(other)
            self._inWeights[other] = weight

    def modifyInWeight(self, other: 'Vertex', weight: int) -> None:
        self._inWeights[other] = weight

    def addOutVertex(self, other, weight: int = 1) -> None:
        if other not in self._outVertices:
            self._outVertices.append(other)
            self._outWeights[other] = weight

    def modifyOutWeight(self, other: 'Vertex', weight: int) -> None:
        self._outWeights[other] = weight

    def WinWeightSum(self) -> int:
        return sum(self._inWeights.values())

    def WoutWeightSum(self) -> int:
        return sum(self._outWeights.values())

    # Returns the most left vertex connected from this vertex via positive edge.
    # Should be above or on the same y-axis as this vertex.
    def mostLeftOutVertex(self) -> 'Vertex' or None:
        # Get all connected from this vertex that are above this vertex. Also, the weight of the
        # connection should be > 0 in order to be considered.
        upperVertices = [x for x in self._outVertices if x.location.y >= self._location.y and self._outWeights[x] > 0]
        if not upperVertices:
            return None

        # Get all connected from this vertex that are above this vertex and to the left of this vertex
        upperLeftVertices = [x for x in upperVertices if x.location.x <= self._location.x]
        if upperLeftVertices:
            tgs = self._calculateTgs(upperLeftVertices)
            atgs = [abs(x) for x in tgs]
            smallestTgIndex = atgs.index(min(atgs))
            return upperLeftVertices[smallestTgIndex]

        # Get all connected from this vertex that are above this vertex and to the right of this vertex.
        upperRightVertices = [x for x in upperVertices if x.location.x >= self._location.x]
        if upperRightVertices:
            tgs = self._calculateTgs(upperRightVertices)
            atgs = [abs(x) for x in tgs]
            largestTgIndex = atgs.index(max(atgs))
            return upperRightVertices[largestTgIndex]
        else:
            return None

    def mostLeftInVertex(self) -> 'Vertex' or None:
        # Get all connected to this vertex that are above this vertex
        upperVertices = [x for x in self._inVertices if x.location.y <= self._location.y]
        if not upperVertices:
            return None

        # Get all connected to this vertex that are above this vertex and to the left of this vertex
        upperLeftVertices = [x for x in upperVertices if x.location.x <= self._location.x]
        if upperLeftVertices:
            tgs = self._calculateTgs(upperLeftVertices)
            atgs = [abs(x) for x in tgs]
            smallestTgIndex = atgs.index(min(atgs))
            return upperLeftVertices[smallestTgIndex]

        # Get all connected to this vertex that are above this vertex and to the right of this vertex
        upperRightVertices = [x for x in upperVertices if x.location.x >= self._location.x]
        if upperRightVertices:
            tgs = self._calculateTgs(upperRightVertices)
            atgs = [abs(x) for x in tgs]
            largestTgIndex = atgs.index(max(atgs))
            return upperRightVertices[largestTgIndex]

    @property
    def id(self) -> int:
        return self._key

    @id.setter
    def id(self, key: int):
        self._key = key

    @property
    def location(self) -> Point:
        return self._location

    @location.setter
    def location(self, loc: Point):
        self._location = loc

    @property
    def inVertices(self) -> list:
        return self._inVertices

    @property
    def outVertices(self) -> list:
        return self._outVertices

    @property
    def hasImmutableKey(self) -> bool:
        return self._immutableKey

    @property
    def key(self) -> int:
        return self._key

    @hasImmutableKey.setter
    def hasImmutableKey(self, value: bool):
        self._immutableKey = value

    def _calculateTgs(self, vertices: list) -> list:
        dy = [x.location.y - self._location.y for x in vertices]
        dx = [x.location.x - self._location.x for x in vertices]

        return [dy[i] / dx[i] for i in range(len(dy))]

    def __str__(self):
        return (f"{self._key} Connected to: {[x.id for x in self._outVertices]} "
                f"Connected by: {[x.id for x in self._inVertices]}")

    def __eq__(self, other):
        return self._location.x == other.location.x and self._location.y == other.location.y

    def __lt__(self, other):
        if self._location.y == other.location.y:
            return self._location.x < other.location.x
        return self._location.y < other.location.y

    def __hash__(self):
        return hash((self._location.x, self._location.y))
