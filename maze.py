"""Модуль для генерации и решения лабиринтов"""


from random import getrandbits
from PIL import Image, ImageDraw


class Maze:
    """Класс для генерации и решения лабиринтов"""

    def __init__(self, rows: int, cols: int) -> None:
        self.rows = rows
        self.cols = cols
        self.maze = [[0] * self.cols for _ in range(self.rows)]
        self.way = None
        self.generate()

    def generate(self) -> None: #pylint: disable=R0912
        """Генерирует лабиринт"""
        index = 2
        for i in range(self.rows):
            for j in range(self.cols):
                if i in (0, self.rows - 1) or j in (0, self.cols - 1):
                    self.maze[i][j] = 1
        for i in range(2, self.rows, 2):
            for j in range(0, self.cols, 2):
                self.maze[i][j] = 1
        for i in range(1, self.cols, 2):
            self.maze[1][i] = index
            index += 1

        for i in range(1, self.rows, 2):
            for j in range(1, self.cols - 2, 2):
                if getrandbits(1):
                    self.maze[i][j + 1] = 1
                elif self.maze[i][j] == self.maze[i][j + 2]:
                    self.maze[i][j + 1] = 1
                else:
                    cell = self.maze[i][j + 2]
                    for k in range(1, self.cols, 2):
                        if self.maze[i][k] == cell:
                            self.maze[i][k] = self.maze[i][j]

            if i == self.rows - 2:
                break

            for j in range(1, self.cols, 2):
                self.maze[i + 2][j] = self.maze[i][j]
                if getrandbits(1):
                    count = 0
                    cell = self.maze[i][j]
                    for k in range(1, self.cols, 2):
                        if (
                            self.maze[i][k] == cell and
                            self.maze[i + 1][k] == 0
                        ):
                            count += 1
                    if count > 1:
                        self.maze[i + 1][j] = 1
                        self.maze[i + 2][j] = index
                        index += 1

        for i in range(1, self.cols - 2, 2):
            if (
                self.maze[self.rows - 2][i] !=
                self.maze[self.rows - 2][i + 2]
            ):
                self.maze[self.rows - 2][i + 1] = 0
                cell = self.maze[self.rows - 2][i + 2]
                for j in range(1, self.cols, 2):
                    if self.maze[self.rows - 2][j] == cell:
                        self.maze[self.rows - 2][j] = \
                            self.maze[self.rows - 2][i]

        for i in range(1, self.rows, 2):
            for j in range(1, self.cols, 2):
                self.maze[i][j] = 0

    def solve(self) -> None:
        """Решение лабиринта"""
        start = [1, 1]
        end = [self.rows - 2, self.cols - 2]

        def get_distance(first: tuple, second: tuple) -> int:
            """Вычисляет кратчайшее расстояние между двумя точками"""
            return (
                abs(first[0] - second[0]) +
                abs(first[1] - second[1])
            ) // 2

        def find_element_in_matrix(matrix: list, element: int) -> list|None:
            """Ищет первую позицию элемента в матрице"""
            for i, row in enumerate(matrix):
                for j, cell in enumerate(row):
                    if cell == element:
                        return [i, j]
            return None

        def find_way(maze: list, position: tuple) -> None:
            """Рекурсивный поиск пути из данной точки"""
            x, y = position #pylint: disable=C0103
            maze[x][y][1] = 1
            ways = []

            def try_move(move_x: int, move_y: int) -> None:
                """Попытка сделать шаг"""
                wall_x = x + move_x
                wall_y = y + move_y
                new_x = x + move_x * 2
                new_y = y + move_y * 2
                if (
                    maze[wall_x][wall_y] != 1 and
                    maze[new_x][new_y][1] != 1
                ):
                    maze[new_x][new_y] = [
                        get_distance((new_x, new_y), end),
                        0,
                        maze[x][y][2] + [[new_x, new_y]]
                    ]
                    ways.append(maze[new_x][new_y])

            try_move(0, 1)
            try_move(-1, 0)
            try_move(1, 0)
            try_move(0, -1)

            shortest_ways = list(filter(lambda x: not x[1], ways))
            shortest_ways.sort(key=lambda x: x[0])
            if any(sublist[:2] == [0, 0] for sublist in shortest_ways):
                return
            if shortest_ways:
                new_start = find_element_in_matrix(maze, shortest_ways[0])
                find_way(maze, new_start)
            else:
                new_start = [1, 1]
                for i in range(1, self.rows, 2):
                    for j in range(1, self.cols, 2):
                        if maze[i][j][0] != 0 and maze[i][j][1] != 1:
                            if (
                                maze[i][j][0] <
                                maze[new_start[0]][new_start[1]][0]
                            ):
                                new_start = [i, j]
                find_way(maze, new_start)

        solving_maze = [[i for i in row] for row in self.maze] #pylint: disable=R1721
        for i in range(1, self.rows, 2):
            for j in range(1, self.cols, 2):
                solving_maze[i][j] = [0, 0, 0]
        solving_maze[start[0]][start[1]] = \
            [get_distance(start, end), 0, [list(start)]]
        find_way(solving_maze, start)
        self.way = solving_maze[end[0]][end[1]][2]

    @staticmethod
    def load_maze(filename: str) -> "Maze":
        """Загружает лабиринт из текстового файла"""
        with open(filename, 'r', encoding='utf-8') as file:
            maze_data = [
                list(map(int, line.strip())) for line in file.readlines()
            ]
            maze = Maze(len(maze_data), len(maze_data[0]))
            maze.maze = maze_data
            return maze

    def save_maze(self, filename: str) -> None:
        """Выгружает лабиринт в текстовый файл"""
        with open(filename, 'w', encoding='utf-8') as file:
            for row in self.maze:
                file.write(''.join(map(str, row)) + '\n')

    def create_image(self, solved: bool = False) -> Image.Image:
        """Генерирует изображение лабиринта"""
        maze = self.maze
        cell_size = 10
        wall_color = (0, 0, 0)
        passage_color = (255, 255, 255)
        way_color = (205, 0, 255)

        width = self.cols * cell_size
        height = self.rows * cell_size
        img = Image.new('RGB', (width, height), passage_color)
        draw = ImageDraw.Draw(img)

        def draw_cell(i: int, j: int, color: tuple) -> None:
            """Закрашивает ячейку"""
            draw.rectangle(
                [
                    (
                        j * cell_size,
                        i * cell_size
                    ),
                    (
                        (j + 1) * cell_size,
                        (i + 1) * cell_size
                    )
                ],
                color
            )

        for i in range(self.rows):
            for j in range(self.cols):
                if (
                    maze[i][j] == 1 and
                    not (j == 1 and i == 0) and
                    not (
                        j == self.cols - 2 and
                        i == self.rows - 1
                    )
                ):
                    draw_cell(i, j, wall_color)

        if solved:
            draw_cell(0, 1, way_color)
            draw_cell(self.rows - 1, self.cols - 2, way_color)
            for i, j in self.way:
                draw_cell(i, j, way_color)
                if (
                    [i + 2, j] in self.way and
                    maze[i + 1][j] == 0
                ):
                    draw_cell(i + 1, j, way_color)
                if (
                    [i, j + 2] in self.way and
                    maze[i][j + 1] == 0
                ):
                    draw_cell(i, j + 1, way_color)

        return img
