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

# For media upload (v1 API required)
auth = tweepy.OAuth1UserHandler(
    os.environ["API_KEY"],
    os.environ["API_SECRET"],
    os.environ["ACCESS_TOKEN"],
    os.environ["ACCESS_TOKEN_SECRET"]
)
api = tweepy.API(auth)

CSV_FILE = "tweets.csv"

rows = []
threads = {}

# ---- Read CSV ----
with open(CSV_FILE, newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        rows.append(row)

        # Skip already posted
        if row.get("posted", "").strip().upper() == "TRUE":
            continue

        thread_id = row.get("thread_id")

        if thread_id not in threads:
            threads[thread_id] = []

        threads[thread_id].append(row)

# ---- Pick FIRST unposted thread ----
thread_to_post = None

for t_id in threads:
    thread = sorted(threads[t_id], key=lambda x: int(x.get("order") or 0))
    if any(r.get("posted", "").strip().upper() != "TRUE" for r in thread):
        thread_to_post = thread
        break

if not thread_to_post:
    print("No tweets left to post.")
    exit(0)

# ---- Post THREAD ----
previous_tweet_id = None
posted_ids = []

for tweet in thread_to_post:
    text = tweet.get("tweet_text", "").strip()
    tweet_type = tweet.get("type", "REPLY").strip().upper()

    try:
        # MAIN tweet → attach image
        if tweet_type == "MAIN":
            image_id = tweet.get("id")
            
            image_path = f"images/post ({image_id}).jpg"

            if os.path.exists(image_path):
                media = api.media_upload(image_path)
                response = client.create_tweet(
                    text=text,
                    media_ids=[media.media_id]
                )
            else:
                print(f"Image not found: {image_path}")
                response = client.create_tweet(text=text)

        # REPLY tweets
        else:
            response = client.create_tweet(
                text=text,
                in_reply_to_tweet_id=previous_tweet_id
            )

        previous_tweet_id = response.data["id"]
        posted_ids.append(tweet.get("id"))

        print(f"Posted: {text[:50]}...")

    except Exception as e:
        print(f"Error posting tweet: {e}")
        break

# ---- Mark as posted ----
for row in rows:
    if row in thread_to_post:
        row["posted"] = "TRUE"

# ---- Save CSV safely ----
fieldnames = ["id", "tweet_text", "thread_id", "order", "type", "posted"]

with open(CSV_FILE, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
    writer.writeheader()
    writer.writerows(rows)

print("Thread posted successfully ✅")
