class NextUp:
    # Default Constructor
    def __init__(self):
        self.queue = []                 # List of songs suggested by party member
        self.queue_max = 10             # Maximum number of songs in the queue.
        self.current_song = {}          #
        self.next_song = {"uri": ""}    #
        self.songs_removed = []         #
        self.song_banned = []           # List of songs that have been banned
        self.ban_threshold = 3          # Number of times a song is removed from the queue before it is banned
        self.explicit = True            # Determines if explicit songs can be played
        self.party_members = []         # List of party members
        self.party_code = ""            # Party Connect Code

    # Song
    def get_queue(self):
        return self.queue

    def clear_queue(self):
        self.queue.clear()

    def get_queue_max(self):
        return self.queue_max

    def set_queue_max(self, queue_max):
        self.queue_max = queue_max

    def get_current_song(self):
        return self.current_song

    def set_current_song(self, song_name):
        self.current_song = song_name

    def get_next_song(self):
        return self.next_song

    def set_next_song(self, song_name):
        self.next_song = song_name

    def get_song_ban(self):
        return self.song_banned

    def get_ban_threshold(self):
        return self.ban_threshold

    def set_ban_threshold(self, ban_threshold):
        self.ban_threshold = ban_threshold

    def get_explicit(self):
        return self.explicit

    def set_explicit(self, _explicit):
        self.explicit = _explicit

    def add_song(self, uri, name, artist, album):
        if len(self.queue) != self.queue_max:
            if uri not in self.song_banned:
                existing_song = False
                for song in self.queue:
                    if song["uri"] == uri:
                        existing_song = True
                        break
                if (existing_song is False) and (uri != self.next_song["uri"]) and (uri != self.current_song["uri"]):
                    new_song = {"uri": uri,
                                "name": name,
                                "artist": artist,
                                "album": album,
                                "remove_votes": 0,
                                "bump_votes": 0}
                    removed = False
                    for song in self.songs_removed:
                        if song["uri"] == song["uri"]:
                            removed = True
                            new_song["times_removed"] = song["times_removed"]
                            break
                    if removed is False:
                        new_song["times_removed"] = 0
                    self.queue.append(new_song)
                    return "SUCCESS"
                else:
                    return "IN QUEUE"
            else:
                return "BANNED"
        else:
            return "MAX REACHED"

    def bump_song(self, song_number):
        if song_number != 1:
            self.queue[song_number - 1], self.queue[song_number - 2] \
                = self.queue[song_number - 2], self.queue[song_number - 1]

    def remove_song(self, _song):
        for song in self.queue:
            if song == _song:
                self.queue.remove(song)
                break
        for song in self.songs_removed:
            if song["times_removed"] == self.ban_threshold:
                self.song_banned.append(song["uri"])
                self.songs_removed.remove(song)

    def remove_vote_song(self, song_number):
        self.queue[int(song_number) - 1]["remove_votes"] += 1

    def undo_remove_vote_song(self, song_number):
        self.queue[int(song_number) - 1]["remove_votes"] -= 1
        if self.queue[int(song_number) - 1]["remove_votes"] < 0:
            self.queue[int(song_number) - 1]["remove_votes"] = 0

    # Party
    def get_party_members(self):
        return self.party_members

    def get_party_code(self):
        return self.party_code
