import tweepy
import os
import csv

client = tweepy.Client(
    consumer_key=os.getenv("API_KEY"),
    consumer_secret=os.getenv("API_SECRET"),
    access_token=os.getenv("ACCESS_TOKEN"),
    access_token_secret=os.getenv("ACCESS_TOKEN_SECRET"),
)

def post_from_csv():
    with open("tweets.csv", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    if not rows:
        print("CSV is empty")
        return

    # find first unposted item
    first = next((r for r in rows if r.get("posted") == "FALSE"), None)

    if not first:
        print("No tweets left")
        return

    thread_id = first.get("thread_id", "").strip()

    # 🧵 THREAD LOGIC
    if thread_id:
        thread_tweets = sorted(
            [
                r for r in rows
                if r.get("thread_id", "").strip() == thread_id
                and r.get("posted") == "FALSE"
            ],
            key=lambda r: int(r.get("order", 0))
        )

        previous_tweet_id = None

        for tweet in thread_tweets:
            if previous_tweet_id:
                response = client.create_tweet(
                    text=tweet["tweet_text"],
                    in_reply_to_tweet_id=previous_tweet_id
                )
            else:
                response = client.create_tweet(text=tweet["tweet_text"])

            previous_tweet_id = response.data["id"]
            tweet["posted"] = "TRUE"

        print(f"Thread posted: {thread_id}")

    # 📝 SINGLE TWEET LOGIC
    else:
        client.create_tweet(text=first["tweet_text"])
        first["posted"] = "TRUE"
        print("Tweet posted:", first["tweet_text"])

    # write back to CSV
    with open("tweets.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)

if __name__ == "__main__":
    post_from_csv()
