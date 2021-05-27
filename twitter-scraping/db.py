import sqlite3
from sqlite3 import Error

def create_connection():
    db_file = "./db.db"
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        if conn is None:
            print("Error! Cannot connect to the database.")

        return conn
    except Error as e:
        print(e)
    
    return conn

def execute_sql(sql):
    conn = create_connection()
    try:
        c = conn.cursor()
        c.execute(sql)
    except Error as e:
        print(e)

    conn.close()


def create_videos_table():
    conn = create_connection()
    sql_statement = """CREATE TABLE IF NOT EXISTS videos (
                            id integer PRIMARY KEY,
                            category text NOT NULL,
                            channel text NOT NULL,
                            title text NOT NULL,
                            date text NOT NULL,
                            views integer NOT NULL,
                            link text NOT NULL,
                            tweets_scraped integer NOT NULL DEFAULT 0
                        )"""
    execute_sql(sql_statement)
    conn.close()

def create_tweets_table():
    conn = create_connection()
    sql = """CREATE TABLE IF NOT EXISTS tweets (
                id integer PRIMARY KEY,
                video_id integer NOT NULL,
                raw_html text NOT NULL,
                processed integer NOT NULL DEFAULT 0,
                user_name text,
                user_handle text,
                content text,
                date text,
                replies integer,
                retweets integer,
                likes integer,
                FOREIGN KEY(video_id) REFERENCES videos(id)
            )"""
    cur = conn.cursor()
    cur.execute(sql)
    conn.close()

def create_video(video):
    conn = create_connection()
    sql = """INSERT INTO videos(category, channel, title, date, views, link)
             VALUES(?,?,?,?,?,?)"""
    cur = conn.cursor()
    cur.execute(sql, video)
    conn.commit()
    vid_id = cur.lastrowid
    conn.close()
    return vid_id

def next_unprocessed_video():
    conn = create_connection()
    sql = """SELECT id, link
             FROM   videos
             WHERE  tweets_scraped = 0
             LIMIT  1"""
    cur = conn.cursor()
    cur.execute(sql)
    vid = cur.fetchone()
    conn.close()
    return vid

def next_uncomputed_video():
    conn = create_connection()
    sql = """SELECT id
             FROM   videos
             WHERE  tweet_count IS NULL"""
    cur = conn.cursor()
    cur.execute(sql)
    video = cur.fetchone()
    conn.close()
    if video:
        return video[0]
    else:
        return None

def next_unprocessed_tweet():
    conn = create_connection()
    sql = """SELECT id, raw_html
             FROM   tweets
             WHERE  processed = 0
             LIMIT  1"""
    cur = conn.cursor()
    cur.execute(sql)
    tweet = cur.fetchone()
    conn.close()
    return tweet

def next_tweet_with_processing_status(status):
    conn = create_connection()
    sql = """SELECT id, raw_html
             FROM   tweets
             WHERE  processed = ?
             LIMIT  1"""
    cur = conn.cursor()
    cur.execute(sql, (status,))
    tweet = cur.fetchone()
    conn.close()
    return tweet

def create_tweet(tweet):
    conn = create_connection()
    sql = """INSERT INTO tweets(video_id, raw_html)
             VALUES (?,?)"""
    cur = conn.cursor()
    cur.execute(sql, tweet)
    conn.commit()
    tweet_id = cur.lastrowid
    conn.close()
    return tweet_id

def update_tweet(tweet):
    conn = create_connection()
    sql = """UPDATE tweets
             SET    user_name = ?,
                    user_handle = ?,
                    content = ?,
                    date = ?,
                    replies = ?,
                    retweets = ?,
                    likes = ?,
                    processed = 1
            WHERE   id = ?"""
    cur = conn.cursor()
    cur.execute(sql, tweet)
    conn.commit()
    conn.close

def set_tweet_processing_status(tweet_id, status):
    conn = create_connection()
    sql = """UPDATE tweets
             SET    processed = ?
             WHERE  id = ?"""
    cur = conn.cursor()
    cur.execute(sql, (status, tweet_id))
    conn.commit()
    conn.close()

def mark_processing_fail(tweet_id):
    conn = create_connection()
    sql = """UPDATE tweets
             SET    processed = -1
             WHERE  id = ?"""
    cur = conn.cursor()
    cur.execute(sql, (tweet_id,))
    conn.commit()
    conn.close()

def drop_tweets_of_video(video_id):
    conn = create_connection()
    sql = """DELETE FROM tweets 
             WHERE video_id=?"""
    cur = conn.cursor()
    cur.execute(sql, (video_id,))
    conn.commit()
    conn.close()

def set_video_to_scraped(video_id):
    conn = create_connection()
    sql = """UPDATE videos
             SET    tweets_scraped = 1
             WHERE  id = ?"""
    cur = conn.cursor()
    cur.execute(sql, (video_id,))
    conn.commit()
    conn.close()

def create_columns_for_video_stats():
    conn = create_connection()
    sql = ["ALTER TABLE videos ADD tweet_count integer;",
           "ALTER TABLE videos ADD retweet_count integer;",
           "ALTER TABLE videos ADD like_count integer;",
           "ALTER TABLE videos ADD reply_count integer;",
           "ALTER TABLE videos ADD normalized_tweet_count real;",
           "ALTER TABLE videos ADD normalized_retweet_count real;",
           "ALTER TABLE videos ADD normalized_like_count real;",
           "ALTER TABLE videos ADD normalized_reply_count real;"]

    cur = conn.cursor()
    for s in sql:
        cur.execute(s)

    conn.commit()
    conn.close()

def compute_stats(video_id):
    conn = create_connection()
    sql = ["UPDATE videos SET tweet_count = (SELECT COUNT(*) FROM tweets WHERE video_id = videos.id) WHERE id = ?",
           "UPDATE videos SET retweet_count = (SELECT SUM(retweets) FROM tweets WHERE video_id = videos.id) WHERE id = ?",
           "UPDATE videos SET like_count = (SELECT SUM(likes) FROM tweets WHERE video_id = videos.id) WHERE id = ?",
           "UPDATE videos SET reply_count = (SELECT SUM(replies) FROM tweets WHERE video_id = videos.id) WHERE id = ?",
           "UPDATE videos SET normalized_tweet_count = (SELECT tweet_count*1.0 / views FROM videos WHERE id = id) WHERE id = ?",
           "UPDATE videos SET normalized_retweet_count = (SELECT retweet_count*1.0 / views FROM videos WHERE id = id) WHERE id = ?",
           "UPDATE videos SET normalized_like_count = (SELECT like_count*1.0 / views FROM videos WHERE id = id) WHERE id = ?",
           "UPDATE videos SET normalized_reply_count = (SELECT reply_count*1.0 / views FROM videos WHERE id = id) WHERE id = ?"]

    cur = conn.cursor()
    for s in sql:
        cur.execute(s, (video_id,))

    conn.commit()
    conn.close()