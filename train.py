import argparse
import glob
import json

import sys

import pathlib

import os
import re


def parseargs():
    # Парсим аргументы
    parser = argparse.ArgumentParser(description="Tool for generating model")
    parser.add_argument('--input-dir', default=None,
                        help='Path to directory with files, if not provided use stdin instead', required=False)
    parser.add_argument('--model', default='model.json', help='Name of model file', required=False)
    parser.add_argument('--lc', help='Replace with lowercase', required=False, action='store_true')
    return parser.parse_args()


def prepare_text(text):
    # Регулярочки не алфавита
    nonalph_regex = re.compile('\W')
    digit_regex = re.compile('\d')
    text = nonalph_regex.sub(' ', text)
    text = digit_regex.sub('', text)
    # Убираем лишние пробелы
    text = text.strip()
    # Делим на массив
    words = text.split()
    return words


def add_to_model(model, word1, word2):
    count = model.setdefault(word1, {}).setdefault(word2, 0)
    model[word1][word2] = count + 1


def write_model_to_file(model, out_file):
    # Пишем модель в файл создавая недостающие папки(Сохраняем в JSON формате)
    odir = os.path.dirname(out_file)
    pathlib.Path(odir).mkdir(parents=True, exist_ok=True)
    with open(out_file, 'w', encoding='utf-8') as ofile:
        json.dump(model, ofile, ensure_ascii=False)

def train(dir=None, out_file='model.json', to_lower=False):
    # Модель
    words_model = {}

    # Чтобы не копипастить
    if not dir:
        input_files = [None]
    else:
        # Берём все .txt в директории, если нет, то вернёт пустой массив
        input_files = glob.glob('{}/*.txt'.format(dir))

    if not input_files:
        print('В указанной директории отсутствуют файлы с текстами')
        sys.exit(0)

    for file_name in input_files:
        # Читаем из файлов или stdin если не задано
        if not file_name:
            file = sys.stdin
        else:
            file = open(file_name, encoding='utf-8')

        # Последнее слово пердыдущей строки
        last_word_in_line = None
        for line in file:
            # В нижний регистр если надо
            if to_lower:
                line = line.lower()
            # Убираем мусор
            words_in_line = prepare_text(line)

            # Если пустая строка, то ничего не делаем
            if not words_in_line:
                continue
            # Не забываем про последнее слово того что было до этой строки
            if last_word_in_line:
                add_to_model(words_model, last_word_in_line, words_in_line[0])

            # Количество слов в строке
            words_count = len(words_in_line)

            # Обновляем модель
            for i in range(words_count - 1):
                add_to_model(words_model, words_in_line[i], words_in_line[i + 1])

            # Сохраняем последнее слово
            last_word_in_line = words_in_line[-1]

    write_model_to_file(words_model, out_file)


if __name__ == '__main__':
    args = parseargs()
    dir = args.input_dir
    to_lower = args.lc
    out_file = args.model

    train(dir=dir, out_file=out_file, to_lower=to_lower)


