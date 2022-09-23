import music_tag as mt

# file = mt.load_file('test.mp3')

# file['title'] = 'test123'
# file['album'] = 'test456'
# file['artist'] = 'test789'
# file.save()

# print(file['title'])

import os
import re

errors = 0
ok = 0

for root, _, files in os.walk('./data/downloads'):
    for f in files:
        r = re.search(r'(.*)-(.*)\.mp3', f)

        try:
            file = mt.load_file(f'{root}/{f}')
            file['artist'] = r.group(1).strip()
            file['title'] = r.group(2).strip()

            strano = 'strano'
            domace = 'domace'
            if root.find(strano):
                file['album'] = strano
            elif root.find(domace):
                file['album'] = domace
            else:
                pass

            file.save()

            ok+=1

        except Exception as e:
            print(f'Error at "{root}/{f}" file: {e}')
            errors+=1

print(ok, "\t", errors)
