from flask import Flask, jsonify, request
from flask_cors import CORS
import threading
import SpotifyPlayer
import HolePuncher
import qrcode


if __name__ == '__main__':
    # Configure and Start Flask
    app = Flask(__name__)
    app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True
    CORS(app)
    threading.Thread(target=app.run, kwargs={"host": "0.0.0.0", "port": 5000}).start()

    # Start HolePuncher
    HolePuncher1 = HolePuncher.HolePuncher()
    HolePuncher1.punch()
    connect_code_qr = qrcode.make(HolePuncher1.tunnel)
    connect_code_qr.save("connect_code.png")

    SpotifyPlayer1 = SpotifyPlayer.SpotifyPlayer()

    # DEVICE
    @app.route("/get_devices", methods=["GET"])
    def get_devices():
        return jsonify(SpotifyPlayer1.get_devices())

    @app.route("/get_active_device", methods=["GET"])
    def get_active_device():
        return jsonify(SpotifyPlayer1.get_active_device())

    @app.route("/set_device", methods=["PUT"])
    def set_device():
        data = request.form.to_dict(flat=False)
        try:
            if data["device_id"][0]:
                SpotifyPlayer1.set_device_id(_device_id=data["device_id"][0])
                return jsonify({"message": "device_selection_success"})
            else:
                return jsonify({"error": "missing_device_id"})
        except KeyError as error:
            if error == "device_id":
                return jsonify({"error": "missing_device_id"})

    # USER
    @app.route("/get_current_user", methods=["GET"])
    def get_current_user():
        return SpotifyPlayer1.get_current_user()

    @app.route("/get_current_user_id", methods=["GET"])
    def get_current_user_id():
        return jsonify({"user_id": SpotifyPlayer1.get_current_user_id()})

    # Playlist
    @app.route("/get_playlist", methods=["GET"])
    def get_queue():
        return jsonify(SpotifyPlayer1.get_playlist())

    @app.route("/get_current_song", methods=["GET"])
    def get_current_song():
        return jsonify({"current_song": SpotifyPlayer1.get_current_track()})

    @app.route("/get_next_song", methods=["GET"])
    def get_next_song():
        return jsonify({"next_song": SpotifyPlayer1.get_playlist()[1]})

    @app.route("/add_playlist_track", methods=["PUT"])
    def add_playlist_track():
        data = request.form.to_dict(flat=False)
        try:
            if data["uri"][0].split():
                song_request = SpotifyPlayer1.add_playlist_track(data["uri"][0].strip())
            else:
                return jsonify({"error": "missing_uri"})
        except KeyError:
            return jsonify({"error": "missing_uri"})
        if song_request == "SUCCESS":
            return jsonify(["successful_add"])
        elif song_request == "IN QUEUE":
            return jsonify(["track_already_in_queue"])
        elif song_request == "BANNED":
            return jsonify(["track_banned"])

    @app.route("/get_all_track_votes", methods=["GET"])
    def get_all_track_votes():
        return jsonify(SpotifyPlayer1.get_all_track_votes())

    @app.route("/get_track_votes",  methods=["GET"])
    def get_track_votes():
        data = request.form.to_dict(flat=False)
        try:
            if data["uri"][0].strip():
                return jsonify(SpotifyPlayer1.get_track_votes(uri=data["uri"][0].strip()))
            else:
                return jsonify({"error": "missing_uri"})
        except KeyError:
            return jsonify({"error": "missing_uri"})

    @app.route("/vote_track", methods=["PUT"])
    def vote_track():
        data = request.form.to_dict(flat=False)
        try:
            if data["uri"][0].strip():
                pass
            else:
                return jsonify({"error": "missing_uri"})
            if data["vote"][0].strip():
                if data["vote"][0].strip() == "+":
                    return jsonify({"message": SpotifyPlayer1.vote_track(data["uri"][0].strip(), "+")})
                elif data["vote"][0].strip() == "-":
                    return jsonify({"message": SpotifyPlayer1.vote_track(data["uri"][0].strip(), "-")})
                else:
                    return jsonify({"error": "invalid_vote"})
            else:
                return jsonify({"error": "missing_vote"})
        except (KeyError, TypeError) as error:
            if "uri" in str(error):
                return jsonify({"error": "missing_uri"})
            else:
                return jsonify({"error": "missing_vote"})

    @app.route("/play_track", methods=["PUT"])
    def play_track():
        data = request.form.to_dict(flat=False)
        try:
            if data["uri"][0].strip():
                SpotifyPlayer1.play_track(data["uri"][0].strip())
        except KeyError:
            return jsonify({"error": "missing_uri"})
        return jsonify({"message": "successful_play"})

    @app.route("/reorder_track", methods=["PUT"])
    def reorder_track():
        data = request.form.to_dict(flat=False)
        try:
            if data["uri"][0].strip():
                pass
            else:
                return jsonify({"error": "missing_uri"})
            if data["position"][0].strip():
                SpotifyPlayer1.update_playlist_items()
                return jsonify({"message": SpotifyPlayer1.reorder_track(data["uri"][0].strip(),
                                                                        data["position"][0].strip())})
            else:
                return jsonify({"error": "missing_position"})
        except KeyError as error:
            if "uri" in str(error):
                return jsonify({"error": "missing_uri"})
            else:
                return jsonify({"error": "missing_position"})

    @app.route("/resume", methods=["PUT"])
    def resume():
        _resume = SpotifyPlayer1.resume()
        if _resume is None:
            return jsonify({"message": "resume_successful"})
        elif "Restriction" in _resume:
            return jsonify({"message": "resume_failed"})
        elif "No active" in _resume or "Device not found" in _resume:
            return jsonify({"error": "no_active_device"})

    @app.route("/pause", methods=["PUT"])
    def pause():
        _pause = SpotifyPlayer1.pause()
        if _pause is None:
            return jsonify({"message": "pause_successful"})
        elif "Restriction" in _pause:
            return jsonify({"message": "pause_failed"})
        elif "No active" in _pause or "Device not found" in _pause:
            return jsonify({"error": "no_active_device"})

    @app.route("/set_volume", methods=["PUT"])
    def volume():
        data = request.form.to_dict(flat=False)
        try:
            _volume = data["volume"][0]
            if int(_volume) < 0 or int(_volume) > 100:
                return jsonify({"error": "valid_volume_range_1_-_100"})
            response = SpotifyPlayer1.set_volume(volume=_volume)
            if response == "SUCCESS":
                return jsonify({"message": "volume_" + _volume})
            elif "VOLUME_CONTROL_DISALLOW" in response:
                return jsonify({"error": "volume_control_not_allowed"})
        except KeyError:
            return jsonify({"error": "missing_volume"})

    @app.route("/enable_repeat", methods=["PUT"])
    def enable_repeat():
        response = SpotifyPlayer1.enable_repeat()
        if response is None:
            return jsonify({"message": "repeat_enabled"})
        elif response == "device_not_found":
            return jsonify({"error": "device_not_found"})

    @app.route("/disable_repeat", methods=["PUT"])
    def disable_repeat():
        response = SpotifyPlayer1.disable_repeat()
        if response is None:
            return jsonify({"message": "repeat_disabled"})
        elif response == "device_not_found":
            return jsonify({"error": "device_not_found"})

    @app.route("/get_explicit", methods=["GET"])
    def get_explicit():
        return jsonify({"message": "explicit_" + str(SpotifyPlayer1.get_explicit()).lower()})

    @app.route("/set_explicit", methods=["PUT"])
    def set_explicit():
        data = request.form.to_dict(flat=False)
        try:
            explicit = data["explicit"][0].strip()
            if explicit:
                if explicit.upper() in ["TRUE"]:
                    SpotifyPlayer1.set_explicit(True)
                    return jsonify({"message": "explicit_true"})
                elif explicit.upper() in ["FALSE"]:
                    SpotifyPlayer1.set_explicit(False)
                    return jsonify({"message": "explicit_false"})
                else:
                    return jsonify({"error": "invalid_data_type"})
        except KeyError:
            return jsonify({"error": "missing_explicit"})

    @app.route("/get_playing_state", methods=["GET"])
    def get_playing_state():
        return jsonify({"playing": SpotifyPlayer1.get_playing_state()})

    @app.route("/search", methods=["GET"])
    def search():
        data = request.form.to_dict(flat=False)
        try:
            if data["song_name"][0].strip():
                return jsonify(SpotifyPlayer1.search(data["song_name"][0].strip()))
            else:
                return jsonify({"error": "missing_song_name"})
        except KeyError:
            return jsonify({"error": "missing_song_name"})

    SpotifyPlayer1.disable_repeat()
    # Logic for sending the next song to Spotify
    SpotifyPlayer1.set_current_user_id()
    existing_playlist = False
    for playlist in SpotifyPlayer1.get_playlists()["items"]:
        if playlist["name"] == "NextUp":
            SpotifyPlayer1.playlist_id = playlist["id"]
            SpotifyPlayer1.set_playlist_uri(playlist["uri"])
            SpotifyPlayer1.update_playlist_items()
            existing_playlist = True
            break
    if existing_playlist is False:
        SpotifyPlayer1.create_playlist("NextUp")
        for playlist in SpotifyPlayer1.get_playlists()["items"]:
            if playlist["name"] == "NextUp":
                SpotifyPlayer1.playlist_id = playlist["id"]
                SpotifyPlayer1.set_playlist_uri(playlist["uri"])
                SpotifyPlayer1.set_playlist_cover()
                SpotifyPlayer1.update_playlist_items()
                break
    SpotifyPlayer1.remove_playlist_track("spotify:track:3yBlJtq86wROQpHi1goEKT")
    SpotifyPlayer1.remove_playlist_track("spotify:track:7rnVWqXzpDKnGWxEejZCWA")
    SpotifyPlayer1.remove_playlist_track("spotify:track:6UWQ9q6gNZC8AQh3otkUFa")
    SpotifyPlayer1.remove_playlist_track("spotify:track:6XYLpATwi1mOfFEua11wzJ")
    SpotifyPlayer1.add_playlist_track("spotify:track:7rnVWqXzpDKnGWxEejZCWA")
    SpotifyPlayer1.add_playlist_track("spotify:track:6UWQ9q6gNZC8AQh3otkUFa")
    SpotifyPlayer1.add_playlist_track("spotify:track:6XYLpATwi1mOfFEua11wzJ")
    SpotifyPlayer1.start_playlist()
