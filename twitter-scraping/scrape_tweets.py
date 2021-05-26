import time
import urllib.parse
from selenium import webdriver

from db import *

# Converts a long HTTP URL to the shortened youtu.be URL
def get_short_url(long_url):
    base_url = "http://www.youtube.com/watch?v="
    short_base_url ="https://youtu.be/"
    return long_url.replace(base_url, short_base_url)


def get_search_url(short_video_url):
    base_url = "https://twitter.com/search?q="
    suffix = "&src=typed_query&f=live"
    enc_video_url = urllib.parse.quote(short_video_url, safe='')
    return base_url + enc_video_url + suffix


def get_tweets(video):
    driver = webdriver.Chrome("./chromedriver")

    short_video_url = get_short_url(video[1])
    search_url = get_search_url(short_video_url)
    driver.get(search_url)
    time.sleep(2)

    all_tweets = list(driver.find_elements_by_css_selector('div[data-testid="tweet"]'))
    tweetcount = len(all_tweets)
    print("Collected " + str(tweetcount) + " tweets for video at " + short_video_url)

    # No tweets for this video
    if tweetcount == 0:
        print("No tweets found for video at " + short_video_url)
        driver.close()
        return

    # Scroll & scrape
    tweet_htmls = [e.get_attribute('outerHTML') for e in all_tweets]
    delta = 1
    while delta > 0:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(3)

        delta = 0
        for nt in driver.find_elements_by_css_selector('div[data-testid="tweet"]'):
            if not nt in all_tweets:
                all_tweets.append(nt)
                tweet_htmls.append(nt.get_attribute('outerHTML'))
                delta += 1
        
        print("Collected " + str(delta) + " tweets for video at " + short_video_url)

    driver.close()

    print("Done scraping, saving tweets to DB...")
    for t in tweet_htmls:
        create_tweet((video[0], t))


def main():
    create_tweets_table()

    # Main scraping loop...
    while True:
        vid = next_unprocessed_video()
        if not vid:
            break

        drop_tweets_of_video(vid[0])
        get_tweets(vid)
        set_video_to_scraped(vid[0])


if __name__ == '__main__':
    main()