from bs4.element import ContentMetaAttributeValue
from db import *
from bs4 import BeautifulSoup
import re

def get_username_from_html(raw_html):
    soup = BeautifulSoup(raw_html, 'html.parser')
    # Content of second link to profile -> span -> span.text
    # <div class="css-1dbjc4n r-1wbh5a2 r-dnmrzs">
    #   ...
    #     <span class="css-901oao css-16my406 r-poiln3 r-bcqeeo r-qvutc0">
    #          <span class="css-901oao css-16my406 r-poiln3 r-bcqeeo r-qvutc0">
    #               Grigor Hindoyan
    link = soup.find_all('a', {'href': re.compile(r'\/[a-zA-Z0-9_]*$')})[1]
    name_span = link.find('span').find('span')
    return name_span.getText()

def get_user_handle_from_html(raw_html):
    # First in page
    # <a href="/SaphireG2" role="link"
    soup = BeautifulSoup(raw_html, 'html.parser')
    return soup.find('a', {'href': re.compile(r'\/[a-zA-Z0-9_]*$')})['href'][1:]

def get_content_from_html(raw_html):
    # TODO...
    return ""
    

def get_date_from_html(raw_html):
    # <time datetime="2021-05-14T22:16:25.000Z">May 15</time>
    soup = BeautifulSoup(raw_html, 'html.parser')
    return soup.find('time')['datetime']

def get_replies_from_html(raw_html):
    # <div aria-label="0 Replies. Reply" role="button" tabindex="0"
    soup = BeautifulSoup(raw_html, 'html.parser')
    div = soup.find('div', {'aria-label': re.compile(r'Repl(ies|y)')})
    return int(div['aria-label'].split()[0])

def get_retweets_from_html(raw_html):
    # <div aria-label="0 Retweets. Retweet" role="button" tabindex="0"
    soup = BeautifulSoup(raw_html, 'html.parser')
    div = soup.find('div', {'aria-label': re.compile(r'Retweet[s]?')})
    return int(div['aria-label'].split()[0])


def get_likes_from_html(raw_html):
    # <div aria-label="0 Likes. Like" role="button" tabindex="0"
    soup = BeautifulSoup(raw_html, 'html.parser')
    div = soup.find('div', {'aria-label': re.compile(r'Like[s]?')})
    return int(div['aria-label'].split()[0])

def pass_one(id, raw_html):
    user_name = get_username_from_html(raw_html)
    user_handle = get_user_handle_from_html(raw_html)
    content = get_content_from_html(raw_html)
    date = get_date_from_html(raw_html)
    replies = get_replies_from_html(raw_html)
    retweets = get_retweets_from_html(raw_html)
    likes = get_likes_from_html(raw_html)

    processed_tweet = (
        user_name,
        user_handle,
        content,
        date,
        replies,
        retweets,
        likes,
        id
    )

    update_tweet(processed_tweet)
    print("[1] Processed tweet ID " + str(id) + ": " + str(processed_tweet))

def pass_two(id, raw_html):
    user_name = ""
    user_handle = ""
    content = ""
    date = get_date_from_html(raw_html)
    replies = get_replies_from_html(raw_html)
    retweets = get_retweets_from_html(raw_html)
    likes = get_likes_from_html(raw_html)

    processed_tweet = (
        user_name,
        user_handle,
        content,
        date,
        replies,
        retweets,
        likes,
        id
    )

    update_tweet(processed_tweet)
    set_tweet_processing_status(id, 2)
    print("[2] Processed tweet ID " + str(id) + ": " + str(processed_tweet))

def main():
    while True:
        tweet = next_unprocessed_tweet()
        if not tweet:
            break

        id = tweet[0]
        raw_html = tweet[1]

        try:
            pass_one(id, raw_html)
        except:
            try: # Try scraping w/o username...
                pass_two(id, raw_html)
            except:
                mark_processing_fail(id)
                print("Failed to process tweet ID " + str(id))
            


if __name__ == '__main__':
    main()
