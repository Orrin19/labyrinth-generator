"""Консольное приложения для создания и решения лабиринтов"""


import argparse
from PIL import Image
from maze import Maze


def configure_parser() -> None:
    """Создание и настройка объекта парсера"""
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-r',
        '--rows',
        type = int,
        dest = 'rows',
        help = 'высота лабиринта со стенками (нечётное число, > 3)'
    )
    parser.add_argument(
        '-c',
        '--cols',
        type = int,
        dest = 'cols',
        help = 'ширина лабиринта со стенками (нечётное число, > 3)'
    )
    parser.add_argument(
        '-imp',
        '--import',
        type = str,
        dest = 'import_maze',
        help = 'название файла с текстовым представлением лабиринта'
    )
    parser.add_argument(
        '-s',
        '--show',
        type = bool,
        dest = 'show',
        action = argparse.BooleanOptionalAction,
        help = 'флаг демонстрации результата'
    )
    parser.add_argument(
        '-t',
        '--text',
        type = bool,
        dest = 'text',
        action = argparse.BooleanOptionalAction,
        help = 'флаг создания текстового файла'
    )
    parser.add_argument(
        '-i',
        '--image',
        type = bool,
        dest = 'image',
        action = argparse.BooleanOptionalAction,
        help = 'флаг создания изображения'
    )
    parser.add_argument(
        '-n',
        '--name',
        type = str,
        dest = 'name',
        help = 'имя лабиринта (файла выхода)'
    )
    return parser


def show_image(maze: Maze) -> None:
    """Показывает изображение лабиринта и его решение"""
    maze_image = maze.create_image()
    solved_image = maze.create_image(solved = True)
    width = maze_image.width
    height = maze_image.height
    new_image = Image.new("RGB", (width * 2 + 10, height))
    new_image.paste(maze_image, (0, 0))
    new_image.paste(solved_image, (width + 10, 0))
    new_image.show()


def main():
    """Основная функция приложения"""
    parser = configure_parser()
    args = parser.parse_args()
    maze = None

    if args.import_maze:
        maze = Maze.load_maze(args.import_maze)
        maze.solve()
    else:
        if (
            args.rows is None or
            args.cols is None or
            args.rows < 4 or
            args.cols < 4
        ):
            parser.print_help()
            return
        if args.rows % 2 == 0 or args.cols % 2 == 0:
            print('Измерения лабиринта должны быть нечётными!')
            return
        if (
            args.rows * args.cols > 14400 or
            args.rows > 201 or
            args.cols > 201
        ):
            print('Лабиринт слишком большой!')
            return
        maze = Maze(args.rows, args.cols)
        maze.solve()

    if not args.name:
        args.name = 'test'
    if args.text:
        maze.save_maze(args.name + '.txt')
        print('Лабиринт сохранен в текстовом файле', args.name + '.txt')
    if args.image:
        maze.create_image().save(args.name + '.png')
        print('Изображение лабиринта сохранено в файле', args.name + '.png')
    if args.show:
        show_image(maze)


if __name__ == "__main__":
    main()
