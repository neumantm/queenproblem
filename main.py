#!/usr/bin/env python3

from ast import arg
import queue
from typing import List, Dict, Any

from dataclasses import dataclass, field
from copy import deepcopy
from json import dump, load
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

    def to_dict(self) -> Dict[str, Any]:
        return {
            'x': self.x,
            'y': self.y,
            'queen': self.queen,
            'blocked_by_queen': self.blocked_by_queen
        }

def cell_from_dict(cell_dict: Dict[str, any]) -> Cell:
    return Cell(cell_dict['x'], cell_dict['y'], cell_dict['queen'], cell_dict['blocked_by_queen'])

class Field:
    def __init__(self, from_dict=None) -> None:
        self.rows: List[List[Cell]]

        if from_dict is not None:
            self.rows = [[cell_from_dict(cell_dict) for cell_dict in row] for row in from_dict['rows']]
        else:
            self.rows = list()
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

    def to_dict(self) -> Dict[str, Any]:
        return {
            'rows': [[cell.to_dict() for cell in row] for row in self.rows]
        }

    def __eq__(self, __o: object) -> bool:
        if type(__o) != Field:
            return False
        return self.rows == __o.rows

def try_to_solve(field: Field, queens_remaining: int, solutions: List[Field], output_progress = False):
    if queens_remaining == 0:
        if field not in solutions:
            solutions.append(field)
    free_cells = field.get_free_cells()
    for i,cell in enumerate(free_cells):
        if output_progress:
            print(f"{i}/{len(free_cells)}")
        field_dash = deepcopy(field)
        field_dash.set_queen(cell.x, cell.y)
        try_to_solve(field_dash, queens_remaining -1, solutions)
    return solutions

def bruteForce(solution_file: str):
    f = Field()
    solutions: List[Field] = []
    try_to_solve(f, 8, solutions, True)
    print(f"Found {len(solutions)} solutions.")
    solutions_jsonizable =  [solution.to_dict() for solution in solutions]
    print(solutions_jsonizable)
    with open(solution_file, 'w') as f:
        dump(solutions_jsonizable, f)

def analyze(solution_file: str):
    solutions_fromjson = None
    with open(solution_file, 'r') as f:
        solutions_fromjson = load(f)
    if solutions_fromjson == None:
        raise Exception("Could not read solution file!")
    solutions = [Field(field_dict) for field_dict in solutions_fromjson]
    print(f"Found {len(solutions)} different solutions.")


def main():
    if len(argv) != 3:
        raise Exception("Please supply operation and path for solution file. Operations are solve and analyze.")

    solution_file = argv[2]

    if argv[1] == "solve":
        with open(solution_file, 'w') as f:
            if not f.writable():
                raise Exception("Solution file not writeable.")
        bruteForce(solution_file)
    elif argv[1] == "analyze":
        analyze(solution_file)
    else:
        raise Exception("Possible operations are sovle and analyze.")




if __name__ == "__main__":
    main()
