# Preface
Quick and dirty script to check for updates in youtube playlists, if new ones are found it sends a Windows Toast notification. Designed to be run as a Scheduled Task as to not deplete all daily youtube API tokens.

# Compatability

Only tested on:

Windows 10

Python 3.11.0

# Installation

Clone the repo and cd into it

`git clone https://github.com/natsukashiixo/playlist-notifs.git; cd playlist-notifs`

Optional: Set up venv

`python -m venv venv`

Install requirements

`pip -r install requirements.txt`

Create your api_key.txt file

`"{api_key_here_keep_the_citation_marks}" | Set-Content -Path "api_key.txt"`

# Usage

Create an empty text file named playlist_urls.txt

`New-Item -ItemType File "playlist_urls.txt"`

Get the playlist ID by going to `youtube.com/@creators_handle/playlists` and clicking on `View full playlist`. You can copy the entire url and put it in the `playlist_urls.txt` file.

If you want to add multiple playlists, simply put them each one on a new line.

If you'd like to only put in the ID, that's also valid. The ID is the part of the url that's after `?list=`. 

The `playlists_url.txt` file's contents are cleared after being read.

After that you can run the script with:

`python main.py`

Notifications should pop up and a file named `stored_values.json` should appear. That file simply stores which playlists you're tracking and the latest addition to the playlist in question.

If you'd like to run it as a task, you can use Windows Task Scheduler to do so.

# To-do

Set up so `watch?=VIDEOID&list=PLAYLISTID` links can be used in `playlist_urls.txt`

Set up some way to configure if/when locally stored thumbnails get deleted instead of doing it at each program launch

# Known bugs

Each time a new playlist is being read in, all existing tracked playlists send a notification.