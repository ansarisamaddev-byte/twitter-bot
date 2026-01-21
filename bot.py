import csv
import os
import tweepy

# ---- Twitter Auth ----
client = tweepy.Client(
    consumer_key=os.environ["API_KEY"],
    consumer_secret=os.environ["API_SECRET"],
    access_token=os.environ["ACCESS_TOKEN"],
    access_token_secret=os.environ["ACCESS_TOKEN_SECRET"]
)

CSV_FILE = "tweets.csv"

rows = []
tweet_to_post = None

# ---- Read CSV ----
with open(CSV_FILE, newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        rows.append(row)
        if row["posted"].lower() != "true" and tweet_to_post is None:
            tweet_to_post = row

if not tweet_to_post:
    print("No tweets left to post.")
    exit(0)

# ---- Post Tweet ----
response = client.create_tweet(text=tweet_to_post["text"])
tweet_id = response.data["id"]

print(f"Tweet posted: {tweet_id}")

# ---- Mark as posted ----
for row in rows:
    if row["id"] == tweet_to_post["id"]:
        row["posted"] = "true"

# ---- Write back to CSV ----
with open(CSV_FILE, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=rows[0].keys())
    writer.writeheader()
    writer.writerows(rows)
