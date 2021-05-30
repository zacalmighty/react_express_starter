from pyngrok import ngrok

# HolePuncher - allows users to connect from the Internet


class HolePuncher:
    # Default Constructor
    def __init__(self):
        # Active Tunnel Information
        self.tunnel = ""
        # Sub-Domain for the tunnel
        self.connect_code = ""

    # Start Tunnel
    def punch(self):
        self.tunnel = ngrok.connect(3000, "http").__dict__["public_url"]
        self.connect_code = self.tunnel.split("http://")[1].split(".ngrok")[0]

    # Return Tunnel Information
    def get_tunnel(self):
        return self.tunnel

    # Return Connect Code
    def get_connect_code(self):
        return self.connect_code



