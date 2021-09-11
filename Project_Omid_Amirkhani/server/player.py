import uuid
import json
import socket


class Player:

    def __init__(self, addr, udp_port):

        self.identifier = str(uuid.uuid4())
        self.addr = addr
        self.udp_addr = (addr[0], int(udp_port))
        self.login_status = False
        self.user_id = None
        self.point = None
        self.fname = None
        self.lname = None
        self.city = None
        self.state = None
        self.color = None
        self.score = None

    def __eq__(self, other):
        if self.user_id:
            if other.user_id:
                return self.user_id == other.user_id
        return self.identifier == other.identifier

    def send_tcp(self, success, data, sock):

        success_string = "False"
        if success:
            success_string = "True"
        message = json.dumps({"success": success_string, "message": data})
        sock.send(message.encode())
        # print('sent')

    def send_udp(self, player_identifier, message, user_id=None):

        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        if user_id:
            sock.sendto(json.dumps({player_identifier: [user_id, message]}).encode(), self.udp_addr)

        else:
            sock.sendto(json.dumps({player_identifier: message}).encode(), self.udp_addr)
