#!/usr/bin/ipython

import os
import os.path
import subprocess
import eyed3

from dataclasses import dataclass

MUSIC_DIRECTORY = '/data/Media/music/'
PLAYLIST_DIRECTORY = '/home/hatten/.config/mpd/playlists/'
BANNED_GENRES = ['Tribal', 'Downtempo', 'Psychedelic']
BANNED_ARTIST = ['Die Antwoord', 'Skrillex', 'Fox Stevenson', 'Binärpilot',
                 'League of Legends', 'BABYMETAL', 'Pentakill']

@dataclass
class ID3Tags:
    title: str = ""
    artist: str = ""
    genre: str = ""
    bpm: float = 0

def main():
    for root, subdirectory, files in os.walk(MUSIC_DIRECTORY):
        if 'mixes' in root.lower() or 'youtube-dl' in root.lower():
            continue
        for f in files:
            if '.mp3' in f:

                if 'podcast' in f.lower() or 'necrodancer' in f.lower():
                    continue

                full_path = os.path.join(root, f)
                mpd_path = '/'.join(full_path.split('/')[4:])
                bpm = None
                title = None

                try:
                    file_tags = get_info_id3v2_subprocess(full_path)
                except UnicodeDecodeError as e:
                    print('broken tags:', full_path, file=sys.stderr)
                    continue


                bpm = file_tags.bpm

                # ditch long songs
                if file_tags.artist in BANNED_ARTIST:
                    continue

                if bpm==None or bpm==0:
                    print('calculating bpm for', f)
                    p = subprocess.run(
                        ['bpm-tag', '-n', full_path],
                        capture_output=True, check=True, text=True)
                    bpm = float(p.stderr.split(' ')[-2])
                    bpmround = round(bpm)
                    if abs(bpm - bpmround) > 0.15:
                        print(bpm, bpmround,
                              "difference too large, check manually:")
                        continue
                        subprocess.run(['mpc', 'insert', '--wait', mpd_path],
                                       check=True, capture_output=True)
                        subprocess.run(['mpc', '--wait', 'next'], check=False, capture_output=True)
                        subprocess.run(['mpc', 'play'], check=False, capture_output=True)
                        subprocess.run(['mpc', 'seek', '40%'], check=False, capture_output=True)
                        input_str = input('BPM: ')
                        if input_str == "0":
                            print('skipping')
                            continue
                        elif input_str != "":
                            bpmround = int(input_str)
                        #subprocess.run(['mpc', 'pause'], check=False, capture_output=True)



                    subprocess.run(
                        ['id3v2', '--TBPM', str(bpmround), full_path],
                        check=True)
                    bpm = bpmround

                if 90 <= bpm <= 110 and file_tags.genre not in BANNED_GENRES:
                    print(mpd_path)
                    # print(file_tags.title, ';',
                    #       bpm, 'bpm', ';',
                    #       'genre:', file_tags.genre)

def get_info_id3v2_subprocess(full_path):
    result = ID3Tags()
    p = subprocess.run(
        ['id3v2', '-l', full_path],
        capture_output=True, check=True, text=True)
    for line in p.stdout.split('\n'):
        if 'TPE1' in line:
            result.artist = ' '.join(line.split(' ')[3:])
        if 'TIT2' in line:
            result.title = ' '.join(line.split(' ')[3:])
        if 'TBPM' in line:
            result.bpm = float(line.split(' ')[-1])
        if 'TCON' in line:
            result.genre = line.split(' ')[3]
    return result


def get_info_eyed3_module(full_path):
    eyed3_file = eyed3.load(full_path)
    artist = eyed3_file.tag.artist
    genre = "" if not eyed3_file.tag.genre else eyed3_file.tag.genre.name
    title = eyed3_file.tag.title
    bpm = float(eyed3_file.tag.bpm)

def get_info_eyed3_subprocess(full_path):
    p = subprocess.run(
        ['eyeD3', full_path],
        capture_output=True, check=True, text=True)
    for line in p.stdout.split('\n'):
        if 'artist:' in line:
            artist = ' '.join(line.split(' ')[1:])
        if 'title:' in line:
            title = ' '.join(line.split(' ')[1:])
        if 'BPM:' in line:
            bpm = int(line.split(' ')[1])
        if 'genre:' in line:
            genre = line.split(' ')[-3]


if __name__ == '__main__':
    main()
