import os
from pathlib import Path
from pytube import YouTube
from flask import Flask, redirect, render_template, request, session, url_for, jsonify
from flask_bootstrap import Bootstrap
from youtubesearchpython import VideosSearch
from moviepy.editor import VideoFileClip
from bs4 import BeautifulSoup
import threading

from spotipy import Spotify
from spotipy.oauth2 import SpotifyOAuth
from spotipy.cache_handler import FlaskSessionCacheHandler

client_id = "d262067fcbd044c9bee4d6d6b47a4291"
client_secret = "66197e8aa71a4605bbc9b936ddc217a0"
redirect_uri = "http://localhost:5000/callback"
scope = "playlist-read-private, streaming, playlist-modify-private, user-library-modify, user-library-read"

cache_handler = FlaskSessionCacheHandler(session)
sp_oauth = SpotifyOAuth(
    client_id=client_id,
    client_secret=client_secret,
    redirect_uri=redirect_uri,
    scope=scope,
    cache_handler=cache_handler,
)
sp = Spotify(auth_manager=sp_oauth)

################### Flask Setup #################
app = Flask(__name__)
Bootstrap(app)
app.config["SECRET_KEY"] = os.urandom(64)

downloads_status = {
    "total_videos": 0,
    "downloaded_videos": 0,
    "converted_videos": 0,
    "downloaded_songs": set(),  # Usado para evitar downloads redundantes
}


def update_status(downloaded=False, converted=False):
    if downloaded:
        downloads_status["downloaded_videos"] += 1
    if converted:
        downloads_status["converted_videos"] += 1


def download_and_convert(video_url, path, finished_event):
    # Download the video
    yt = YouTube(video_url, use_oauth=False, allow_oauth_cache=True)
    yd = yt.streams.get_highest_resolution()
    yd.download(path)
    update_status(downloaded=True)

    # Convert the videos to .mp3 format
    file_name = yd.default_filename
    video_path = os.path.join(path, file_name)
    audio_path = os.path.splitext(video_path)[0] + ".mp3"
    try:
        # Load the video file
        video = VideoFileClip(video_path)
        # Extract the audio
        audio = video.audio
        # Write the audio to an .mp3 file
        audio.write_audiofile(audio_path)
        # Close the video and audio objects
        video.close()
        audio.close()
        # Delete the original video file
        os.remove(video_path)
        update_status(converted=True)
    except Exception as e:
        print(f"Erro ao converter o vídeo {file_name}: {e}")
    finally:
        if all(
            [
                downloads_status["downloaded_videos"]
                == downloads_status["total_videos"],
                downloads_status["converted_videos"]
                == downloads_status["total_videos"],
            ]
        ):
            finished_event.set()
            # Reset the download_status values to zero
            downloads_status["total_videos"] = 0
            downloads_status["downloaded_videos"] = 0
            downloads_status["converted_videos"] = 0
            downloads_status["downloaded_songs"] = set()


@app.route("/")
def home():
    if not sp_oauth.validate_token(cache_handler.get_cached_token()):
        auth_url = sp_oauth.get_authorize_url()
        return redirect(auth_url)
    return redirect(url_for("select_playlist"))


@app.route("/callback")
def callback():
    try:
        sp_oauth.get_access_token(request.args["code"])
    except Exception as e:
        print(f"Erro ao obter token de acesso: {e}")

    print(f"Código de Autorização: {request.args['code']}")
    return redirect(url_for("select_playlist"))


@app.route("/select_playlist")
def select_playlist():
    # Assuming sp is your Spotify API object
    if not sp_oauth.get_access_token(cache_handler.get_cached_token()):
        auth_url = sp_oauth.get_authorization_code()
        return redirect(auth_url)

    # Fetch the user's playlists
    playlists = sp.current_user_playlists()

    # Extract playlist information
    playlists_info = [(pl["name"], pl["id"]) for pl in playlists["items"]]

    # Check if a specific playlist is requested
    playlist_id = request.args.get("playlist_id")
    downloaded_songs = []

    if playlist_id:
        playlist_tracks = sp.playlist_tracks(playlist_id)
        playlist = sp.playlist(playlist_id)
        playlist_name = playlist["name"]

        # Caminho que serão baixadas as musicas por padrão
        downloads_path = str(Path.home() / f"Downloads/Spotify Musics/{playlist_name}")

        # Extrair nome das musicas com os artistas
        songs_info = [
            (
                track["track"]["name"],
                " - ".join([artist["name"] for artist in track["track"]["artists"]]),
            )
            for track in playlist_tracks["items"]
        ]

        # Merge song names and artists into a single string variable
        music_list = [f"{name} - {artists}" for name, artists in songs_info]
        music = "\n".join(music_list)

        downloads_status["total_videos"] = len(playlist_tracks["items"])
        finished_event = threading.Event()

        for line in music.split("\n"):
            if line in downloads_status["downloaded_songs"]:
                continue

            videosSearch = VideosSearch(line, limit=1)
            search_results = videosSearch.result().get("result", [])

            if search_results:
                video_url = search_results[0]["link"]
                print(line + " URL: " + video_url)
                threading.Thread(
                    target=download_and_convert,
                    args=(video_url, downloads_path, finished_event),
                ).start()
                downloaded_songs.append(line)
                downloads_status["downloaded_songs"].add(line)
            else:
                print(f"No video found for the song: {line}")

        # Wait for all downloads to finish
        finished_event.wait()
        return redirect(url_for("select_playlist"))

    return render_template(
        "playlists.html",
        playlists_info=playlists_info,
        downloaded_songs=downloaded_songs,
    )

@app.route('/get_progress')
def get_progress():
    total_songs = downloads_status['total_videos']
    downloaded_songs = len(downloads_status['downloaded_songs'])
    converted_videos = downloads_status['converted_videos']

    if total_songs > 0:
        progress_percentage = (downloaded_songs / total_songs) * 100
        conv_percentage = (converted_videos / total_songs) * 100
    else:
        progress_percentage = 0  # Define como 0 se total_songs for igual a zero
        conv_percentage = 0

    return jsonify({
        'progress_percentage': progress_percentage, 
        'conv_percentage': conv_percentage
    })

@app.route("/about")
def about():
    return render_template("about.html")


if __name__ == "__main__":
    app.run(debug=True)
