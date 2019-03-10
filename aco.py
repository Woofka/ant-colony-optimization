import random


class AntColony:
    def __init__(self, antsNum, alpha, beta, pheromoneQantity, pheromoneElite, pheromoneEvaporation):
        self.antsNum              = antsNum  # количество муравьев в колонии
        self.alpha                = alpha    # степень влияния эвристического расстояния на выбор пути
        self.beta                 = beta     # степень влияния концентрации феромона на выбор пути
        self.pheromoneQantity     = pheromoneQantity      # множитель количества феромона, оставляемого муравьями
        self.pheromoneElite       = pheromoneElite        # множитель усиления наилучшего пути (феромон элитных муравьев)
        self.pheromoneEvaporation = pheromoneEvaporation  # доля испаряющегося феромона
        self.verticesNum          = 0        # число вершин матрицы
        self.matrixCost           = []       # матрица смежности со стоимостью пути
        self.matrixPheromone      = []       # матрица смежности с концентрациями феромона
        self.antsRoutes           = []       # список маршрутов, пройденных муравьями
        self.routesCosts          = []       # список стоимостей соответствующих маршрутов
        self.bestRoute            = []       # кратчайший маршрут
        self.bestRouteCost        = 0        # стоимость кратчайшего маршрута

    def routeCost(self, route):
        """
        Возвращает стоимость маршрута <route> согласно матрице смежности <self.matrixCost>
        Где <route> - последовательность прохождения вершин графа, например: [1, 3, 2, 1]
        """
        cost = 0
        for k in range(len(route) - 1):
            cost += self.matrixCost[route[k + 1]][route[k]]
        return cost

    def readMatrix(self):
        """ Считывает матрицу смежности <self.matrixCost> из stdin и инициализирует кол-во вершин графа <self.verticesNum> """
        row = input()
        self.matrixCost.append(list(map(int, row.split())))
        self.verticesNum = len(self.matrixCost[0])
        for i in range(self.verticesNum - 1):
            row = input()
            self.matrixCost.append(list(map(int, row.split())))

    def initPhMap(self):
        """ Инициализирует случайную матрицу смежности <self.matrixPheromone>, содержащую концентрации феромона от 0.01 до 0.05 """
        self.matrixPheromone = [[0 if i == j else random.randint(10, 50) / 1000 for i in range(self.verticesNum)] for j in range(self.verticesNum)]

    def initAnts(self):
        """ Инициализирует начальное положение муравьев в <self.antsRoutes> и длины их маршрутов <self.routesLengths> """
        self.antsRoutes = [[i % self.verticesNum] if i > self.verticesNum - 1 else [i] for i in range(self.antsNum)]
        self.routesCosts = [0 for i in range(self.antsNum)]

    def initBestRoute(self):
        """ Инициализирует начальный кратчайший маршрут <self.bestRoute> и его стоимость <self.bestRouteCost> """
        self.bestRoute = [i for i in range(self.verticesNum)]
        self.bestRoute.append(0)
        self.bestRouteCost = self.routeCost(self.bestRoute)

    def calculateRoutes(self):
        """ Для каждого k-го муравья в колонии просчитывает маршрут <self.antsRoutes[k]> и вычисляет его стоимость <self.routesCosts[k]> """
        for k in range(self.antsNum):
            for y in range(self.verticesNum - 2):
                i = self.antsRoutes[k][-1]
                sumValue = 0.0
                probability = []
                for j in range(self.verticesNum):
                    if j not in self.antsRoutes[k]:
                        TauNu = (1 / self.matrixCost[j][i]) ** self.alpha * self.matrixPheromone[j][i] ** self.beta  # величина целесообразности перехода из вершины i в вершину j
                        sumValue += TauNu
                        probability.append([TauNu, j])
                previousValue = 0
                randomInteger = random.randint(0, 99)
                if sumValue == 0.0:
                    sumValue += 0.000001
                for z in probability:
                    z[0] = previousValue + 100 * z[0] / sumValue  # вероятность перехода из вершины i в вершину j на отрезке от 0 до 100
                    previousValue = z[0]
                    if randomInteger <= z[0]:  # если случайное число попало в текущий промежуток на отрезке
                        self.antsRoutes[k].append(z[1])
                        break
            for j in range(self.verticesNum):  # нахождение последней непосещенной вершины
                if j not in self.antsRoutes[k]:
                    self.antsRoutes[k].append(j)
                    self.antsRoutes[k].append(self.antsRoutes[k][0])
                    break
            self.routesCosts[k] = self.routeCost(self.antsRoutes[k])  # замыкание маршрута

    def updateBestRoute(self):
        """ Обновляет кратчайший машрут <self.bestRoute> и его стоимость <self.bestRouteCost> """
        bestAnt = -1
        bestCost = self.bestRouteCost
        for k in range(self.antsNum):
            if self.routesCosts[k] < bestCost:
                bestAnt = k
                bestCost = self.routesCosts[k]
        if bestAnt != -1:
            self.bestRouteCost = self.routesCosts[bestAnt]
            self.bestRoute = self.antsRoutes[bestAnt]

    def updatePheromone(self):
        """ Обновляет концентрации феромонов в матрице <self.matrixPheromone> """
        deltaMatrixPheromone = [[0.0 for i in range(self.verticesNum)] for j in range(self.verticesNum)]
        for k in range(self.antsNum):
            for i in range(len(self.antsRoutes[k]) - 1):
                deltaMatrixPheromone[self.antsRoutes[k][i + 1]][self.antsRoutes[k][i]] += self.pheromoneQantity / self.routesCosts[k]
            deltaMatrixPheromone[self.antsRoutes[k][0]][self.antsRoutes[k][-1]] += self.pheromoneQantity / self.routesCosts[k]
            self.antsRoutes[k] = [self.antsRoutes[k][-1]]
        for i in range(len(self.bestRoute) - 1):
            deltaMatrixPheromone[self.bestRoute[i + 1]][self.bestRoute[i]] += self.pheromoneElite * self.pheromoneQantity / self.bestRouteCost
        for j in range(self.verticesNum):
            for i in range(self.verticesNum):
                self.matrixPheromone[j][i] = (1 - self.pheromoneEvaporation) * self.matrixPheromone[j][i] + deltaMatrixPheromone[j][i]

    def aco(self, tmax):
        """ Основной цикл муравьиного алгоритма. Ищет кратчайший маршрут в течение <tmax> итераций """
        self.readMatrix()
        self.initPhMap()
        self.initAnts()
        self.initBestRoute()
        for t in range(tmax):
            self.calculateRoutes()
            self.updateBestRoute()
            self.updatePheromone()


# ----- MAIN PROGRAM -----
colony = AntColony(antsNum=20, alpha=0.311, beta=1, pheromoneQantity=0.645, pheromoneElite=1.6, pheromoneEvaporation=0.86)
colony.aco(tmax=500)
print(colony.bestRouteCost)
