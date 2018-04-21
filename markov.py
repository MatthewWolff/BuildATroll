#!/bin/python
import json
import re
from math import isnan
from os import path

import markovify
import numpy as np
import pandas as pd


def get_model(corpus):
    file_id = corpus.split("_")[0]
    model_path = file_id + "_markov_model.json"
    if not path.exists(model_path):  # if model doesn't exist, make it
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


def clean(string):
    tw = string
    tw = re.sub("(https?://.*)|(www\..*)|(t\.co.*)|(amzn\.to.*)( |$)|", "", tw)  # remove links + newlines
    tw = re.sub("\n", "", tw)
    return tw


def get_corpus():
    bot_corpus = "bot_corpus.txt"
    if not path.exists(bot_corpus):  # if corpus doesn't exist, make it
        # russian trolls, with an ID set for constant time user access
        users = pd.read_csv("users.csv")
        users.set_index(keys="id", inplace=True, drop=False)
        tweets = pd.read_csv("tweets.csv")

        # sort users by their ratio of favorites per follower
        users["favorites_per_follower"] = users.apply(lambda row: row.favourites_count / (row.followers_count + 1),
                                                      axis=1)
        users.sort_values(by=["favorites_per_follower"], ascending=False, inplace=True)

        # create a column of empty lists to collect tweets in, then make a list of dictionaries from users
        users["tweets"] = np.empty((len(users), 0)).tolist()
        curated_tweets = pd.Series(users.tweets.values, index=users.id).to_dict()

        for index, tweet in tweets.iterrows():
            if isnan(tweet.user_id) or "RT" in str(tweet.text):  # ignore unidentified tweets and re-tweets
                continue
            # curate list of tweets and their # of favorites
            curated_tweets[tweet.user_id].append([str(tweet.text), tweet.favorite_count if not "nan" else 0])
        # sort the list by # of favorites then combine its contents into a corpus, taking care to clean the text
        corpus = " ".join(" ".join(clean(z[0]) for z in sorted(x, key=lambda y: y[1])) for x in curated_tweets.values())
        with open(bot_corpus, "wb") as o:
            o.write(corpus)
    else:
        # Get raw text as string.
        with open(bot_corpus) as f:
            corpus = f.read()
    return bot_corpus  # lol return the file name for now


if __name__ == "__main__":

    corpus_name = get_corpus()
    markov_model = get_model(corpus_name)

    for i in range(10):
        print "The Russians say:", markov_model.make_short_sentence(280)  # characters
