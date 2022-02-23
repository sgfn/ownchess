import csv


def merge_files(filename: str):
    with open(f'tests/results/{filename}.csv', 'w') as write_f:
        for i in range(1, 5):
            with open(f'tests/results/{filename}-{i}.csv') as read_f:
                reader = csv.reader(read_f)
                for line in reader:
                    for index, item in enumerate(line):
                        if index == len(line)-1:
                            write_f.write(item.rstrip(','))
                        else:
                            write_f.write(item)
                            write_f.write(',')
                    write_f.write('\n')


def get_failed(filename: str):
    with open(f'tests/data/failed_{filename}.csv', 'w') as write_f:
        counter = 0
        with open(f'tests/results/{filename}.csv') as read_f:
            reader = csv.reader(read_f)
            for line in reader:
                if 'FAILED' in line:
                    counter += 1
                    write_f.write(line[0])
                    write_f.write('\n')
    print(f'Found {counter} failed tests')


def get_data_of(filename: str):
    with open(f'tests/data/failed_{filename}.csv') as failed_read_f:
        filename_2 = 'perft_full' if 'full' in filename else 'perft_micro'
        with open(f'tests/data/{filename_2}.csv') as read_f:
            reader_1 = csv.reader(failed_read_f)
            reader_2 = csv.reader(read_f)
            data = []
            for line in reader_2:
                data.append(line)
            with open(f'tests/data/fixed_failed_{filename}.csv', 'w') as write_f:
                for line in reader_1:
                    for data_row in data:
                        if line[0] == data_row[0]:
                            print('found one')
                            for index, item in enumerate(data_row):
                                if index == len(data_row) - 1:
                                    write_f.write(item.rstrip(','))
                                else:
                                    write_f.write(item)
                                    write_f.write(',')
                            write_f.write('\n')


if __name__ == '__main__':
    FILENAME = 'perft_full-d4-devel'
    get_data_of(FILENAME)
