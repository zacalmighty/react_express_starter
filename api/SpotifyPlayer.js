var url;
const ngrok = require('ngrok');
(async function() {
    url = await ngrok.connect(3000);
    console.log(url);
})();
const http = require("http");
const hostname = "127.0.0.1";
const port = 3000;
const server = http.createServer((req, res) => {
    res.statusCode = 200;
    res.setHeader("Content-type", "text/html");
    res.write(url);
    res.end("Hello World!")
});
server.listen(port, hostname, () => {
    console.log("Server started on port " + port);
});



class NextUp{
    constructor(){
        this.device_id = "";
        this.user_id = "";
        this.open_queue = true;
        this.queue = [];
        this.current_track = {};
        this.next_track = {};
        this.track_votes = [];
        this.tracks_removed = [];
        this.tracks_banned = [];
        this.ban_threshold = 3;
        this.explicit = true;
        this.party_members = [];
        this.party_code = "";
    }
    
    get_devices()
    {
        fetch("https://api.spotify.com/v1/me/player/devices", {method: 'GET'})
            .then(response => response.text())
            .then(result => console.log(result))
            .catch(error => console.log('error', error));
    }
    
    get_active_devices(){
        //
    }
    
    get_device_id(){
        return this.device_id;
    }
    
    set_device_id(_device_id){
        this.device_id = _device_id;
        return {"message": "device_id_" + this.device_id};
    }
    
    get_current_user(){
        fetch("https://api.spotify.com/v1/me", {method: 'GET'})
            .then(response => response.text())
            .then(result => console.log(result))
            .catch(error => console.log('error', error));
        
    }

    get_current_user_id(){
        //
    }
    
    set_current_user_id(){
        //
    }
    
    get_open_queue(){
        return this.open_queue;
    }
    
    set_open_queue(_open_queue){
        if (typeof _explicit == "boolean"){      
            this.open_queue = open_queue;
            return {"message": "open_queue_" + this.open_queue};
        }
        return {"error": "invalid_data_type"};
    }
    
    create_playlist(_name){
        //
    }
    
    get_queue(){
        return this.queue;
    }
    
    set_playlist_id(_playlist_id){
        this.playlist_id = _playlist_id;
        return {"message": "playlist_id_" + this.playlist_id.toString()};
    }
    
    set_playlist_uri(_playlist_uri){
        this.playlist_uri = _playlist_uri;
    }
    
    add_queue_track(uri){
        if (!this.tracks_banned.includes(uri))
        {
            var track;
            for (track in this.queue){
                if (this.queue[track]["track"]["uri"] == uri){
                    return {"error": "track_in_queue"};
                }
            }
            this.queue.push({"track": {"uri": uri}});
            return {"message": "successful_add"};
        }
        else {
            return {"error": "track_banned"};
        }
    }
    
    remove_queue_track(uri){
        var track;
        for (track in this.queue){
            if (this.queue[track]["track"]["uri"] == uri){
                this.queue.splice(track, 1);
                return {"message": "successful_removal"};
            }
        }
        return {"error": "track_not_in_queue"}
    }
    
    vote_track(uri, vote){
        var track;
        for (track in this.queue){
            if (this.queue[track]["track"]["uri"] == uri){
                for (track in this.track_votes){
                    if (this.track_votes[track]["track"]["uri"] == uri){
                        if (vote == "+"){
                            this.track_votes[track]["track"]["votes"] += 1;
                            return {"message": "successful_upvote"};
                        }
                        else if (vote == "-"){
                            this.track_votes[track]["track"]["votes"] -= 1;
                            return {"message": "successful_downvote"};
                        }
                        else {
                            return {"error": "invalid_vote"};
                        }
                    }
                }
                if (vote == "+"){
                    this.track_votes.push({"track": {"uri": uri, "votes": 1}});
                    return {"message": "successful_upvote"};
                }
                else if (vote == "-"){
                    this.track_votes.push({"track": {"uri": uri, "votes": -1}});
                    return {"message": "successful_downvote"};
                }
                else {
                    return {"error": "invalid_vote"};
                }
            }
        }
        return {"error": "track_not_in_queue"};
    }
    
    get_all_track_votes(){
        return this.track_votes;
    }
    
    get_track_votes(uri){
        var track;
        for (track in this.track_votes){
            if (this.track_votes[track]["track"]["uri"] == uri){
                return this.track_votes[track];
            }
        }
        return {"error": "track_has_not_been_voted_on"};
    }
    
    get_explicit(){
        return this.explicit;
    }
    
    set_explicit(_explicit){
        if (typeof _explicit == "boolean"){
            this.explicit = _explicit;
            return {"message": "explicit_" + this.explicit.toString()};
        }
        return {"error": "invalid_data_type"};
        
    }
    
    search(_name){
    }
}