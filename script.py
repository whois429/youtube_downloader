from typing import Any
from pathlib import Path

import validators
import inquirer
import yt_dlp
from pyfiglet import Figlet


OUT_DIR = '/output'

class MyLogger:
    def debug(self, msg: str) -> None:
        # Comment in youtube-dl documentation:
        # For compatibility with youtube-dl, both debug and info are passed 
        # into debug. You can distinguish them by the prefix '[debug] '
        if msg.startswith('[debug] '):
            pass
        elif any([
                msg.startswith('[youtube]'), 
                msg.startswith('[youtube:tab]'),
                msg.startswith('[Merger]'), 
                'format(s)' in msg,
                'Deleting original file' in msg
            ]):
            pass
        elif not any([msg.startswith('[download] Downloading')]):
            pass
        else:
            self.info(msg)

    def info(self, msg: str) -> None:
        print(msg)

    def warning(self, msg: str) -> None:
        print(msg)

    def error(self, msg: str) -> None:
        print(msg)


def my_hook(d: Any) -> None:
    if d['status'] == 'finished':
        print(f'[download] Video "{d["info_dict"]["title"]}" \
              was downloaded, now post-processing...')


def get_user_input() -> dict[str, str]:
    user_data = inquirer.prompt([
        inquirer.List(
            'type', 
            'Select the type of content you want to download', 
            ['Video', 'Audio']
        )
    ])

    if user_data['type'] == 'Video':
        user_data.update(inquirer.prompt([
            inquirer.List(
                'res', 
                'Select the resolution of downloaded videos', 
                ['2160p', '1440p', '1080p', '720p', 
                 '480p', '360p', '240p', '144p']
            )
        ]))

    user_data['links'] = []
    while True:
        counter = 0

        user_data['links'].append(inquirer.prompt([
            inquirer.Text(
                'link', 
                'Enter a YouTube video link or enter STOP to continue'
            )
        ])['link'])

        if user_data['links'][-1] == 'STOP':
            user_data['links'].pop()
            break
        elif not validators.url(user_data['links'][counter]):
            print(f'The link you entered is invalid \
                  ({user_data["links"][counter]})!')
            user_data['links'].pop()

        counter += 1
    
    return user_data


def download(user_data: dict[str, str]) -> None:
    Path(OUT_DIR).mkdir(parents=True, exist_ok=True)

    if user_data['links']:
        ydl_opts = {
            'outtmpl': OUT_DIR + '/%(title)s.%(ext)s',
            'ignoreerrors': True,
            'logger': MyLogger(),
            'progress_hooks': [my_hook],
        }
        if user_data['type'] == 'Video':
            ydl_opts.update({
                'format': f'bestvideo[height<=\
                    {user_data["res"].replace("p", "")}]+bestaudio/best'
            })
        else:
            ydl_opts.update({
                'format': 'bestaudio/best',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
            })

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download(user_data['links'])


def main() -> None:
    print(Figlet(font='slant').renderText('YouTube   Downloader'))

    download(get_user_input())


if __name__ == '__main__':
    main()
