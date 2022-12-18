#!/usr/bin/python3
import asyncio
import re
import sys
from pathlib import Path

from colorama import Fore, Style, init

init(autoreset=True)

DATE = r'[0-3][0-9]-[0,1][0-9]-[2][0][2][0-5] [0-2][0-9]:[0-5][0-9]:[0-5][0-9]'

URI = r'\b[a-z, A-Z]:\\[\w,\\,.]*\b|./[\w, /, .]*\b'

REGEX = DATE + '|' + URI


class Reader:
    def __init__(self, file: str) -> None:
        self.file = file

    async def read_line(self: 'Reader'):
        with open(self.file) as f:
            for line in f.readlines():
                pure_line = re.sub(REGEX, '', line)
                yield line, pure_line


def recive_files() -> list[str] | None:
    files = sys.argv[1:]

    for file in files:
        if not Path(file).exists():
            sys.stdout.write(f'File `{file}` not found.\n')
            sys.exit()

    if len(files) < 2:
        sys.stdout.write('There is nothing to compare.\n')
        sys.exit()

    return files


def compare_strings(string_1, string_2) -> tuple[list[str], list[str]]:
    strings_1 = []
    strings_2 = []
    flag = True
    pivot = 0
    for i in range(min(len(string_1), len(string_2))):
        if string_1[i] != string_2[i]:
            if flag:
                strings_1.append(string_1[pivot:i])
                strings_2.append(string_2[pivot:i])
                flag = False
                pivot = i
        else:
            if not flag:
                strings_1.append(string_1[pivot:i])
                strings_2.append(string_2[pivot:i])
                flag = True
                pivot = i
    strings_1.append(string_1[pivot:])
    strings_2.append(string_2[pivot:])
    return strings_1, strings_2


def color_out(start: str, strings: list) -> None:
    for string in strings:
        flag = True
        sys.stdout.write(start)
        for pic in string:
            if flag:
                sys.stdout.write(pic)
                flag = False
            else:
                sys.stdout.write(Fore.LIGHTRED_EX + pic)
                flag = True


def diff_out(
    start_dif: int, end_dif: int, strings_1: list[str], strings_2: list[str]
) -> None:
    sys.stdout.write(
        Fore.LIGHTYELLOW_EX + f'Difference from {start_dif} to {end_dif}\n'
    )
    color_out('< ', strings_1)
    sys.stdout.write(Fore.LIGHTYELLOW_EX + '---\n')
    color_out('> ', strings_2)
    sys.stdout.write('\n')


async def amain():
    files = recive_files()

    reader_1 = Reader(files[0]).read_line()
    reader_2 = Reader(files[1]).read_line()
    dif_1 = []
    dif_2 = []
    step = start_dif = 0
    flag = True

    try:
        while True:
            step += 1
            line_1, pure_line_1 = await reader_1.__anext__()
            line_2, pure_line_2 = await reader_2.__anext__()
            if not pure_line_1 == pure_line_2:
                if flag:
                    start_dif = step
                flag = False
                lines_1, lines_2 = compare_strings(line_1, line_2)
                dif_1.append(lines_1)
                dif_2.append(lines_2)
            else:
                if not flag:
                    diff_out(start_dif, step, dif_1, dif_2)
                    dif_1 = []
                    dif_2 = []
                flag = True

    except StopAsyncIteration:
        diff_out(start_dif, step, dif_1, dif_2)

    if not start_dif:
        sys.stdout.write(Fore.LIGHTGREEN_EX + Style.BRIGHT + 'No difference!')

    sys.stdout.write(Fore.LIGHTGREEN_EX + Style.BRIGHT + 'End file\n')


if __name__ == '__main__':
    asyncio.run(amain())
