from dbutils import transactional, get_connection
import requests
from bs4 import BeautifulSoup
import config
import re

player_pattern = re.compile(r'(?P<name>[^(]+)\s*(?:\((?P<status>.+)\s+-\s+(?P<role>.+)\))?')
role_pattern = re.compile(r'(?P<role>.[^(]+)')

@transactional
def clear_roles():
    cursor = get_connection().cursor()
    cursor.execute('delete from role')

@transactional
def clear_players():
    cursor = get_connection().cursor()
    cursor.execute('delete from player')

@transactional
def write_roles():
    first_page = requests.get(config.WEREWOLF_THREAD)
    parsed_page = BeautifulSoup(first_page.text)
    third_post = parsed_page.find_all('div', class_='post')[2]
    roles = {}
    roles['werewolf'] = third_post.find_all('span', attrs={'style':"color: #FF0000"})
    roles['vampire'] = third_post.find_all('span', attrs={'style':"color: #400000"})
    roles['village'] = third_post.find_all('span', attrs={'style':"color: #00BF00"})
    roles['switchable'] = third_post.find_all('span', attrs={'style':"color: #808000"})
    roles['neutral'] = third_post.find_all('span', attrs={'style':"color: #8040FF"})
    cursor = get_connection().cursor()
    for role, tags in roles.items():
        for tag in tags:
            if 'ROLES' in tag.text:
                continue
            else:
                match = role_pattern.match(tag.text)
                if match:
                    cursor.execute('insert into role(name, faction) values(%s, %s)', (match.group('role').strip(), role))



@transactional
def write_users():
    first_page = requests.get(config.WEREWOLF_THREAD)
    parsed_page = BeautifulSoup(first_page.text)
    second_post = parsed_page.find_all('div', class_='post')[1]
    cursor = get_connection().cursor()
    in_players = False
    hit_br = False
    for tag in second_post.descendants:
        if not in_players and tag == 'PLAYER LIST:':
            in_players = True
        elif in_players:
            if tag.name == 'br':
                if hit_br:
                    break
                else:
                    hit_br = True
            else:
                hit_br = False
                match = player_pattern.match(tag.strip())
                if match:
                    cursor.execute('insert into player(name, role, status) values(%s, %s, %s)', (match.group('name').strip(), match.group('role'), match.group('status')))

if __name__ == '__main__':
    clear_players()
    clear_roles()
    write_roles()
    write_users()
