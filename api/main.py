from flask import Flask, jsonify, request, abort
from flask_cors import CORS
import threading
import SpotifyPlayer
import HolePuncher
import NextUp
import time
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
    print(HolePuncher1.get_connect_code())
    connect_code_qr = qrcode.make(HolePuncher1.tunnel)
    connect_code_qr.save("connect_code.png")

    SpotifyPlayer1 = SpotifyPlayer.SpotifyPlayer()
    NextUp1 = NextUp.NextUp()

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
            device_id = data["device_id"][0]
            if SpotifyPlayer1.set_device_id(_device_id=device_id) == "SUCCESS":
                return jsonify(["DEVICE SELECTION SUCCESS"])
            else:
                return jsonify(["DEVICE SELECTION FAILED"])
        except KeyError:
            return abort(404, description="No Device ID Requested")

    # USER
    @app.route("/get_current_user", methods=["GET"])
    def get_current_user():
        return SpotifyPlayer1.get_current_user()

    @app.route("/get_current_user_id", methods=["GET"])
    def get_current_user_id():
        return jsonify({"user_id": SpotifyPlayer1.get_current_user_id()})

    # QUEUE
    @app.route("/get_queue", methods=["GET"])
    def get_queue():
        return jsonify(NextUp1.get_queue())

    @app.route("/get_current_song", methods=["GET"])
    def get_current_song():
        return jsonify({"current_song": SpotifyPlayer1.get_current_song()})

    @app.route("/get_next_song", methods=["GET"])
    def get_next_song():
        return jsonify({"next_song": NextUp1.get_next_song()})

    @app.route("/add_song", methods=["PUT"])
    def add_song():
        data = request.form.to_dict(flat=False)
        try:
            if data["uri"][0].strip() == "":
                return abort(404, description="No Song URI Requested")
            uri = data["uri"][0]
        except KeyError:
            return abort(404, description="No Song URI Requested")
        try:
            if data["name"][0].strip() == "":
                return abort(404, description="No Song Name Requested")
            name = data["name"][0]
        except KeyError:
            return abort(404, description="No Song Name Requested")
        try:
            if data["artist"][0].strip() == "":
                return abort(404, description="No Song Artist Requested")
            artist = data["artist"][0]
        except KeyError:
            return abort(404, description="No Song Artist Requested")
        try:
            if data["album"][0].strip() == "":
                return abort(404, description="No Song Album Requested")
            album = data["album"][0]
        except KeyError:
            return abort(404, description="No Song Album Requested")
        song_request = NextUp1.add_song(uri, name, artist, album)
        if song_request == "SUCCESS":
            return jsonify(["SUCCESSFUL ADD"])
        elif song_request == "IN QUEUE":
            return jsonify(["SONG ALREADY IN QUEUE"])
        elif song_request == "BANNED":
            return jsonify(["SONG HAS BEEN BANNED FROM THE QUEUE"])
        elif song_request == "MAX REACHED":
            return jsonify(["QUEUE HAS REACHED MAXIMUM CAPACITY"])

    @app.route("/remove_vote_song", methods=["PUT"])
    def remove_vote_song():
        data = request.form.to_dict(flat=False)
        try:
            if data["song_number"][0].strip() == "":
                return abort(404, description="No Song Number")
            song_number = data["song_number"][0]
            try:
                if int(song_number) == 0:
                    raise IndexError
                NextUp1.remove_vote_song(song_number)
            except IndexError:
                return abort(400, description="Invalid Song Number")
            return jsonify(["SUCCESSFUL VOTE"])
        except KeyError:
            return abort(404, description="No Song Number")
        pass

    @app.route("/undo_remove_vote_song", methods=["PUT"])
    def undo_remove_vote_song():
        data = request.form.to_dict(flat=False)
        try:
            if data["song_number"][0].strip() == "":
                return abort(404, description="No Song Number")
            song_number = data["song_number"][0]
            try:
                if int(song_number) == 0:
                    raise IndexError
                NextUp1.undo_remove_vote_song(song_number)
            except IndexError:
                return abort(400, description="Invalid Song Number")
            return jsonify(["SUCCESSFUL VOTE"])
        except KeyError:
            return abort(404, description="No SongNumber")
        pass

    @app.route("/play_song", methods=["PUT"])
    def play_song():
        data = request.form.to_dict(flat=False)
        try:
            if data["uri"][0].strip() == "":
                return abort(404, description="No Song URI")
            SpotifyPlayer1.play_song(data["uri"][0].strip())
        except KeyError:
            return abort(404, description="No Song URI")
        return jsonify("SUCCESSFUL PLAY")

    @app.route("/resume", methods=["PUT"])
    def resume():
        _resume = SpotifyPlayer1.resume()
        if _resume is None or "Restriction" in _resume:
            return jsonify("SUCCESSFUL RESUME")
        elif "No active" in _resume:
            return jsonify(["No active device found"])

    @app.route("/pause", methods=["PUT"])
    def pause():
        _pause = SpotifyPlayer1.pause()
        if _pause is None or "Restriction" in _pause:
            return jsonify("SUCCESSFUL PAUSE")
        elif "No active" in _pause:
            return jsonify(["No active device found"])

    @app.route("/set_volume", methods=["PUT"])
    def volume():
        data = request.form.to_dict(flat=False)
        try:
            _volume = data["volume"][0]
            if int(_volume) < 0 or int(_volume) > 100:
                return jsonify("VOLUME CAN ONLY BE BETWEEN 1 - 100")
            response = SpotifyPlayer1.set_volume(volume=_volume)
            if response == "SUCCESS":
                return jsonify(["VOLUME SET TO " + _volume.upper()])
            elif "VOLUME_CONTROL_DISALLOW" in response:
                return jsonify(["CANNOT CONTROL VOLUME ON THIS DEVICE"])
        except KeyError:
            return abort(404, description="No Device ID Requested")

    @app.route("/enable_repeat", methods=["PUT"])
    def enable_repeat():
        pass

    @app.route("/disable_repeat", methods=["PUT"])
    def disable_repeat():
        pass

    @app.route("/get_explicit", methods=["GET"])
    def get_explicit():
        return jsonify({"explicit": NextUp1.get_explicit()})

    @app.route("/set_explicit", methods=["PUT"])
    def set_explicit():
        data = request.form.to_dict(flat=False)
        try:
            explicit = data["explicit"][0].strip()
            if explicit == "":
                return abort(404, description="No Explicit Type")
            elif explicit.upper() not in ["TRUE", "FALSE"]:
                return abort(400, description="Invalid Data Type")
            else:
                NextUp1.set_explicit(bool(explicit))
                return jsonify("EXPLICIT SET TO " + str(explicit).upper())
        except KeyError:
            return abort(404, description="No Explicit Requested")

    @app.route("/get_state", methods=["GET"])
    def get_state():
        return jsonify({"playing": SpotifyPlayer1.get_state()})

    @app.route("/search", methods=["GET"])
    def search():
        data = request.form.to_dict(flat=False)
        song_name = data["song_name"][0].strip()
        try:
            if song_name == "":
                return abort(404, description="No Song Requested")
            return jsonify(SpotifyPlayer1.search(song_name))
        except KeyError:
            return abort(404, description="No Song Requested")

    SpotifyPlayer1.disable_repeat()
    # Logic for sending the next song to Spotify
    # Set the Current Song on Next Up from the Current Song from Spotify
    first_run = True
    while True:
        try:
            NextUp1.set_current_song(SpotifyPlayer1.get_current_song())
            break
        except TypeError:
            pass
    # Add Song via API Endpoint PUT /add_song
    while True:
        if first_run is True:
            try:
                NextUp1.set_next_song(NextUp1.get_queue()[0])
                SpotifyPlayer1.add_to_queue(NextUp1.get_next_song()["uri"])
                NextUp1.remove_song(NextUp1.get_next_song())
                first_run = False
            except IndexError:
                pass
        else:
            if SpotifyPlayer1.get_current_song()['uri'] == NextUp1.get_next_song()["uri"]:
                # Set the Next Song as the first song in the NextUp queue
                try:
                    NextUp1.set_next_song(NextUp1.get_queue()[0])
                except IndexError:
                    # Insert Algorithm for Next Song
                    pass

                # Add the Next Song from NextUp to the Spotify Queue
                try:
                    SpotifyPlayer1.add_to_queue(NextUp1.get_next_song()["uri"])
                except KeyError:
                    pass

                # Remove the Song from the NextUp Queue
                NextUp1.remove_song(NextUp1.get_next_song())
        time.sleep(2)
