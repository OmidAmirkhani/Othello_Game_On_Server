import uuid
import mysql.connector
from player import Player
import reversi


class Rooms:

    def __init__(self, capacity=2):

        self.rooms = {}
        self.players = {}
        self.room_capacity = capacity
        self.db_connection = mysql.connector.connect(host="localhost", user="omid", password="omid")
        self.db_cursor = self.db_connection.cursor(buffered=True)  # buffered = True would

    def preregister(self, addr, udp_port):

        player = None
        for preregistered_player in self.players.values():
            if preregistered_player.addr == addr:
                player = preregistered_player
                player.udp_addr((addr[0], udp_port))
                break

        if player is None:
            player = Player(addr, udp_port)
            self.players[player.identifier] = player

        return player

    def logout(self, player_identifier):
        player = self.players[player_identifier]
        player.login_status = False
        uid = player.user_id
        player.user_id = None
        player.city = None
        player.state = None
        player.point = None
        player.fname = None
        player.lname = None
        return uid

    def login_from_database(self, player_identifier, uid, pwd):
        if not self.db_connection.is_connected():
            self.db_connection.connect()  
        self.db_cursor.execute("CREATE DATABASE IF NOT EXISTS User")  
        self.db_cursor.execute("use User")  
        self.db_cursor.execute(
            "create table if not exists USER(uid VARCHAR(30) NOT NULL PRIMARY KEY,password VARCHAR(30),fname VARCHAR("
            "30),lname VARCHAR(30),city VARCHAR(20),state VARCHAR(30),point VARCHAR(10))")
        self.db_connection.commit()

        query = "SELECT * FROM USER WHERE uid = '" + uid + "' AND password = '" + pwd + "'"
        self.db_cursor.execute(query)
        rowcount = self.db_cursor.rowcount
        # print(rowcount)
        # print(self.db_cursor.fetchall())
        if self.db_cursor.rowcount == 1:
            player = self.players[player_identifier]
            player.login_status = True
            player.user_id = uid
            record = self.db_cursor.fetchall()[0]
            player.point = float(record[-1])
            player.fname = record[2]
            player.lname = record[3]
            player.city = record[4]
            player.state = record[5]
            return uid
        else:
            return False

    def register_to_database(self, player_identifier, uid, pwd, fname, lname, city, state):
        if not self.db_connection.is_connected():
            self.db_connection.connect()
        self.db_cursor.execute("CREATE DATABASE IF NOT EXISTS User")
        self.db_cursor.execute("use User")
        self.db_cursor.execute(
            "Create table if not exists USER(uid VARCHAR(30) NOT NULL PRIMARY KEY,password VARCHAR(30),fname VARCHAR("
            "30),lname VARCHAR(30),city VARCHAR(20),state VARCHAR(30),point VARCHAR(10))")
        self.db_connection.commit()
        self.db_cursor.execute("use User")  
        query = "INSERT INTO USER(uid,password,fname,lname,city,state,point) VALUES ('%s','%s','%s','%s','%s'," \
                "'%s','%s')" % (
            uid, pwd, fname, lname, city, state, '0')
        try:
            self.db_cursor.execute(query)
            self.db_connection.commit()
            # player = self.players[player_identifier]
            # player.login_status = True
            # player.user_id = uid
            return uid
        except Exception as e:
            print(e)
        self.db_connection.rollback()
        self.db_connection.close()
        return False

    def get_top_from_database(self, n=10):
        if not self.db_connection.is_connected():
            self.db_connection.connect()  
        self.db_cursor.execute("use User")
        query = "SELECT uid, point FROM USER ORDER BY point*1 DESC LIMIT " + str(n)
        self.db_cursor.execute(query)
        tops = self.db_cursor.fetchall()
        r = []
        for p in tops:
            r.append((p[1], p[0]))
        self.db_connection.rollback()
        self.db_connection.close()
        return r

    def save_to_database(self, room_id):
        room = self.rooms[room_id]
        if not self.db_connection.is_connected():
            self.db_connection.connect()
        self.db_cursor.execute("use User")
        query = "UPDATE USER SET point = %s where uid = %s"

        _, sb, sc = room.game.chessCount
        if sb > sc:
            b_multiplier = 1.5
            w_multiplier = 0.4
        elif sb < sc:
            b_multiplier = 0.4
            w_multiplier = 1.5
        else:
            b_multiplier = 1
            w_multiplier = 1

        try:
            for p in room.players:
                if p.color == 'black':
                    p.point += p.score * b_multiplier
                else:
                    p.point += p.score * w_multiplier
                p.point = round(p.point, 2)
                input_data = (p.point, p.user_id)
                self.db_cursor.execute(query, input_data)
                p.score = 0
            self.db_connection.commit()
        except Exception as e:
            print(e)
        self.db_connection.rollback()
        self.db_connection.close()

    def join(self, player_identifier, room_id=None):

        if player_identifier not in self.players:
            raise ClientNotRegistered()

        player = self.players[player_identifier]

        if room_id is None:
            for room_id in self.rooms.keys():
                if not self.rooms[room_id].is_full():
                    self.rooms[room_id].players.append(player)
                    player.color = 'black' if self.rooms[room_id].players.index(player) + 1 == 1 else 'white'
                    # print(player.color)
                    return room_id
                    break
            room_id = self.create()
            self.join(player_identifier, room_id)
            return room_id

        elif room_id in self.rooms:
            if not self.rooms[room_id].is_full():
                self.rooms[room_id].players.append(player)
                player.color = 'black' if self.rooms[room_id].players.index(player) + 1 == 1 else 'white'
                # print(player.color, ' x')
                return room_id
            else:
                raise RoomFull()
        else:
            raise RoomNotFound()

    def leave_room(self, player_identifier, room_id):

        if player_identifier not in self.players:
            raise ClientNotRegistered()

        player = self.players[player_identifier]

        if room_id in self.rooms:
            self.rooms[room_id].leave(player)
            if len(self.rooms[room_id].players) == 0:
                del self.rooms[room_id]
        else:
            raise RoomNotFound()

    def leave(self, player_identifier):

        if player_identifier not in self.players:
            raise ClientNotRegistered()

        del self.players[player_identifier]
        # print(self.players)

    def create(self, room_name=None):

        identifier = str(uuid.uuid4())
        self.rooms[identifier] = Room(identifier,
                                      self.room_capacity,
                                      room_name)
        return identifier

    def remove_empty(self):

        for room_id in list(self.rooms.keys()):
            if self.rooms[room_id].is_empty():
                del self.rooms[room_id]

    def send(self, identifier, room_id, message, sock=None):

        # print(identifier, room_id, message)
        if room_id not in self.rooms:
            raise RoomNotFound()

        room = self.rooms[room_id]
        # print(room)
        # if not room.is_in_room(identifier):
        #     raise NotInRoom()

        for player in room.players:
            if player.identifier != identifier:
                player.send_udp(identifier, message, self.players[identifier].user_id)
                # print('sending to playesssss in rooom')

    def sendto(self, identifier, room_id, recipients, message, sock):

        if room_id not in self.rooms:
            raise RoomNotFound()

        room = self.rooms[room_id]
        if not room.is_in_room(identifier):
            raise NotInRoom()
   
        if isinstance(recipients, str):
            recipients = [recipients]
            
        for player_identifier in self.players:
            if self.players[player_identifier].user_id in recipients:
                self.players[player_identifier].send_udp(identifier, message, self.players[identifier].user_id)


class Room:

    def __init__(self, identifier, capacity, room_name):

        self.capacity = capacity
        self.players = []
        self.identifier = identifier
        if room_name is not None:
            self.name = room_name
        else:
            self.name = self.identifier

        self.game = reversi.Reversi()

    def join(self, player):

        if not self.is_full():
            self.players.append(player)
        else:
            raise RoomFull()

    def leave(self, player):

        if player in self.players:
            self.players.remove(player)
        else:
            raise NotInRoom()

    def is_empty(self):

        if len(self.players) == 0:
            return True
        else:
            return False

    def is_full(self):

        if len(self.players) == self.capacity:
            return True
        else:
            return False

    def is_in_room(self, player_identifier):

        in_room = False
        for player in self.players:
            if player.identifier == player_identifier:
                in_room = True
                break
        return in_room


class RoomFull(Exception):
    pass


class RoomNotFound(Exception):
    pass


class NotInRoom(Exception):
    pass


class ClientNotRegistered(Exception):
    pass
