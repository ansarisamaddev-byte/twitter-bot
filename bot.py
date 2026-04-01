import csv
import os
import time
import tweepy

# ---- Twitter Auth (v2 for tweets) ----
client = tweepy.Client(
    consumer_key=os.environ["API_KEY"],
    consumer_secret=os.environ["API_SECRET"],
    access_token=os.environ["ACCESS_TOKEN"],
    access_token_secret=os.environ["ACCESS_TOKEN_SECRET"]
)

# ---- Auth (v1.1 for media upload) ----
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

# ---- Find next unposted thread ----
thread_id_to_post = None

for row in rows:
    if row.get("posted", "").strip().upper() != "TRUE":
        thread_id_to_post = row.get("thread_id")
        break

if not thread_id_to_post:
    print("No tweets left to post.")
    exit(0)

# ---- Collect full thread ----
thread_rows = [r for r in rows if r.get("thread_id") == thread_id_to_post]
thread_rows.sort(key=lambda x: int(x.get("order", 0)))

print(f"Posting thread: {thread_id_to_post}")

previous_tweet_id = None
posted_ids = []

# ---- Post thread ----
for tweet in thread_rows:
    try:
        tweet_text = tweet.get("tweet_text", "").strip()
        tweet_id_val = tweet.get("id")

        if not tweet_text:
            continue

        # ---- Image path ----
        image_path = os.path.join(IMAGE_FOLDER, f"post ({tweet_id_val}).jpg")
        media_ids = None

        if os.path.exists(image_path):
            print(f"Uploading image: {image_path}")
            media = api.media_upload(image_path)
            media_ids = [media.media_id]
        else:
            print(f"No image for tweet {tweet_id_val}")

        # ---- Post tweet ----
        response = client.create_tweet(
            text=tweet_text,
            in_reply_to_tweet_id=previous_tweet_id,
            media_ids=media_ids
        )

        new_tweet_id = response.data["id"]
        print(f"Posted tweet: {new_tweet_id}")

        previous_tweet_id = new_tweet_id
        posted_ids.append(tweet_id_val)

        time.sleep(2)  # avoid rate limits

    except Exception as e:
        print(f"Error posting tweet {tweet.get('id')}: {e}")
        break

# ---- Mark as posted ONLY if success ----
for row in rows:
    if row.get("id") in posted_ids:
        row["posted"] = "TRUE"

# ---- Safe write to CSV ----
fieldnames = ["id", "tweet_text", "thread_id", "order", "posted"]

with open(CSV_FILE, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
    writer.writeheader()
    writer.writerows(rows)

print("Done ✅")
