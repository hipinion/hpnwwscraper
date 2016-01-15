from dbutils import transactional, get_connection
from bs4 import BeautifulSoup
import re

class passthrough(dict):
    def __missing__(self, key):
        return key

ALIASES = passthrough({
    'bread': 'suspension bridge',
    'bread astaire': 'suspension bridge',
    'nokill': 'no kill',
    'pierrot': 'john plainman',
    'pierrot/john plainman': 'john plainman',
    'pierrot/plainman': 'john plainman',
    'landspeed': 'landspeedrecord',
    'palmer elder itch': 'palmer eldritch',
    'palmer eldtrich': 'palmer eldritch',
    'sep': 'separator',
    'vhb': 'vh balanced',
    'pants': 'pantsoclock',
    'gala gala gala gala': 'galactagogue',
    'van helsing-balanced': 'vh balanced'
    })

color_style_patt = re.compile(r'color: #[0-9A-Fa-f]{6}')

def filter_votes(bolds, color, string):
        return set([tag for tag in bolds if not tag.find_parent('blockquote') and tag.find('span', attrs={'style': 'color: {}'.format(color)}) and tag.find(string=re.compile(r'.*{}.*'.format(string), re.I))])

def find_no_kills(lynch_votes):
    return set([tag for tag in lynch_votes if tag.find('span', string=re.compile(r'.*no kill.*', re.I))])

def find_any_color_vote(bolds):
    return set([tag for tag in bolds if not tag.find_parent('blockquote') and tag.find('span') and color_style_patt.match(tag.find('span').attrs['style'])])

@transactional
def clear_votes():
    cursor = get_connection().cursor()
    cursor.execute('delete from vote')

@transactional
def find_votes():
    cursor = get_connection().cursor()
    cursor.execute('select * from post')
    posts = cursor.fetchall()
    cursor = get_connection().cursor()
    cursor.execute('select name from player')
    names = cursor.fetchall()
    names = set([_['name'] for _ in names])

    for row in posts:
        post_content = row['content']
        parsed_content = BeautifulSoup(post_content)
        bolds = set(parsed_content.find_all('span', attrs={'style': 'font-weight: bold'}))
        votes = {}
        votes['lynch'] = filter_votes(bolds, '#FF0000', 'lynch')
        votes['no kill'] = find_no_kills(votes['lynch'])
        votes['lynch'] = votes['lynch'].difference(votes['no kill'])
        votes['rescind'] = filter_votes(bolds, '#00BF00', 'rescind')
        votes['mayor'] = filter_votes(bolds, '#0000FF', 'mayor')
        votes['rescind mayor'] = filter_votes(bolds, '#FF8000', 'rescind mayor')
        votes['non standard'] = find_any_color_vote(bolds)\
                .difference(votes['lynch'])\
                .difference(votes['no kill'])\
                .difference(votes['rescind'])\
                .difference(votes['mayor'])\
                .difference(votes['rescind mayor'])

        for k, v in votes.items():
            for tag in v:
                context = str(tag)
                vote_type = k
                post = row['thread_sequence']
                player_for = ALIASES[tag.find('span').text.lower().strip(' .')]
                if player_for in names:
                    cursor.execute('insert into vote(post, player_for, type, context) values(%s, %s, %s, %s)', (post, player_for, vote_type, context))
                else:
                    print player_for

if __name__ == '__main__':
    clear_votes()
    find_votes()
