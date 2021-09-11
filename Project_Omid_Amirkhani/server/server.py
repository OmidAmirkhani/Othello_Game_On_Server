#!/usr/bin/python

import argparse
import socket
import json
import time
from threading import Thread, Lock
from rooms import Rooms, RoomNotFound, NotInRoom, RoomFull


def main_loop(tcp_port, udp_port, rooms):

    lock = Lock()
    udp_server = UdpServer(udp_port, rooms, lock)
    tcp_server = TcpServer(tcp_port, rooms, lock)
    udp_server.start()
    tcp_server.start()
    is_running = True
    print("Simple Game Server.")
    print("--------------------------------------")
    print("list : list rooms")
    print("room #room_id : print room information")
    print("user #user_id : print user information")
    print("quit : quit server")
    print("--------------------------------------")

    while is_running:
        cmd = input("cmd >")
        if cmd == 'users':
            print('users :')
            for p in rooms.players:
                print(p)
        elif cmd == "list":
            print("Rooms :")
            for room_id, room in rooms.rooms.items():
                print("%s - %s (%d/%d)" % (room.identifier,
                                           room.name,
                                           len(room.players),
                                           room.capacity))
        elif cmd.startswith("room "):
            try:
                id = cmd[5:]
                room = rooms.rooms[id]
                print("%s - %s (%d/%d)" % (room.identifier,
                                           room.name,
                                           len(room.players),
                                           room.capacity))
                print("Players :")
                for player in room.players:
                    print(player.identifier)
            except:
                print("Error while getting room informations")
        elif cmd.startswith("user "):
            try:
                player = rooms.players[cmd[5:]]
                print("%s : %s:%d" % (player.identifier,
                                      player.udp_addr[0],
                                      player.udp_addr[1]))
            except:
                print("Error while getting user informations")
        elif cmd == "quit":
            print("Shutting down  server...")
            udp_server.is_listening = False
            tcp_server.is_listening = False
            is_running = False

    udp_server.join()
    tcp_server.join()


class UdpServer(Thread):
    def __init__(self, udp_port, rooms, lock):

        Thread.__init__(self)
        self.rooms = rooms
        self.lock = lock
        self.is_listening = True
        self.udp_port = int(udp_port)
        self.msg = '{"success": %(success)s, "message":"%(message)s"}'

    def run(self):

        self.sock = socket.socket(socket.AF_INET,
                                  socket.SOCK_DGRAM)
        self.sock.bind(("0.0.0.0", self.udp_port))
        self.sock.setblocking(0)
        self.sock.settimeout(5)
        while self.is_listening:
            try:
                data, address = self.sock.recvfrom(1024)
            except socket.timeout:
                continue

            try:
                data = json.loads(data)
                try:
                    identifier = data['identifier']
                except KeyError:
                    identifier = None

                try:
                    room_id = data['room_id']
                except KeyError:
                    room_id = None

                try:
                    payload = data['payload']
                except KeyError:
                    payload = None

                try:
                    action = data['action']
                except KeyError:
                    action = None

                try:
                    if room_id not in self.rooms.rooms.keys():
                        raise RoomNotFound
                    self.lock.acquire()
                    try:
                        if action == 'join_request':
                            try:
                                # print('jjjjjrrrrrrrr')
                                # print(identifier, room_id, 'erererer', self.sock)
                                self.rooms.send(identifier,
                                                room_id,
                                                'request for join',
                                                self.sock)
                            except:
                                pass
                        elif action == "send":
                            try:
                                self.rooms.send(identifier,
                                                room_id,
                                                payload['message'],
                                                self.sock)
                            except:
                                pass
                        elif action == "sendto":
                            try:
                                # print(identifier, room_id, payload)
                                self.rooms.sendto(identifier,
                                                  room_id,
                                                  payload['recipients'],
                                                  payload['message'],
                                                  self.sock)
                            except:
                                pass
                    finally:
                        self.lock.release()
                except RoomNotFound:
                    print("Room not found")

            except KeyError:
                print("Json from %s:%s is not valid" % address)
            except ValueError:
                print("Message from %s:%s is not valid json string" % address)

        self.stop()

    def stop(self):

        self.sock.close()


class TcpServer(Thread):
    def __init__(self, tcp_port, rooms, lock):

        Thread.__init__(self)
        self.lock = lock
        self.tcp_port = int(tcp_port)
        self.rooms = rooms
        self.is_listening = True
        self.msg = '{"success": "%(success)s", "message":"%(message)s"}'

    def run(self):

        self.sock = socket.socket(socket.AF_INET,
                                  socket.SOCK_STREAM)
        self.sock.bind(('0.0.0.0', self.tcp_port))
        self.sock.setblocking(0)
        self.sock.settimeout(5)
        time_reference = time.time()
        self.sock.listen(1)

        while self.is_listening:

            if time_reference + 60 < time.time():
                self.rooms.remove_empty()
                time_reference = time.time()
            try:
                conn, addr = self.sock.accept()
            except socket.timeout:
                continue

            data = conn.recv(1024)
            # print(data)
            try:
                data = json.loads(data)
                action = data['action']
                identifier = None
                try:
                    identifier = data['identifier']
                except KeyError:
                    pass 

                room_id = None
                try:
                    room_id = data['room_id']
                except KeyError:
                    pass  

                payload = None
                try:
                    payload = data['payload']
                except KeyError:
                    pass  
                self.lock.acquire()
                try:
                    self.route(conn,
                               addr,
                               action,
                               payload,
                               identifier,
                               room_id)
                finally:
                    self.lock.release()
            except KeyError:
                print("Json from %s:%s is not valid" % addr)
                conn.send("Json is not valid")
            except ValueError:
                print("Message from %s:%s is not valid json string" % addr)
                conn.send("Message is not a valid json string")

            conn.close()

        self.stop()

    def route(self,
              sock,
              addr,
              action,
              payload,
              identifier=None,
              room_id=None):


        if action == "preregister":
            client = self.rooms.preregister(addr, int(payload))
            client.send_tcp(True, client.identifier, sock)
            return 0

        if identifier is not None:
            if identifier not in self.rooms.players.keys():
                print("Unknown identifier %s for %s:%s" % (identifier, addr[0], addr[1]))
                sock.send(self.msg % {"success": "False", "message": "Unknown identifier"})
                return 0

            client = self.rooms.players[identifier]

            if action == 'login':
                uid = self.rooms.login_from_database(identifier, payload['username'], payload['password'])
                if uid:
                    client.send_tcp(True, f'salam {uid}', sock)
                else:
                    client.send_tcp(False, 'error on logging in', sock)
            elif action == 'register':
                uid = self.rooms.register_to_database(identifier,
                                                      payload['uid'],
                                                      payload['password'],
                                                      payload['firstname'],
                                                      payload['lastname'],
                                                      payload['city'],
                                                      payload['state'])
                if uid:
                    client.send_tcp(True, f'hi {uid}', sock)
                else:
                    client.send_tcp(False, 'error on registration', sock)
            elif action == 'logout':
                uid = self.rooms.logout(identifier)
                client.send_tcp(True, f'bye {uid}', sock)
            elif action == 'my_info':
                player = self.rooms.players[identifier]
                client.send_tcp(True,
                                {'fullname': player.fname + ' ' + player.lname,
                                 'point': player.point,
                                 'username': player.user_id,
                                 'address': player.state + ' ' + player.city},
                                sock)
            elif action == "join":
                try:
                    if payload not in self.rooms.rooms.keys():
                        raise RoomNotFound()
                    self.rooms.join(identifier, payload)
                    client.send_tcp(True, payload, sock)
                    # self.rooms.send(identifier, payload, 'request for join')
                except RoomNotFound:
                    client.send_tcp(False, room_id, sock)
                except RoomFull:
                    client.send_tcp(False, room_id, sock)
            elif action == "autojoin":
                room_id = self.rooms.join(identifier)
                client.send_tcp(True, room_id, sock)
            elif action == "get_rooms":
                rooms = []
                for id_room, room in self.rooms.rooms.items():
                    if not room.game.over:
                        rooms.append({"id": id_room,
                                      "name": room.name,
                                      "nb_players": len(room.players),
                                      "capacity": room.capacity})
                client.send_tcp(True, rooms, sock)
            elif action == "get_room":
                room = self.rooms.rooms[payload]
                player_number = room.players.index(self.rooms.players[identifier]) + 1
                # print(room.identifier, room.name)
                client.send_tcp(True,
                                {'id': room.identifier,
                                 'name': room.name,
                                 'players': [{'fullname': player.fname + ' ' + player.lname,
                                              'point': player.point,
                                              'username': player.user_id,
                                              'address': player.state + ' ' + player.city,
                                              'color': [player.color, room.game.current]} for player in room.players],
                                 'turn': room.game.current == player_number,
                                 'board': room.game.board},
                                sock)
            elif action == 'put':
                room = self.rooms.rooms[room_id]
                player_number = room.players.index(self.rooms.players[identifier]) + 1
                x, y = payload
                sb, sc = None, None
                if len(room.players) < 2:
                    status = 'room is waiting for player'
                elif player_number != room.game.current:
                    status = 'Not your turn'
                elif room.game.canPut(x, y, player_number):
                    room.game.put(x, y)
                    if not room.game.over:
                        room.game.skipPut()
                    sa, sb, sc = room.game.chessCount
                    status = 'ok'
                else:
                    status = 'bad move'
                # print(room.game.current, player_number)
                if room.game.over:
                    for p in room.players:
                        if p.color == 'black':
                            p.score = sb
                        else:
                            p.score = sc
                    self.rooms.save_to_database(room_id)

                client.send_tcp(True,
                                {'status': status,
                                 'board': room.game.board,
                                 'turn': room.game.current == player_number,
                                 'game_over': room.game.over,
                                 'sb': sb,
                                 'sc': sc},
                                sock)
                self.rooms.send(identifier,
                                room_id,
                                {'move': [x, y],
                                 'board': room.game.board,
                                 'turn': not room.game.current == player_number,
                                 'game_over': room.game.over,
                                 'sb': sb,
                                 'sc': sc}
                                )
            elif action == "create":
                player = self.rooms.players[identifier]
                rooms_ids = list(self.rooms.rooms.keys())
                for r in rooms_ids:
                    if self.rooms.rooms[r].name == player.user_id + '_room':
                        del self.rooms.rooms[r]

                room_identifier = self.rooms.create(payload)
                self.rooms.join(client.identifier, room_identifier)

                client.send_tcp(True, room_identifier, sock)
            elif action == 'top_10':
                # print('ttototptot')
                tops = self.rooms.get_top_from_database(10)
                client.send_tcp(True,
                                tops,
                                sock)
            elif action == 'leave':
                self.rooms.leave(identifier)
            elif action == 'leave_room':
                try:
                    if room_id not in self.rooms.rooms:
                        raise RoomNotFound()
                    self.rooms.leave_room(identifier, room_id)
                    client.send_tcp(True, room_id, sock)
                except RoomNotFound:
                    client.send_tcp(False, room_id, sock)
                except NotInRoom:
                    client.send_tcp(False, room_id, sock)
            else:
                sock.send_tcp(self.msg % {"success": "False",
                                          "message": "You must preregister"})

    def stop(self):

        self.sock.close()


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Simple game server')
    parser.add_argument('--tcpport',
                        dest='tcp_port',
                        help='Listening tcp port',
                        default="1234")
    parser.add_argument('--udpport',
                        dest='udp_port',
                        help='Listening udp port',
                        default="1234")
    parser.add_argument('--capacity',
                        dest='room_capacity',
                        help='Max players per room',
                        default="2")

    args = parser.parse_args()
    rooms = Rooms(int(args.room_capacity))
    main_loop(args.tcp_port, args.udp_port, rooms)
