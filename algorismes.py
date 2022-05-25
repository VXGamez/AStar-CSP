import json
import time
import geopy.distance

idCounter = 0
origen = "Barcelona"
desti = "Tremp"


class Edge:
    def __init__(self, weight, node):
        self.weight = weight
        self.node = node

    def __str__(self):
        return "\n\t{\n\t\tWeight: " + str(self.weight) + "\n\t\tNode: " + self.node.name + "\n\t}"

    def __repr__(self):
        return str(self)


class Node:
    f = float("inf")
    g = float("inf")
    parent = None

    def __init__(self, name, address, country, latitude, longitude):
        self.h = None
        global idCounter
        self.name = name
        self.address = address
        self.country = country
        self.latitude = latitude
        self.longitude = longitude
        self.id = idCounter
        idCounter += 1
        self.neighbors = []

    def __str__(self):
        return "{\n\tName: " + self.name + "\n\tAddress: " + self.address + "\n\tneighbours: " + str(
            self.neighbors) + "\n}"

    def __repr__(self):
        return str(self)

    def compareTo(self, node):
        return self.f > node.f

    def addBranch(self, weight, node):
        self.neighbors.append(Edge(weight, node))

    def calculateHeuristic(self, target):
        coords_1 = (self.latitude, self.longitude)
        coords_2 = (target.latitude, target.longitude)
        self.h = geopy.distance.geodesic(coords_1, coords_2).m
        return self.h

    def getName(self):
        return self.name

    def getWeight(self, t):
        for k in self.neighbors:
            if k.node.name == t.name:
                return k.weight
        return 0


def aStar(start, target):
    closedList = []
    openList = []

    if start is None:
        return None

    start.f = start.g + start.calculateHeuristic(target)
    openList.append(start)

    while len(openList) > 0:
        n = openList[0]
        if n == target:
            return n

        for e in n.neighbors:
            m = e.node
            totalWeight = n.g + e.weight

            if m not in openList and m not in closedList:
                m.parent = n
                m.g = totalWeight
                m.f = m.g + m.calculateHeuristic(target)
                openList.append(m)
            else:
                if totalWeight < m.g:
                    m.parent = n
                    m.g = totalWeight
                    m.f = m.g + m.calculateHeuristic(target)
                    if m in closedList:
                        closedList.remove(m)
                        openList.append(m)

        openList.remove(n)
        closedList.append(n)
    return None


def csp(start, target):
    steps = []
    visited = []
    steps.append(start)
    n = start
    while n != target:
        if len(n.neighbors) > 0:
            max = n.neighbors[0]
            if n not in visited:
                for f in n.neighbors:
                    if f.node == target:
                        max = f
                        break
                    if len(f.node.neighbors) > len(max.node.neighbors):
                        max = f
            else:
                return None
            steps.append(max)
            visited.append(n)
            max.node.parent = n
            n = max.node
    return n


def printPath(target, temps):
    n = target
    if n is None:
        print("\nNO HI HA RUTA ENTRE " + origen + " I " + desti + " ( " + format(temps, ".4f") + "ms )")
        return

    ids = []

    while n.parent is not None:
        ids.append(n.id)
        n = n.parent

    ids.append(n.id)
    ids.reverse()

    print("\nRECORREGUT ENTRE " + origen + " I " + desti + " ( " + format(temps, ".4f") + "ms )")
    i = 0
    totalKM = 0
    while i < len(ids) - 1:
        totalKM += cities[ids[i]].getWeight(cities[ids[i + 1]])
        print(
            cities[ids[i]].name + "  ---" + str(cities[ids[i]].getWeight(cities[ids[i + 1]])) + "-->  " + cities[
                ids[i + 1]].name)
        i += 1

    print("DISTANCIA TOTAL " + str(totalKM) + "m")

    print("")


def buildGraph():
    f = open("datasets/dades_routes_1.json")
    global data
    data = json.load(f)
    f.close()
    global cities
    cities = []

    for c in data['cities']:
        cities.append(Node(c['name'], c['address'], c['country'], c['latitude'], c['longitude']));

    for c in data['connections']:
        cFrom = findCity(c['from'], cities)
        cTo = findCity(c['to'], cities)
        cFrom.addBranch(c['distance'], cTo)

    return findCity(origen, cities), findCity(desti, cities)


def findCity(name, array):
    for city in array:
        if city.getName() == name:
            return city
    return None


def main():
    head, target = buildGraph()
    print("\n---------------- A* ----------------")
    start = time.time()
    res = aStar(head, target)
    end = time.time()
    printPath(res, (end - start)*1000)
    print("------------------------------------")
    print("\n---------------- CSP ----------------")
    start = time.time()
    res = csp(head, target)
    end = time.time()
    printPath(res, (end - start)*1000)
    print("------------------------------------\n")


if __name__ == '__main__':
    main()
