#!/usr/bin/python3

import os
import random
import time
import pprint

from tinytag import TinyTag

SAVEFILE='/home/hatten/.stepmania-5.0/Save/LocalProfiles/00000000/Stats.xml'
MUSICDIR='/home/hatten/.stepmania-5.0/Songs'
COURSEDIR='/home/hatten/.stepmania-5.0/Courses'


def generate_mixtape(pattern, max_length):
    result = {}
    pack_stats = {}
    for i in set(pattern):
        result[i] = []

    root = get_save_data()

    for pack in os.listdir(MUSICDIR):
        pack_stats[pack] = 0
        print(pack)
        for songdir in os.listdir(os.path.join(MUSICDIR, pack)):
            fulldir = os.path.join(MUSICDIR, pack, songdir)

            if not os.path.isdir(fulldir):
                continue

            files = os.listdir(fulldir)
            
            ssc = True
            sfile = [x for x in files if '.ssc' in x.lower()]
            if not sfile:
                ssc = False
                sfile = [x for x in files if '.sm' in x.lower()]

            if not sfile:
                print('no sm/ssc found for {}'.format(fulldir))
                continue

            sfile = sfile[0]

            with open(os.path.join(MUSICDIR, pack, songdir, sfile)) as f:
                content = f.readlines()
            
            
            if ssc:
                chart_type = None
                difficulty = None
                meter = 0

                for line in content:
                    if '#STEPSTYPE' in line:
                        chart_type = line.strip().split(':')[1][:-1]
                    if '#DIFFICULTY' in line:
                        difficulty = line.strip().split(':')[1][:-1]
                    if '#METER' in line:
                        meter = int(line.strip().split(':')[1][:-1])
                    if chart_type and difficulty and meter:
                        if 'dance-single' in chart_type and meter in pattern:
                            result[meter].append((os.path.join(pack, songdir),
                                                  difficulty,
                                                  get_songlength(fulldir, files)
                                                 ))
                            pack_stats[pack] += 1
                        chart_type = None
                        difficulty = None
                        meter = 0


            if not ssc:
                i = 0
                while i < len(content):
                    line = content[i]
                    if '#NOTES' in line:
                        i += 1
                        chart_type = content[i].strip()

                        i += 1
                        author = content[i]

                        i += 1
                        difficulty = content[i].strip()[:-1]

                        i += 1
                        meter = int(content[i].strip()[:-1])
                        
                        if ('dance-single' in chart_type
                            and meter in pattern
                           and grade(root, os.path.join(pack, songdir),
                                     difficulty, 6) ):
                            result[meter].append((os.path.join(pack, songdir),
                                                  difficulty,
                                                  get_songlength(fulldir, files)
                                                 ))
                            pack_stats[pack] += 1

                    i += 1

    pprint.pprint(pack_stats)
    mixtape_length = 0
    mixtape = []

    for key,val in result.items():
        print('difficulty {}, {} songs'.format(key, len(val)))

    while mixtape_length < max_length:
        for difficulty in pattern:
            item = result[difficulty].pop(
                random.randrange(len(result[difficulty])))
            mixtape.append(item)
            mixtape_length += item[2]

            if mixtape_length >= max_length:
                break

    pprint.pprint(mixtape)

    filename = 'mixtape_{}.crs'.format(time.time())
    print('writing to {}'.format(filename))

    with open(os.path.join(COURSEDIR, filename), 'w') as f:
        f.write('#COURSE:generated mixtape\n')
        for track in mixtape:
            f.write('#SONG:{}:{};\n'.format(track[0], track[1]))


def get_save_data(f = SAVEFILE):
    import xml.etree.ElementTree as ET
    tree = ET.parse(f)
    root = tree.getroot()
    return root

#AA - tier03
#A - tier04
#B - tier05
#C - tier06
#D - tier07
#F - Failed
def grade(root, song, difficulty, max_grade):
    for current_song in root[1]:
        if song not in current_song.attrib['Dir']:
            continue
        for current_difficulty in current_song:
            if ('dance-single' not in current_difficulty.attrib['StepsType']
                or difficulty.lower() not in
                current_difficulty.attrib['Difficulty'].lower()):
                continue
            if current_difficulty[0].tag != 'HighScoreList':
                print('check xml of {}, has more than '
                      'highscorelist'.format(current_song))
                continue
            grade = current_difficulty[0].find('HighGrade')
            if grade is None:
                return False
            grade = grade.text.lower()
            if grade == 'failed':
                return False 
            grade = int(grade.replace('tier', ''))
            if grade > max_grade:
                return False
            return True
        return False
    return False








def get_songlength(fulldir, files):
    for f in files:
        if '.ogg' in f:
            tag = TinyTag.get(os.path.join(fulldir, f))
            return round(tag.duration)
    return None



if __name__ == '__main__':
    generate_mixtape(pattern=[6,7], max_length=30*60)
