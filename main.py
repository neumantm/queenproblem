#!/usr/bin/env python3

from ast import arg
import queue
from typing import List

from dataclasses import dataclass, field
from copy import deepcopy
from json import dump
from sys import argv

@dataclass
class Cell:
    x: int #Cell number in row
    y: int #Row number
    queen: bool = field(default=False)
    blocked_by_queen: bool = field(default=False)

    def symbol(self) -> str:
        if self.queen:
            return "o"
        elif self.blocked_by_queen:
            return "x"
        else:
            return " "

    def is_free(self) -> bool:
        return not self.queen and not self.blocked_by_queen

    def set_blocked_by_queen(self) -> None:
        if self.queen:
            raise Exception("Killing queen on: ", self)
        self.blocked_by_queen = True

    def set_queen(self) -> None:
        if not self.is_free():
            raise Exception("Failed to set queen on: ", self)
        self.queen = True

class Field:
    def __init__(self) -> None:
        self.rows: List[List[Cell]] = list()
        for i in range(0, 8):
            self.rows.append(list())
            for j in range(0, 8):
                self.rows[i].append(Cell(j, i))

    def __repr__(self) -> str:
        return repr(self.rows)

    def draw(self) -> None:
        print("---------------------------------")
        for row in self.rows:
            print("| ", end="")
            for cell in row:
                print(cell.symbol(), end=" | ")
            print()
            print("---------------------------------")

    def g_c(self, x: int, y: int) -> Cell:
        return self.rows[y][x]

    def set_queen(self, x: int, y: int) -> None:
        self.g_c(x,y).set_queen()
        for x_dash in range(0,8):
            if x_dash == x:
                continue
            self.__set_blocked_by_queen(x_dash, y)
        for y_dash in range(0,8):
            if y_dash == y:
                continue
            self.__set_blocked_by_queen(x, y_dash)
        for i in range(-8,8):
            if i == 0:
                continue
            x_dash = (x + i)
            y_dash = (y + i)
            if x_dash < 0 or x_dash > 7 or y_dash < 0 or y_dash > 7:
                continue
            self.__set_blocked_by_queen(x_dash, y_dash)
        for i in range(-8,8):
            if i == 0:
                continue
            x_dash = (x + i)
            y_dash = (y - i)
            if x_dash < 0 or x_dash > 7 or y_dash < 0 or y_dash > 7:
                continue
            self.__set_blocked_by_queen(x_dash, y_dash)

    def __set_blocked_by_queen(self, x: int, y: int) -> None:
        self.g_c(x,y).set_blocked_by_queen()

    def get_free_cells(self) -> List[Cell]:
        result = []
        for row in self.rows:
            result += [cell for cell in row if cell.is_free()]
        return result

def try_to_solve(field: Field, queens_remaining: int, output_progress = False) -> List[Field]:
    solutions = []
    if queens_remaining == 0:
        solutions.append(field)
    free_cells = field.get_free_cells()
    for i,cell in enumerate(free_cells):
        if output_progress:
            print(f"{i}/{len(free_cells)}")
        field_dash = deepcopy(field)
        field_dash.set_queen(cell.x, cell.y)
        try_to_solve(field_dash, queens_remaining -1)
    return solutions

def main():
    if len(argv) != 2:
        raise Exception("Please supply path for solution file")
    f = Field()
    solutions = try_to_solve(f, 8, True)
    print(f"Found {len(solutions)} solutions.")
    with open(argv[1], 'w') as f:
        dump(solutions, f)


if __name__ == "__main__":
    main()
