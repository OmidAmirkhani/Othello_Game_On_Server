import json
import threading
import socket


class Client:

    def __init__(self,
                 server_host,
                 server_port_tcp=1234,
                 server_port_udp=1234,
                 client_port_udp=1235,
                 qt_signal=None):

        self.identifier = None
        self.server_message = []
        self.room_id = None
        self.client_udp = ("0.0.0.0", client_port_udp)
        self.lock = threading.Lock()
        self.server_listener = SocketThread(self.client_udp,
                                            self,
                                            self.lock,
                                            pyqtsignal=qt_signal)
        self.server_listener.start()
        self.server_udp = (server_host, server_port_udp)
        self.server_tcp = (server_host, server_port_tcp)

        self.qt_signal = qt_signal

        self.preregister()

    def create_room(self, room_name=None):

        message = json.dumps({"action": "create", "payload": room_name, "identifier": self.identifier})
        self.sock_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock_tcp.connect(self.server_tcp)
        self.sock_tcp.send(message.encode())
        data = self.sock_tcp.recv(1024)
        self.sock_tcp.close()
        result, message = self.parse_data(data)
        self.room_id = message
        return result, message

    def join_room(self, room_id):

        self.room_id = room_id
        message = json.dumps({"action": "join", "payload": room_id, "identifier": self.identifier})
        self.sock_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock_tcp.connect(self.server_tcp)
        self.sock_tcp.send(message.encode())
        data = self.sock_tcp.recv(1024)
        self.sock_tcp.close()
        result, message = self.parse_data(data)
        self.room_id = message
        return result, message

    def autojoin(self):

        message = json.dumps({"action": "autojoin", "identifier": self.identifier})
        self.sock_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock_tcp.connect(self.server_tcp)
        self.sock_tcp.send(message.encode())
        data = self.sock_tcp.recv(1024)
        self.sock_tcp.close()
        result, message = self.parse_data(data)
        self.room_id = message

    def leave_room(self):

        message = json.dumps({
            "action": "leave_room",
            "room_id": self.room_id,
            "identifier": self.identifier
        })
        self.sock_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock_tcp.connect(self.server_tcp)
        self.sock_tcp.send(message.encode())
        data = self.sock_tcp.recv(1024)
        self.sock_tcp.close()
        result, message = self.parse_data(data)

    def leave(self):

        message = json.dumps({
            "action": "leave",
            "identifier": self.identifier
        })
        self.sock_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock_tcp.connect(self.server_tcp)
        self.sock_tcp.send(message.encode())
        self.server_listener.stop()
        # self.server_listener.join(0.2)
        # print('??')
        # data = self.sock_tcp.recv(1024)
        # self.sock_tcp.close()
        # result, message = self.parse_data(data)

    def get_rooms(self):

        message = json.dumps({"action": "get_rooms", "identifier": self.identifier})
        self.sock_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock_tcp.connect(self.server_tcp)
        self.sock_tcp.send(message.encode())
        data = self.sock_tcp.recv(1024)
        self.sock_tcp.close()
        result, message = self.parse_data(data)
        return result, message

    def join_request(self, room_id):
        message = json.dumps({
            "action": "join_request",
            "room_id": room_id,
            "identifier": self.identifier
        })
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.sendto(message.encode(), self.server_udp)

    def send(self, message):
        print(message, 'to sendddd')

        message = json.dumps({
            "action": "send",
            "payload": {"message": message},
            "room_id": self.room_id,
            "identifier": self.identifier
        })
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.sendto(message.encode(), self.server_udp)

    def sendto(self, recipients, message):

        message = json.dumps({
            "action": "sendto",
            "payload": {
                "recipients": recipients,
                "message": message
            },
            "room_id": self.room_id,
            "identifier": self.identifier
        })
        # print(recipients, message, self.room_id, self.identifier)
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.sendto(message.encode(), self.server_udp)

    def preregister(self):

        message = json.dumps({
            "action": "preregister",
            "payload": self.client_udp[1]
        })
        self.sock_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock_tcp.connect(self.server_tcp)
        self.sock_tcp.send(message.encode())
        data = self.sock_tcp.recv(1024)
        self.sock_tcp.close()
        result, message = self.parse_data(data)
        self.identifier = message

    def register(self, uid, pwd, fname, lname, city, state):

        message = json.dumps({
            "action": "register",
            "payload": {'uid': uid,
                        'password': pwd,
                        'firstname': fname,
                        'lastname': lname,
                        'city': city,
                        'state': state,
                        },
            "identifier": self.identifier,
        })
        self.sock_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock_tcp.connect(self.server_tcp)
        self.sock_tcp.send(message.encode())
        data = self.sock_tcp.recv(1024)
        self.sock_tcp.close()
        result, message = self.parse_data(data)
        return result, message

    def login(self, username, password):

        message = json.dumps({
            "action": "login",
            "payload": {'username': username, 'password': password},
            "identifier": self.identifier,
        })
        self.sock_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock_tcp.connect(self.server_tcp)
        self.sock_tcp.send(message.encode())
        data = self.sock_tcp.recv(1024)
        self.sock_tcp.close()
        result, message = self.parse_data(data)
        return result, message

    def logout(self):

        message = json.dumps({
            "action": "logout",
            "identifier": self.identifier,
        })
        self.sock_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock_tcp.connect(self.server_tcp)
        self.sock_tcp.send(message.encode())
        data = self.sock_tcp.recv(1024)
        self.sock_tcp.close()
        result, message = self.parse_data(data)
        return result, message
    
    def my_info(self):

        message = json.dumps({
            'action': 'my_info',
            'identifier': self.identifier,
        })
        self.sock_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock_tcp.connect(self.server_tcp)
        self.sock_tcp.send(message.encode())
        data = self.sock_tcp.recv(1024)
        self.sock_tcp.close()
        result, message = self.parse_data(data)
        return result, message

    def get_room(self, room_id):
        message = json.dumps({
            'action': 'get_room',
            'identifier': self.identifier,
            'payload': room_id,
        })
        self.sock_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock_tcp.connect(self.server_tcp)
        self.sock_tcp.send(message.encode())
        data = self.sock_tcp.recv(1024)
        self.sock_tcp.close()
        result, message = self.parse_data(data)
        return result, message

    def put(self, x, y):
        message = json.dumps({
            'action': 'put',
            'identifier': self.identifier,
            'payload': [x, y],
            'room_id': self.room_id,
        })
        self.sock_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock_tcp.connect(self.server_tcp)
        self.sock_tcp.send(message.encode())
        data = self.sock_tcp.recv(1024)
        self.sock_tcp.close()
        result, message = self.parse_data(data)
        return result, message
    

    
    def top_10(self):
        """"""
        message = json.dumps({
            'action': 'top_10',
            'identifier': self.identifier,
        })
        self.sock_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock_tcp.connect(self.server_tcp)
        self.sock_tcp.send(message.encode())
        data = self.sock_tcp.recv(1024)
        self.sock_tcp.close()
        result, message = self.parse_data(data)
        return result, message

    def parse_data(self, data):

        try:
            data = json.loads(data)
            if data['success'] == "True":
                return True, data['message']
            else:
                return False, data['message']
        except ValueError:
            print(data)

    def get_messages(self):

        message = self.server_message
        self.server_message = []
        return set(message)


class SocketThread(threading.Thread):
    def __init__(self, addr, client, lock=None, pyqtsignal=None):

        threading.Thread.__init__(self)
        self.client = client
        self.lock = lock
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(addr)
        self.pyqtsignal = pyqtsignal
        self.is_listening = True

    def run(self):

        while self.is_listening:
            data, addr = self.sock.recvfrom(1024)
            self.lock.acquire()
            try:
                self.client.server_message.append(data)
                # print(data)
                if data:
                    if self.pyqtsignal:
                        self.pyqtsignal.sig.emit(json.loads(data))
                else:
                    pass
            finally:
                self.lock.release()

    def stop(self):

        self.is_listening = False
        try:
            self.sock.shutdown(socket.SOCK_DGRAM)
        except Exception as e:
            print(e.args)

