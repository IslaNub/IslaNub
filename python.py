import datetime
rd = 'release date'
date = datetime.date(2018, 5, 4)
AIW = 'Avengers: Infinity War'
spoiler = 'false'
s = 'spoilers'
if spoiler == 'true':
    print(f'This post about "{AIW}" contains {s}.')
elif spoiler == 'false':
    print(f'This post about "{AIW}" doesn\'t contain {s}.')
print(f'{AIW}\'s {rd} is on {date:%A, %B %d, %Y}.')