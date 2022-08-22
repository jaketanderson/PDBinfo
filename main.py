import tweepy
import time
from datetime import datetime, timezone
import subprocess as sp
import calcs
import os

client = tweepy.Client(
    bearer_token=os.environ["BEARER_TOKEN"],
    consumer_key=os.environ["CONSUMER_KEY"],
    consumer_secret=os.environ["CONSUMER_SECRET"],
    access_token=os.environ["ACCESS_TOKEN"],
    access_token_secret=os.environ["ACCESS_TOKEN_SECRET"],
)

pdbinfo_id = client.get_user(username="pdbinfo", user_auth=True).data.id

stream_rule = tweepy.StreamRule(
    value=f"(has:mentions @pdbinfo) OR (to:{int(pdbinfo_id)})"
)

path = "/media/speedy/"


def fetch_pdb(original_tweet, entry):

    print("Fetching PDB ", entry, " from ", path)

    for char in entry:
        if not (char.isalpha() or char.isnumeric()):
            client.create_tweet(
                in_reply_to_tweet_id=original_tweet.id,
                text=f"The given four-digit PDB contained non-alphanumeric characters. Ensure you are using standard English unicode/ascii/utf-8 numbers and letters.",
            )
            return False

    try:
        sp.run(f"bash getPDB.sh -o {path} -i {entry}", shell=True)

    except:
        client.create_tweet(
            in_reply_to_tweet_id=original_tweet.id,
            text=f"I couldn't download PDB with ID {entry}. If you don't know a valid PDB ID, try using -random in your tweet instead of -id [PDB ID].",
        )
        return False

    return True


class Printer(tweepy.StreamingClient):
    def on_tweet(self, tweet):

        print("-" * 50)
        print(tweet.text)

        text = tweet.text.lower()

        try:
            text.remove("@pdbinfo")
        except:
            pass

        if "-id " in text:
            start = text.find("-id ") + len("-id ")

            try:
                while not (text[start].isalpha() or text[start].isnumeric()):
                    start += 1
                entry = text[start : start + 4].upper()
                print(entry)

            except:
                client.create_tweet(
                    in_reply_to_tweet_id=original_tweet.id,
                    text=f"Error parsing PDB ID.",
                )
                pass

            fetch_pdb(tweet, entry)

            if text.find("-noprot") == -1:

                calcs.protonate(client, tweet, entry)

            calcs.get_sasa(client, tweet, entry)


printer = Printer(os.environ["BEARER_TOKEN"])
printer.add_rules(stream_rule)
printer.filter()
