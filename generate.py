import argparse
import json
import random
import os
import numpy as np
import pathlib


def parseargs():
    # Парсим аргументы
    parser = argparse.ArgumentParser(description="Tool for generating Markov chain")
    parser.add_argument('--model', help='Name of model file', required=True)
    parser.add_argument('--seed', default=None, help='Initial word, random if not in list on not set', required=False)
    parser.add_argument('--length', help='Length of chain', required=True)
    parser.add_argument('--output', default=None, help='Output file, stdout if not set', required=False)
    return parser.parse_args()


def prepare_model(model):
    # Нормируем частоты
    for word, value in model.items():
        count_of_next_words = np.sum(list(value.values()))
        for word_next, count in value.items():
            model[word][word_next] = count / count_of_next_words


def get_first_word(model, seed=None):
    if seed:
        # Попадаем сюда когда передано зерно
        return seed
    else:
        # Вызывается если зерно не задано, или нет в списке слов, или нет следующего слова
        return random.choice(list(model.keys()))


def get_next_word(model, cur_word):
    if not cur_word in model:
        return get_first_word(model)
    else:
        return np.random.choice(list(model[cur_word].keys()), p=list(model[cur_word].values()))


def generate_chain(model, seed, chain_length):
    # Цепь
    chain = []

    # Добавляем первый элемент
    chain.append(get_first_word(model, seed))

    # Последнее слово
    cur_word = chain[0]

    # Строим цепочку пока она короче чем надо
    while len(chain) < chain_length:
        # Выбираем следующее слово
        word = get_next_word(model, cur_word)
        chain.append(word)
        cur_word = word

    return chain


def write_chain(chain, out_file):
    if out_file:
        # Пишем цепь в файл, создавая недостающие директории
        odir = os.path.dirname(out_file)
        pathlib.Path(odir).mkdir(parents=True, exist_ok=True)
        with open(out_file, 'w', encoding='utf-8') as ofile:
            ofile.write(' '.join(chain))
    else:
        # Выводим в stdout
        print(' '.join(chain))


def generate_from_model(model_path, chain_length, seed=None, out_file=None):
    # Загружаем модель из JSON
    model = json.load(open(model_path, encoding='utf-8'))

    prepare_model(model)

    # Если нет зерна в модели, то делаем вид что нет зерна
    if not seed in model:
        seed = None

    chain = generate_chain(model, seed, chain_length)

    write_chain(chain, out_file)

if __name__ == '__main__':
    args = parseargs()
    model_path = args.model
    seed = args.seed
    chain_length = int(args.length)
    out_file = args.output

    generate_from_model(model_path, chain_length, seed=seed, out_file=out_file)


