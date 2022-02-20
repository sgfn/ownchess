import csv
from io import TextIOWrapper
from time import time
from typing import List, Tuple

import modules.board


def load_data(file_path: str = 'tests/data/perft.csv') -> List[
        Tuple[str, int, int, int, int, int, int]]:
    with open(file_path, 'r') as f:
        reader = csv.reader(f)
        _ = next(reader) # skips the comment line
        test_data = [tuple((int(val) if i != 0 else val for i, val in enumerate(row))) for row in reader]
    return test_data


def test_perft(data: Tuple[str, int, int, int, int, int, int], 
               max_depth: int) -> Tuple[List[Tuple[bool, float, int]], int]:
    fen = data[0]
    board = modules.board.Board(fen)
    results = []

    print(f'{fen[:10]}[...]{fen[-10:]}', end='\t')
    for depth in range(1, max_depth+1):
        # Run and time the perft for current depth
        start_time = time()
        res = board.perft(depth)
        time_total = round(time() - start_time, 2)
        # Store the results
        knps = int(res//(time_total*1000)) if time_total != 0 else 100
        passed = (res == data[depth])
        results.append((passed, time_total, knps))

        if passed:
            print('.', end='')
        else:
            print(f'F\t{depth-1}/{max_depth}\n\texpected {data[depth]}, got {res} (delta: {res-data[depth]})\n')
            return results, depth-1
    print(f'\t{max_depth}/{max_depth}')
    return results, max_depth


def test_all(test_data: List[Tuple[str, int, int, int, int, int, int]], 
             max_depth: int, file_handle: TextIOWrapper) -> None:
    
    start_time = time()
    overall_passed = 0
    for test in test_data:
        results, tests_passed = test_perft(test, max_depth)
        overall_passed += tests_passed
        for passed, time_total, knps in results:
            file_handle.write(f'{"PASSED" if passed else "FAILED"},{time_total},{knps},')
        file_handle.write('\n')
    print(f'\nPassed: {overall_passed}/{max_depth*len(test_data)}\tTime: {round(time() - start_time, 2)} s')


if __name__ == '__main__':
    test_data = load_data('tests/data/perft_10.csv')
    with open('tests/results/perft_10.csv', 'w') as f:
        test_all(test_data, 4, f)