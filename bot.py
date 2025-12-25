import csv
import tweepy
import os

client = tweepy.Client(
    consumer_key=os.getenv("API_KEY"),
    consumer_secret=os.getenv("API_SECRET"),
    access_token=os.getenv("ACCESS_TOKEN"),
    access_token_secret=os.getenv("ACCESS_TOKEN_SECRET"),
)

def post_from_csv():
    rows = []
    tweet_to_post = None

    with open("tweets.csv", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)
            if row["posted"] == "FALSE" and not tweet_to_post:
                tweet_to_post = row

    if not tweet_to_post:
        print("No tweets left")
        return

    client.create_tweet(text=tweet_to_post["tweet_text"])

    # mark as posted
    tweet_to_post["posted"] = "TRUE"

    with open("tweets.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)

    print("Tweet posted:", tweet_to_post["tweet_text"])

if __name__ == "__main__":
    post_from_csv()
