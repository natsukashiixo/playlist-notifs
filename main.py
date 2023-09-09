import os
from os.path import abspath
import googleapiclient.discovery
from windows_toasts import Toast, WindowsToaster, ToastDisplayImage
import json
import requests
from pathlib import Path

initial_data = [
        {
        "playlist_owner": "",
        "playlist_id": "",
        "stored_video": ""
    }
]
if not os.path.exists('stored_values.json'):
    with open('stored_values.json', 'w') as initial_file:
        json.dump(initial_data, initial_file)

temp_dir = os.path.join(os.environ['TEMP'], 'pyplay_thumb')
os.makedirs(temp_dir, exist_ok=True)
abs_temp_dir = abspath(temp_dir)

reference_url= 'https://www.youtube.com/watch?v=bcvgyfsnY70&list=PLX_S7d-Dodi_pclDCBbAnC-oiWgzHnVkd&index=1'

playlist_id_list = []
playlists_file = 'playlist_urls.txt'

old_ids_list = []
all_ids_list = []


scopes = ["https://www.googleapis.com/auth/youtube.readonly"]

with open('api_key.txt', 'r') as f:
    api_key = f.read()

# -*- coding: utf-8 -*-

# Sample Python code for youtube.playlistItems.list
# See instructions for running these code samples locally:
# https://developers.google.com/explorer-help/code-samples#python


def isolate_playlist_ids(file, json_data):
    with open(file, 'r') as f:
        raw_urls = f.read()
        for line in raw_urls.splitlines():
            if line.startswith('https://') or line.startswith('www.'):
                id_parts = line.split('list=')
                playlist_id = id_parts[1]
                playlist_id_list.append(playlist_id)
            else:
                playlist_id_list.append(line)
        f.close
    with open(file, 'w') as f:
        f.close    

    for entry in json_data:
        if entry.get("playlist_id") != '':
            playlist_id_list.append(entry.get("playlist_id"))


def youtube_accessible():
    try:
        response = requests.get("https://www.youtube.com")
        if response.status_code == 200:
            return True
    except requests.ConnectionError:
        return False

def get_playlist_info(playlist_var: str):
    # Disable OAuthlib's HTTPS verification when running locally.
    # *DO NOT* leave this option enabled in production.
    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "0"

    api_service_name = "youtube"
    api_version = "v3"
    DEVELOPER_KEY = api_key

    youtube = googleapiclient.discovery.build(
        api_service_name, api_version, developerKey = DEVELOPER_KEY)

    request = youtube.playlistItems().list(
        part="id,snippet",
        playlistId=playlist_var
    )
    response = request.execute()

    return response

def isolate_latest_addition(response):
    json_object = response
    unpacked_list = json_object.get("items", [])[0]
    video_id = unpacked_list.get("snippet", {}).get("resourceId", {}).get("videoId", "")
    return video_id

def stored_video_id(playlist_id: str, json_data):
    for entry in json_data:
        if entry.get("playlist_id") == playlist_id:
            return entry.get("stored_video")

def send_notification(response):
    json_object = response
    unpacked_list = json_object.get("items", [])[0]
    # get playlist name from response #there isnt a playlist title lul
    playlist_owner = unpacked_list.get("snippet", {}).get("channelTitle", "") # this will have to do
    video_title = unpacked_list.get("snippet", {}).get("title", "")
    video_owner = unpacked_list.get("snippet", {}).get("videoOwnerChannelTitle", "")
    video_id = unpacked_list.get("snippet", {}).get("resourceId", {}).get("videoId", "")
    thumbnails = unpacked_list.get("snippet", {}).get("thumbnails", {})
    sd_thumbnail_url = thumbnails.get("default", {}).get("url", "")

    yt_url = fr'https://www.youtube.com/watch?v={video_id}'
    
    # locally save thumbnail
    filename = os.path.join(temp_dir, f"{video_id}_{os.path.basename(sd_thumbnail_url)}")
    thumb_response = requests.get(sd_thumbnail_url)
    if thumb_response.status_code == 200:
        with open(filename, 'wb') as local_copy:
            local_copy.write(thumb_response.content)
    thumb_path = abspath(filename)

    # notification magic
    toaster = WindowsToaster('Playlist tracker')
    newToast = Toast()
    newToast.text_fields = [f'Song added by {playlist_owner}', f'{video_title} by {video_owner}', 'Click to play'] # Caps out at 3 items in list.
    newToast.AddImage(ToastDisplayImage.fromPath(thumb_path))
    newToast.launch_action = f'{yt_url}'
    toaster.show_toast(newToast)

def create_json_object(response):
    json_object = response
    unpacked_list = json_object.get("items", [])[0]
    playlist_id = unpacked_list.get("snippet", {}).get("playlistId", "")
    video_id = unpacked_list.get("snippet", {}).get("resourceId", {}).get("videoId", "")
    playlist_owner = unpacked_list.get("snippet", {}).get("channelTitle", "")

    new_json = {'playlist_owner': playlist_owner, 'playlist_id': playlist_id, 'stored_video': video_id}

    return new_json

def clean_temp_folder(folder):
    clean_bool = False
    if clean_bool == True:
        folder = Path(folder)
        for file in folder.glob('*.*'):
            if os.path.exists(file):
                os.unlink(file)

if __name__ == "__main__":
    with open('stored_values.json', 'r') as file:
        json_data = json.load(file)
    if youtube_accessible():
        initial_data = []
        clean_temp_folder(abs_temp_dir)
        isolate_playlist_ids(playlists_file, json_data)
        playlist_id_list = list(set(playlist_id_list))
        for item in playlist_id_list:
            response = get_playlist_info(item)
            to_write = create_json_object(response)
            initial_data.append(to_write)
                
        for item in playlist_id_list:
            old_id = stored_video_id(item, json_data)
            old_dict = {'playlist_id': item, 'video_id': old_id}
            old_ids_list.append(old_dict)

        for item in playlist_id_list:
            response = get_playlist_info(item)
            new_id = isolate_latest_addition(response)
            all_dict = {'playlist_id': item, 'video_id': new_id}
            all_ids_list.append(all_dict)

        for item in all_ids_list.copy():
            if item in old_ids_list:
                all_ids_list.remove(item)    

        if len(all_ids_list) == 0:
            print('No playlists have been updated')
            pass
        else:
            for item in all_ids_list:
                playlist_id = item['playlist_id']
                response = get_playlist_info(playlist_id)
                video_id = isolate_latest_addition(response)
                stored_index = stored_video_id(item, json_data)
                if stored_index != video_id: 
                    send_notification(response)


        with open('stored_values.json', 'w') as write_file:
            json.dump(initial_data, write_file, ensure_ascii=False, indent=4)
    else:
        print('Youtube is unreachable. Check your connection.')
        pass

