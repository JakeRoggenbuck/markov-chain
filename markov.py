import sqlite3
import json
from tqdm import tqdm
from random import choices
from pprint import pprint


class MakeMarkov:
    def __init__(self):
        self.connection = sqlite3.connect('markov.db')
        self.words = []

    def setup_db(self):
        cur = self.connection.cursor()
        cur.execute("CREATE TABLE words (id INTEGER PRIMARY KEY, word text)")

    def read_file(self):
        """Reads all of the words in the book"""
        with open("./all_stuff.txt", "r") as file:
            text = file.read()
            self.words.extend(text.split())

    def find_unique(self):
        """Adds all unique words to sql db

        Checks if a given word is in the database, if not add it"""
        cur = self.connection.cursor()
        for word in tqdm(self.words):
            cur.execute("SELECT * FROM words WHERE word=?", (word,))
            if cur.fetchone() is None:
                cur.execute("INSERT INTO words (id, word) VALUES (NULL, ?)", (word,))
        self.connection.commit()

    def train(self):
        """Each word is a key, to which there is a value for each next word

        Each word is a key in data and has values that are the next words found
        in the text, along with it's value, a number representing it's occurrences

        {
            'A': {
                'name': 10, 'cat': 2, 'automobile': 1
            },

            'name': {
                'is': 8, 'has': 5, 'it': 1
            },
        }

        """
        data = {}

        cur = self.connection.cursor()
        cur.execute("SELECT * FROM words")
        # Make the initial empty reference
        for word in tqdm(cur.fetchall()):
            data[word[1]] = {}

        # For each word, increment the next fields frequency number
        for word_index in tqdm(range(len(self.words))):
            if word_index == len(self.words) - 1:
                break

            current_word = self.words[word_index]
            next_word = self.words[word_index + 1]

            # Set the value to 1 if it's not there
            if next_word not in data[current_word]:
                data[current_word][next_word] = 1
            # Add one if it exists
            else:
                data[current_word][next_word] += 1

        # Write the chain
        json_object = json.dumps(data, indent=4)
        with open("markov.json", "w") as outfile:
            outfile.write(json_object)

    def print_all(self):
        cur = self.connection.cursor()
        cur.execute("SELECT * FROM words")
        pprint(cur.fetchall())


def generate(start, length):
    """Generate some text using the chain"""
    # Made for easy of use in the api
    if start is None:
        start = "A"

    if length is None:
        length = 100

    # Open the pre built chain
    with open("markov.json", "r") as myfile:
        data = myfile.read()
        obj = json.loads(data)

    word = start
    full = start + " "

    # For each number, get the next words, and use their weights to get the
    # number that comes after, then set that to the new word
    for _ in range(length):
        values = list(obj[word].values())
        word = choices(list(obj[word].keys()), weights=values)[0]
        full += word + " "

    return full


if __name__ == "__main__":
    setup = False
    find_unique_make_sql = False
    train = False

    mark = MakeMarkov()
    if setup:
        mark.setup_db()

    mark.read_file()

    if find_unique_make_sql:
        mark.find_unique()

    if train:
        mark.train()
