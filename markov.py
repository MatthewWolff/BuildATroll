#!/bin/python
import json
from os import path

import markovify
import numpy as np
import pandas as pd


def get_model(corpus):
    file_id = corpus.split("_")[0]
    model_path = file_id + "_markov_model.json"
    if not path.exists(model_path):
        # Get raw text as string.
        with open(corpus) as f:
            text = f.read()

        # Build the model.
        text_model = markovify.Text(text)
        model_json = text_model.to_json()
        with open(model_path, "wb") as o:
            json.dump(model_json, o)
    else:
        with open(model_path, "rb") as f:
            text_model = markovify.Text.from_json(json.load(f))
    return text_model


def get_corpus():
    users = pd.read_csv("users.csv")
    users.set_index("id")
    tweets = pd.read_csv("tweets.csv")

    users["favorites_per_follower"] = users.apply(lambda row: row.favourites_count / (row.followers_count + 1), axis=1)
    users.sort_values(by=["favorites_per_follower"], ascending=False, inplace=True)
    users["tweets"] = np.empty((len(users), 0)).tolist()  # add an empty list to add tweets to
    for tweet in tweets:
        user = users.query("id == " + tweet.user_id)
        user.tweets.append([tweet.text, tweet.favorite_count])
        print user


if __name__ == "__main__":
    get_corpus()

    # # Print five randomly-generated sentences
    # corpus_name = "realdonaldtrump_readable_corpus.txt"
    # markov_model = get_model(corpus_name)
    #
    # # Print three randomly-generated sentences of no more than 140 characters
    # for i in range(3):
    #     print(markov_model.make_short_sentence(140))
