import csv
from io import TextIOWrapper
import multiprocessing
from time import time
from typing import List, Tuple

import modules.board_devel as board_module


def load_data(file_path: str = 'tests/data/perft.csv') -> List[
        Tuple[str, int, int, int, int, int, int]]:
    with open(file_path, 'r') as f:
        reader = csv.reader(f)
        _ = next(reader) # skips the comment line
        test_data = [tuple((int(val) if i != 0 else val for i, val in enumerate(row))) for row in reader]
    return test_data


def test_perft(data: Tuple[str, int, int, int, int, int, int], 
               max_depth: int, verbose: bool = False) -> Tuple[List[Tuple[bool, float, int]], int]:
    fen = data[0]
    board = board_module.Board(fen)
    results = []
    if verbose:
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
            if verbose:
                print('.', end='')
        else:
            if verbose:
                print(f'F\t{depth-1}/{max_depth}\t{round(time() - start_time_total, 2)} s\n\texpected {data[depth]}, got {res} (delta: {"+" if res-data[depth]>0 else ""}{res-data[depth]})\n')
            return results, depth-1
    if verbose:
        print(f'\t{max_depth}/{max_depth}\t{round(time() - start_time_total, 2)} s')
    return results, max_depth


def test_all(test_data: List[Tuple[str, int, int, int, int, int, int]], 
             max_depth: int, index: int, verbose: bool = False) -> str:
    
    file = open(f'tests/results/perft_10-d{max_depth}-99-{index}.csv', 'w')
    failed_fens = []
    start_time = time()
    overall_passed = 0
    csv_str = ''
    for test in test_data:
        results, tests_passed = test_perft(test, max_depth)
        overall_passed += tests_passed
        csv_str += f'{test[0]},'
        for passed, time_total, nodes in results:
            # file_handle.write(f'{"OK" if passed else "FAILED"},{time_total},{nodes},')
            csv_str += f'{"OK" if passed else "FAILED"},{time_total},{nodes},'
            if not passed:
                failed_fens.append(test[0])
        # file_handle.write('\n')
        csv_str += '\n'
    if verbose:
        print(f'\nPassed: {overall_passed}/{max_depth*len(test_data)}\tTime: {round(time() - start_time, 2)} s')
        print(failed_fens)
    
    file.write(csv_str)
    file.close()


if __name__ == '__main__':
    FILE='perft_10'
    MAXDEPTH=5
    VERSION=99
    f_time = open(f'tests/results/lasttime_10.txt', 'w')
    start_time = time()
    # f1 = open(f'tests/results/{FILE}-d{MAXDEPTH}-{VERSION}-1.csv', 'w')
    # f2 = open(f'tests/results/{FILE}-d{MAXDEPTH}-{VERSION}-2.csv', 'w')
    # f3 = open(f'tests/results/{FILE}-d{MAXDEPTH}-{VERSION}-3.csv', 'w')
    # f4 = open(f'tests/results/{FILE}-d{MAXDEPTH}-{VERSION}-4.csv', 'w')

    test_data = load_data(f'tests/data/{FILE}.csv')
    divlen = len(test_data) // 4

    # p1 = multiprocessing.Process(target=test_all, args=(test_data[:divlen], MAXDEPTH, 1,))
    # p2 = multiprocessing.Process(target=test_all, args=(test_data[divlen:2*divlen], MAXDEPTH, 2,))
    # p3 = multiprocessing.Process(target=test_all, args=(test_data[2*divlen:3*divlen], MAXDEPTH, 3,))
    # p4 = multiprocessing.Process(target=test_all, args=(test_data[3*divlen:], MAXDEPTH, 4,))
    list_1 = [test_data[6]]
    list_2 = [test_data[5], test_data[2]]
    list_3 = [test_data[0], test_data[7], test_data[9]]
    list_4 = [test_data[3], test_data[4], test_data[8], test_data[1]]

    p1 = multiprocessing.Process(target=test_all, args=(list_1, MAXDEPTH, 1,))
    p2 = multiprocessing.Process(target=test_all, args=(list_2, MAXDEPTH, 2,))
    p3 = multiprocessing.Process(target=test_all, args=(list_3, MAXDEPTH, 3,))
    p4 = multiprocessing.Process(target=test_all, args=(list_4, MAXDEPTH, 4,))


    p1.start()
    p2.start()
    p3.start()
    p4.start()

    p1.join()
    p2.join()
    p3.join()
    p4.join()
    
    f_time.write(str(time() - start_time))
    f_time.close()
    
    # with open(f'tests/results/{FILE}-d{MAXDEPTH}-{VERSION}.csv', 'w') as f:
    #     test_all(test_data, MAXDEPTH, f)
    # f1.close()
    # f2.close()
    # f3.close()
    # f4.close()
