import spotipy
from spotipy import exceptions
from spotipy.oauth2 import SpotifyOAuth
import cred
from base64 import b64encode
# from time import sleep


# Spotify Connector


class SpotifyPlayer:
    # Default Constructor
    def __init__(self):
        # Spotify Connector
        self.player = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=cred.client_id,
                                                                client_secret=cred.client_secret,
                                                                redirect_uri=cred.redirect_url,
                                                                scope=cred.scope))
        self.device_id = "c3db5ddb12944e3739c933e1ffbe8f4613d8dba9"  # Device to play songs
        self.user_id = ""               # User ID
        self.open_playlist = True       # Is the playlist open to accepting songs?
        self.playlist = []              # List of tracks in the NextUp playlist
        self.playlist_id = ""           # NextUp Playlist ID
        self.playlist_uri = ""          # URI of the NextUp playlist
        self.track_votes = []           # List of dictionaries of tracks along with their votes
        self.tracks_removed = []        # List of songs that have been removed
        self.tracks_banned = []         # List of songs that have been banned
        self.ban_threshold = 3          # Number of times a song is removed from the queue before it is banned
        self.explicit = True            # Determines if explicit songs can be played
        self.party_members = []         # List of party members
        self.party_code = ""            # Party Connect Code

    # DEVICE
    # Get a list of user’s available devices.
    def get_devices(self):
        return self.player.devices()["devices"]

    # Get the Active Device
    def get_active_device(self):
        devices = self.player.devices()["devices"]
        if not devices:
            return {}
        for device in devices:
            if device['is_active'] is True:
                return device
        return {}

    # Get Device ID
    def get_device_id(self):
        return self.device_id

    # Set Device ID
    def set_device_id(self, _device_id):
        self.device_id = _device_id

    # USER
    def get_current_user(self):
        return self.player.current_user()

    def get_current_user_id(self):
        return self.player.current_user()["id"]

    def set_current_user_id(self):
        self.user_id = self.player.current_user()["id"]

    # PLAYLIST
    def get_playlist_open(self):
        return self.open_playlist

    def set_playlist_open(self, _open_playlist):
        self.open_playlist = _open_playlist

    def create_playlist(self, _name):
        return self.player.user_playlist_create(user=self.user_id, name=_name)

    def get_playlist(self):
        return self.playlist

    def get_playlists(self):
        return self.player.user_playlists(user=self.user_id)

    def update_playlist_items(self):
        self.playlist = self.player.playlist_items(playlist_id=self.playlist_id)["items"]

    def set_playlist_cover(self):
        self.player.playlist_upload_cover_image(self.playlist_id, b64encode(open("sample_logo.jpg", "rb").read()))

    # Set the Playlist ID
    def set_playlist_id(self, _playlist_id):
        self.playlist_id = _playlist_id

    # Set The Playlist URI
    def set_playlist_uri(self, _playlist_uri):
        self.playlist_uri = _playlist_uri

    # Add a track to the NextUp playlist
    def add_playlist_track(self, _uri):
        if _uri not in self.tracks_banned:
            for song in self.playlist:
                if song["track"]["uri"] == _uri:
                    return "IN QUEUE"
            self.player.playlist_add_items(self.playlist_id, [_uri])
            self.update_playlist_items()
            return "SUCCESS"
        else:
            return "BANNED"

    # Remove a track from the NextUp playlist
    def remove_playlist_track(self, uri):
        for song in self.playlist:
            if song["track"]["uri"] == uri:
                self.player.playlist_remove_all_occurrences_of_items(self.playlist_id, [uri])
                self.tracks_removed.append(uri)
                break

    # Vote for a track
    def vote_track(self, uri, vote):
        valid_uri = False
        for track in self.playlist:
            if track["track"]["uri"] == uri:
                valid_uri = True
                break
        if valid_uri is True:
            for track in self.track_votes:
                if track["uri"] == uri:
                    if vote == "+":
                        track["votes"] += 1
                        return "successful_upvote"
                    else:
                        track["votes"] -= 1
                        return "successful_downvote"
            if vote == "+":
                self.track_votes.append({"uri": uri, "votes": 1})
                return "successful_upvote"
            else:
                self.track_votes.append({"uri": uri, "votes": -1})
                return "successful_downvote"
        return "invalid_track_uri"

    # Get all track votes
    def get_all_track_votes(self):
        return self.track_votes

    # Get votes for a specific track
    def get_track_votes(self, uri):
        for track in self.track_votes:
            if track["uri"] == uri:
                return track
        return "TRACK HAS NOT BEEN VOTED ON"

    # Remove all tracks from the NextUp playlist
    def clear_playlist(self):
        for song in self.player.playlist_items(playlist_id=self.playlist_id)["items"]:
            self.player.playlist_remove_all_occurrences_of_items(self.playlist_id, [song["track"]["uri"]])

    # Reorder playlist track
    def reorder_track(self, uri, position):
        for x in range(len(self.playlist)):
            if self.playlist[x]["track"]["uri"] == uri:
                return self.player.playlist_reorder_items(playlist_id=self.playlist_id,
                                                          range_start=x,
                                                          insert_before=int(position) - 1)

    # Start athe NextUp playlist
    def start_playlist(self):
        self.player.start_playback(device_id=self.device_id, context_uri=self.playlist_uri)

    # Play a specific track
    def play_track(self, uri):
        self.player.start_playback(device_id=self.device_id, uris=[uri])

    # Start or resume user’s playback.
    def resume(self):
        try:
            return self.player.start_playback(device_id=self.device_id)
        except exceptions.SpotifyException as error:
            return str(error)

    # Pause user’s playback.
    def pause(self):
        try:
            return self.player.pause_playback(device_id=self.device_id)
        except exceptions.SpotifyException as error:
            return str(error)

    # Disable Repeat
    def disable_repeat(self):
        try:
            return self.player.repeat("off", device_id=self.device_id)
        except exceptions.SpotifyException:
            return "device_not_found"

    # Enable Repeat
    def enable_repeat(self):
        try:
            return self.player.repeat("off", device_id=self.device_id)
        except exceptions.SpotifyException:
            return "device_not_found"

    # Set playback volume.
    def set_volume(self, volume):
        try:
            if self.player.volume(int(volume), device_id=self.device_id) is None:
                return "SUCCESS"
        except exceptions.SpotifyException as error:
            return str(error)

    # Get information about user’s current playback.
    def get_current_track(self):
        current_song = self.player.current_playback()["item"]
        _track = {"album_name": current_song["album"]["name"],
                  "artist_name": current_song["artists"][0]["name"],
                  "duration": current_song["duration_ms"],
                  "song_name": current_song["name"],
                  "images": [{"url": current_song["album"]["images"][0]["url"],
                              "size": current_song["album"]["images"][0]["width"]},
                             {"url": current_song["album"]["images"][1]["url"],
                              "size": current_song["album"]["images"][1]["width"]},
                             {"url": current_song["album"]["images"][2]["url"],
                              "size": current_song["album"]["images"][2]["width"]}],
                  "uri": current_song["uri"],
                  "explicit": current_song["explicit"]}
        return _track

    # Check if the current song is playing or paused
    def get_playing_state(self):
        return self.player.current_playback()["is_playing"]

    # Get Explicit
    def get_explicit(self):
        return self.explicit

    # Set Explicit
    def set_explicit(self, _explicit):
        self.explicit = _explicit

    # Searches for an item
    def search(self, _query):
        tracks = []
        query = _query.replace(" ", "+")
        all_tracks = self.player.search(query)
        for x in range(len(all_tracks["tracks"]["items"])):
            _track = {"album": all_tracks["tracks"]["items"][x]["album"]["name"],
                      "artist": all_tracks["tracks"]["items"][x]["artists"][0]["name"],
                      "duration": all_tracks["tracks"]["items"][x]["duration_ms"],
                      "name": all_tracks["tracks"]["items"][x]["name"],
                      "images": [{"url": all_tracks["tracks"]["items"][x]["album"]["images"][0]["url"],
                                  "size": all_tracks["tracks"]["items"][x]["album"]["images"][0]["width"]},
                                 {"url": all_tracks["tracks"]["items"][x]["album"]["images"][0]["url"],
                                  "size": all_tracks["tracks"]["items"][x]["album"]["images"][0]["width"]},
                                 {"url": all_tracks["tracks"]["items"][x]["album"]["images"][0]["url"],
                                  "size": all_tracks["tracks"]["items"][x]["album"]["images"][0]["width"]}],
                      "uri": all_tracks["tracks"]["items"][x]["uri"],
                      "explicit": all_tracks["tracks"]["items"][x]["explicit"]
                      }
            tracks.append(_track)
        return tracks
