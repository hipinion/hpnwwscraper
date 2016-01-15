import requests
from dbutils import transactional, get_connection
from bs4 import BeautifulSoup
import config
from datetime import datetime
from pytz import timezone
import re
import sys, argparse

time_format = u'%a %b %d, %Y %I:%M %p'
num_posts_pattern = re.compile(r'(?P<num_posts>\d+) posts.*')

@transactional
def clear_all_posts():
    cursor = get_connection().cursor()
    cursor.execute('delete from post')

@transactional
def get_all_posts(start_at_database_end=False):
    cursor = get_connection().cursor()
    cursor.execute('select name from player')
    names = cursor.fetchall()
    names = set([_['name'] for _ in names])
    start = 0
    if start_at_database_end:
        cursor.execute('select max(thread_sequence) as max_post from post')
        start = int(cursor.fetchone()['max_post'])+1
    sequence_number = start
    url = config.WEREWOLF_THREAD + '&start={}'.format(start)
    page = requests.get(url)
    parsed_page = BeautifulSoup(page.text)
    posts = parsed_page.find_all('div', class_='post')
    number_of_posts = int(num_posts_pattern.match(parsed_page.find('div', class_='pagination').text.strip()).group('num_posts'))
    while start < number_of_posts:
        print start, len(posts)
        for post in posts:
            username = post.find_all('a', class_='username-coloured')[0]
            post_time = username.parent.nextSibling.strip(u' \xbb')
            post_time = datetime.strptime(post_time, time_format)
            post_time = timezone('US/Pacific').localize(post_time)
            username = username.text.lower()
            post_content = str(post.find('div', class_='content'))
            if not username in names:
                print username
            else:
                cursor.execute('insert into post(player, time, content, thread_sequence) values(%s, %s, %s, %s)', (username, post_time, post_content, sequence_number))
            sequence_number += 1
        start += 30
        url = config.WEREWOLF_THREAD + '&start={}'.format(start)
        page = requests.get(url)
        parsed_page = BeautifulSoup(page.text)
        posts = parsed_page.find_all('div', class_='post')
        number_of_posts = int(num_posts_pattern.match(parsed_page.find('div', class_='pagination').text.strip()).group('num_posts'))

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Collect posts")
    parser.add_argument('--clear_all', action='store_true')
    args = parser.parse_args()
    if args.clear_all:
        clear_all_posts()
    get_all_posts(not args.clear_all)
