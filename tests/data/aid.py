import csv

if __name__ == '__main__':
    with open('tests/data/perft_failed_d4.csv', 'w') as f:
        counter = 0
        for i in range(1, 4):
            with open(f'tests/results/perft-d4-99-{i}.csv') as read_f:
                reader = csv.reader(read_f)
                _ = next(reader)
                for line in reader:
                    if 'FAILED' in line:
                        counter += 1
                        for string in line:
                            f.write(string)
                            f.write(',')
                        f.write('\n')
        print(counter)