import sys
from io import open

if __name__ == '__main__':
    if sys.argv.__len__() is not 5:
        print("Syntax: python3 xxx.py [file_1] [file_2] [file_result] [split_char]")
        sys.exit(1)

    with open(sys.argv[3], 'w', encoding='utf-8') as out_txt:
        with open(sys.argv[1], 'r', encoding='utf-8') as file1, open(sys.argv[2], 'r', encoding='utf-8') as file2:
            for x, y in zip(file1, file2):
                xxx = x.replace("\n", "") + sys.argv[4] + y.replace("\n", "")
                out_txt.write("\n" + xxx)
