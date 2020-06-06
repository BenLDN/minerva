import re
import json
from collections import Counter
from textblob import Word


def read_excluded_words():

    with open('exclude_words.txt', 'r') as exc_file:
        exclude_words = json.load(exc_file)

    return exclude_words


def clean_list(raw_list):

    def clean_string(text):
        return re.sub('[^0-9a-zA-Z]+', ' ', text.lower()).strip()

    return [clean_string(title) for title in raw_list]


def word_freq_from_list(title_list):
    title_words = ' '.join(title_list).split()
    title_words_lemmatised = []

    for title_word in title_words:
        title_words_lemmatised.append(Word(title_word).lemmatize())
    return Counter(title_words_lemmatised)


def word_freq_cleaner(raw_freq, exclude_words):
    word_freq_cleaned = {word: freq for word, freq in raw_freq.items()
                         if len(word) >= 3 and
                         word not in exclude_words}

    return word_freq_cleaned


def calculate_freq_percentage(freq_abs):
    total_words = sum(freq_abs.values())
    return {word: (freq / total_words) for word, freq in freq_abs.items()}


def get_top_words(freq_pctg, word_count):
    return Counter(freq_pctg).most_common()[: word_count]


def add_rank(tuple_list):
    list_with_rank = []

    for i, tup in enumerate(tuple_list):
        list_with_rank.append((tup[0], tup[1], i+1))

    return list_with_rank


def words_tuple_list_from_titles(raw_title_list, word_count):
    title_list = clean_list(raw_title_list)
    exclude_words = read_excluded_words()
    word_freq_abs = word_freq_from_list(title_list)
    word_freq_abs_clean = word_freq_cleaner(word_freq_abs, exclude_words)
    word_freq_pctg = calculate_freq_percentage(word_freq_abs_clean)
    word_freq_pctg_top = get_top_words(word_freq_pctg, word_count)
    return add_rank(word_freq_pctg_top)
