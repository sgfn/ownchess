import csv
from math import log10
from time import time
from typing import List, Tuple

import modules.board_devel as board_module


def load_data(file_path: str) -> List[Tuple[str, int, int, int, int, int, int]]:
    with open(file_path, 'r') as f:
        reader = csv.reader(f)
        _ = next(reader) # skips the comment line
        test_data = [tuple((int(val) if i != 0 else val for i, val in enumerate(row))) for row in reader]
    return test_data


def test_perft(data: Tuple[str, int, int, int, int, int, int], 
               max_depth: int) -> Tuple[List[Tuple[bool, float, int]], int]:
    fen = data[0]
    board = board_module.Board(fen)
    results = []

    print(f'{fen[:10]}[...]{fen[-10:]}', end='\t')
    start_time_total = time()
    for depth in range(1, max_depth+1):
        # Run and time the perft for current depth
        start_time = time()
        res = board.perft(depth)
        time_total = round(time() - start_time, 2)
        # Store the results
        # knps = int(res//(time_total*1000)) if time_total != 0 else 100
        passed = (res == data[depth])
        results.append((passed, time_total, res))

        if passed:
            print('.', end='')
        else:
            print(f'F\t{depth-1}/{max_depth}\t{round(time() - start_time_total, 2)} s\n\texpected {data[depth]}, got {res} (delta: {"+" if res-data[depth]>0 else ""}{res-data[depth]})\n')
            return results, depth-1
    print(f'\t{max_depth}/{max_depth}\t{round(time() - start_time_total, 2)} s')
    return results, max_depth


def test_all(file: str, max_depth: int, version: str = 'devel') -> None:
    test_data = load_data(f'tests/data/{file}.csv')
    print(f"{len(test_data)} tests loaded from file '{file}'")
    print(f"Testing at depth {max_depth} using module board-{version}\n")
    print('No.    FEN                              TESTS   PASSED  TIME')
    with open(f'tests/results/{file}-d{max_depth}-{version}.csv', 'w') as f:
        failed_fens = []
        start_time = time()
        overall_passed = 0
        for index, test in enumerate(test_data):
            print(f'[{" "*(3-int(log10(index+1)))}{index + 1}]', end=' ')
            
            results, tests_passed = test_perft(test, max_depth)
            overall_passed += tests_passed
            for passed, time_total, nodes in results:
                f.write(f'{"OK" if passed else "FAILED"},{time_total},{nodes},')
                if not passed:
                    failed_fens.append(test[0])
            f.write('\n')
        print(f'\n{overall_passed}/{max_depth*len(test_data)} tests passed (time: {round(time() - start_time, 2)} s)')
        # print(failed_fens)


if __name__ == '__main__':
    FILE='perft_micro'
    MAXDEPTH=4
    VERSION='devel'
    test_all(FILE, MAXDEPTH, VERSION)
