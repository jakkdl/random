#!/usr/bin/python3

import time
import random
import pickle
import os.path

from typing import Dict, List, Tuple
from dataclasses import dataclass
import xml.etree.ElementTree as ET

import requests
import mpd # type: ignore


URL = 'http://feeds.feedburner.com/FrostedBreaksLfk'
MPDDIR = '/data/Media/music'
FBLFKDIR = 'podcast/frosted_breaks'
DIR = os.path.join(MPDDIR, FBLFKDIR)
PICKLE_FILE = os.path.join(DIR, 'fblfk_episodes.pickle')
RSS_FILE = os.path.join(DIR, 'fblfk_rss.xml')

@dataclass
class Episode:
    title: str
    url: str
    count: int

Episodes = Dict[int, Episode]

class PodcastDownloader:
    def __init__(self, url: str, path: str, pickle_file: str, rss_file: str) -> None:
        self.url = url
        self.path = path
        self.pickle_file = pickle_file
        self.rss_file = rss_file
        self.last_update = 0.0
        self.episodes : Episodes = {}
        self.rss = ''


        # if there's no pickled file, download rss and update episodes
        if not self._read_episodes():
            self.update(force=True)
        # if there's no rss file, or it's out of date, update
        elif not self._read_rss():
            self.update(force=True)



    def _read_rss(self) -> bool:
        if os.path.isfile(self.rss_file):
            self.last_update = os.path.getmtime(self.rss_file)
            if time.time() - self.last_update < 86400:
                with open(self.rss_file, 'r', encoding='utf-8') as file:
                    self.rss = file.read()
                return True

        return False

    def _read_episodes(self) -> bool:
        if os.path.isfile(self.pickle_file):
            with open(PICKLE_FILE, 'rb') as file:
                self.episodes = pickle.load(file)
            return True
        return False


    def update(self, force: bool = False) -> None:
        if force or time.time() - self.last_update < 86400:
            self._download_rss()
            self._update_episodes()

    def _download_rss(self) -> None:
        content = requests.get(self.url).text
        with open(self.rss_file, 'w', encoding='utf-8') as file:
            file.write(content)
        self.rss = content
        self.last_update = time.time()

    def _update_episodes(self) -> None:
        modified = False
        root = ET.fromstring(self.rss)
        for item in root[0].findall('item'):
            enclosure = item.find('enclosure')
            if enclosure is None:
                print(f'Found no enclosure for {item.tag}')
                continue
            url = enclosure.attrib['url']
            title = url.split('/')[-1]
            number = int(title.split('-')[1])
            if number not in self.episodes:
                self.episodes[number] = Episode(title, url, 0)
                modified = True

        if modified:
            with open(self.pickle_file, 'wb') as file:
                pickle.dump(self.episodes, file)



    def download_random_episode(self) -> Tuple[int, str]:
        min_downloads = min(self.episodes[ep].count for ep in self.episodes)

        min_played_eps = [ep for ep in self.episodes if self.episodes[ep].count == min_downloads]
        key = random.choice(min_played_eps)
        episode = self.episodes[key]
        full_path = os.path.join(self.path, episode.title)
        print(f'Downloading {episode.title}...', end='', flush=True)
        response = requests.get(episode.url).content

        with open(full_path, 'wb') as file:
            file.write(response)


        print(' done')
        return key, episode.title

    def increment(self, key: int) -> None:
        self.episodes[key].count += 1
        with open(self.pickle_file, 'wb') as file:
            pickle.dump(self.episodes, file)

    def download(self) -> Tuple[int, str]:
        self.update()
        return self.download_random_episode()


    def delete_played_episodes(self, playlist: List[str], directory: str) -> None:
        playlist_files = [x.split(' ')[1].split('/')[-1] for x in playlist]
        downloaded_files = [file for file in os.listdir(directory) if '.mp3' in file]
        for file in downloaded_files:
            if file not in playlist_files:
                print(f'removing {file}')
                os.remove(os.path.join(self.path, file))

def main() -> None:
    client = mpd.MPDClient()
    client.timeout = 10
    client.idletimeout = None
    client.connect("localhost", 6600)

    podcast_downloader = PodcastDownloader(
            url=URL,
            path=DIR,
            pickle_file=PICKLE_FILE,
            rss_file=RSS_FILE)

    try:
        while True:
            try:
                podcast_downloader.delete_played_episodes(client.playlist(), DIR)
                while len(client.playlist()) < 3:
                    client.ping()
                    key, file = podcast_downloader.download()
                    try:
                        client.ping()
                    except mpd.ConnectionError:
                        client.connect("localhost", 6600)
                    client.update(FBLFKDIR)
                    time.sleep(1)
                    client.add(os.path.join(FBLFKDIR, file))
                    podcast_downloader.increment(key)

                print('Idling until playlist change.')
                client.idle('playlist')
            except mpd.ConnectionError:
                client.connect("localhost", 6600)

            except KeyboardInterrupt:
                print()
                break
    finally:
        print('Closing and disconnectiong')
        client.close()
        client.disconnect()

if __name__ == '__main__':
    main()
