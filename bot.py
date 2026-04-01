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

# Media upload client
auth = tweepy.OAuth1UserHandler(
    os.environ["API_KEY"],
    os.environ["API_SECRET"],
    os.environ["ACCESS_TOKEN"],
    os.environ["ACCESS_TOKEN_SECRET"]
)
api = tweepy.API(auth)

CSV_FILE = "tweets.csv"
IMAGE_FOLDER = "images"

rows = []

# ---- Read CSV ----
with open(CSV_FILE, newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        rows.append(row)

# ---- Find next MAIN tweet ----
main_tweet = None

for row in rows:
    if (
        row["type"].strip().upper() == "MAIN" and
        row["posted"].strip().upper() != "TRUE"
    ):
        main_tweet = row
        break

if not main_tweet:
    print("No tweets left.")
    exit(0)

thread_id = main_tweet["thread_id"]

# ---- Get full thread ----
thread_tweets = [
    r for r in rows
    if r["thread_id"] == thread_id
]

# Keep MAIN first, then replies
thread_tweets = sorted(
    thread_tweets,
    key=lambda x: 0 if x["type"].upper() == "MAIN" else 1
)

previous_tweet_id = None

try:
    for tweet in thread_tweets:

        # ---- MAIN (WITH IMAGE) ----
        if tweet["type"].upper() == "MAIN":
            image_name = f"post ({tweet['id']}).jpg"
            image_path = os.path.join(IMAGE_FOLDER, image_name)

            if os.path.exists(image_path):
                media = api.media_upload(image_path)
                response = client.create_tweet(
                    text=tweet["tweet_text"],
                    media_ids=[media.media_id]
                )
                print(f"Posted MAIN with image: {image_name}")
            else:
                response = client.create_tweet(text=tweet["tweet_text"])
                print("Posted MAIN (no image found)")

        # ---- REPLIES (NO IMAGE) ----
        else:
            response = client.create_tweet(
                text=tweet["tweet_text"],
                in_reply_to_tweet_id=previous_tweet_id
            )
            print("Posted reply")

        previous_tweet_id = response.data["id"]

        # ---- Mark as posted ----
        for row in rows:
            if row is tweet:
                row["posted"] = "TRUE"

except Exception as e:
    print(f"Error: {e}")

# ---- Save CSV ----
with open(CSV_FILE, "w", newline="", encoding="utf-8") as f:
    fieldnames = ["id", "tweet_text", "thread_id", "type", "posted"]
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rows)

print("Done.")
