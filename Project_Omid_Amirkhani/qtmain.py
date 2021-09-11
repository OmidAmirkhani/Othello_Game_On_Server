# -*- coding: utf-8 -*-
import sys

from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

import client

client1 = None
sig = None

BOARD_SIZE = 520  
GRID_SIZE = 60  
PIECE_SIZE = 45  
DOT_SIZE = 10  
IND_SIZE = 128  
IND_BOARD_SIZE = 150  

margin = (BOARD_SIZE - 8 * GRID_SIZE) // 2  
padding = (GRID_SIZE - PIECE_SIZE) // 2  
d_padding = (GRID_SIZE - DOT_SIZE) // 2  
ind_margin = (IND_BOARD_SIZE - IND_SIZE) // 2


class PaintArea(QWidget):
    

    def __init__(self, board=None):
        super(PaintArea, self).__init__()
        self.board = board
        self.dots = None
        self.spdots = None

        self.setPalette(QPalette(Qt.white))
        self.setAutoFillBackground(True)
        self.setMinimumSize(BOARD_SIZE, BOARD_SIZE)

        self.penConfig = \
            [Qt.black, 2, Qt.PenStyle(Qt.SolidLine), Qt.PenCapStyle(Qt.RoundCap), Qt.PenJoinStyle(Qt.MiterJoin)]
        self.noPen = \
            QPen(Qt.black, 2, Qt.PenStyle(Qt.NoPen), Qt.PenCapStyle(Qt.RoundCap), Qt.PenJoinStyle(Qt.MiterJoin))
        brushColorFrame = QFrame()
        brushColorFrame.setAutoFillBackground(True)
        brushColorFrame.setPalette(QPalette(Qt.white))
        self.brushConfig = Qt.white, Qt.SolidPattern
        self.update()

    def assignBoard(self, board):
        self.board = [list(i) for i in board]

    def assignDots(self, dots):
        self.dots = dots

    def assignSpecialDots(self, dots):
        self.spdots = dots

    def paintEvent(self, QPaintEvent):
 
        if self.board is None:
            raise ValueError("Cannot paint an empty board!")
        p = QPainter(self)

        self.penConfig[0] = Qt.blue
        p.setPen(QPen(*self.penConfig))
        p.setBrush(QBrush(*self.brushConfig))
        for i in range(9):
            A = QPoint(margin, margin + i * GRID_SIZE)
            B = QPoint(BOARD_SIZE - margin, margin + i * GRID_SIZE)
            p.drawLine(A, B)
            A = QPoint(margin + i * GRID_SIZE, margin)
            B = QPoint(margin + i * GRID_SIZE, BOARD_SIZE - margin)
            p.drawLine(A, B)

        self.penConfig[0] = Qt.black
        p.setPen(QPen(*self.penConfig))
        for i in range(8):
            for j in range(8):
                if self.board[i][j] == 0:
                    continue
                fillColor = [None, Qt.black, Qt.white]
                p.setBrush(QBrush(fillColor[self.board[i][j]], Qt.SolidPattern))
                p.drawEllipse(QRect(
                    margin + padding + i * GRID_SIZE, margin + padding + j * GRID_SIZE,
                    PIECE_SIZE, PIECE_SIZE))

        if self.dots is not None:
            p.setPen(self.noPen)
            p.setBrush(QBrush(Qt.blue, Qt.SolidPattern))
            for x, y in self.dots:
                p.drawEllipse(QRect(
                    margin + d_padding + x * GRID_SIZE, margin + d_padding + y * GRID_SIZE,
                    DOT_SIZE, DOT_SIZE))

        if self.spdots is not None:
            p.setPen(self.noPen)
            p.setBrush(QBrush(Qt.red, Qt.SolidPattern))
            for x, y in self.spdots:
                p.drawEllipse(QRect(
                    margin + d_padding + x * GRID_SIZE, margin + d_padding + y * GRID_SIZE,
                    DOT_SIZE, DOT_SIZE))


class LoginForm(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Login Form')
        self.resize(500, 120)

        self.reg_form = RegisterForm(self)
        self.dashboard = None  

        layout = QGridLayout()

        label_name = QLabel('<font size="4"> Username </font>')
        self.lineEdit_username = QLineEdit()
        self.lineEdit_username.setPlaceholderText('Please enter your username')
        layout.addWidget(label_name, 0, 0)
        layout.addWidget(self.lineEdit_username, 0, 1)

        label_password = QLabel('<font size="4"> Password </font>')
        self.lineEdit_password = QLineEdit()
        self.lineEdit_password.setPlaceholderText('Please enter your password')
        layout.addWidget(label_password, 1, 0)
        layout.addWidget(self.lineEdit_password, 1, 1)

        button_login = QPushButton('Login')
        button_login.clicked.connect(self.login)
        layout.addWidget(button_login, 2, 0, 1, 2)
        layout.setRowMinimumHeight(2, 75)

        register_button = QPushButton('(don\'t have account) Register')
        register_button.clicked.connect(self.redirect_to_register)
        layout.addWidget(register_button, 3, 0, 1, 2)

        self.setLayout(layout)

    def closeEvent(self, event):
        try:
            client1.leave()
            print('ok. left')
        except Exception as e:
            print('failed leave', str(e))
        event.accept()

    def redirect_to_register(self):
        self.reg_form.show()
        # self.hide()
        self.setVisible(False)
        # self.close()

    def go_to_dashboard(self):
        self.dashboard = DashboardWindow()
        self.dashboard.show()
        self.setVisible(False)

    def login(self):
        qmsg = QMessageBox()
        username = self.lineEdit_username.text()
        password = self.lineEdit_password.text()
        print(username, password)
        if username == "":
            qmsg.setText('please enter username')
            qmsg.exec_()
            return
        if password == "":
            qmsg.setText('please enter password')
            qmsg.exec_()
            return
        res, msg = client1.login(username, password)
        # print(msg)
        if res:
            qmsg.setText('login successfully')
            qmsg.exec_()
            self.go_to_dashboard()
        else:
            qmsg.setText(msg)
            qmsg.exec_()
            return


class RegisterForm(QWidget):
    def __init__(self, parent=None):
        super(RegisterForm, self).__init__()

        self.setWindowTitle('Register Form')
        self.resize(500, 220)

        self.login_form = parent

        layout = QGridLayout()

        label_firstname = QLabel('<font size="4"> Firstname </font>')
        self.lineEdit_firstname = QLineEdit()
        self.lineEdit_firstname.setPlaceholderText('Please enter your firstname')
        layout.addWidget(label_firstname, 0, 0)
        layout.addWidget(self.lineEdit_firstname, 0, 1)

        label_lastname = QLabel('<font size="4"> Lastname </font>')
        self.lineEdit_lastname = QLineEdit()
        self.lineEdit_lastname.setPlaceholderText('Please enter your lastname')
        layout.addWidget(label_lastname, 1, 0)
        layout.addWidget(self.lineEdit_lastname, 1, 1)

        label_name = QLabel('<font size="4"> Username </font>')
        self.lineEdit_username = QLineEdit()
        self.lineEdit_username.setPlaceholderText('Please enter your username')
        layout.addWidget(label_name, 2, 0)
        layout.addWidget(self.lineEdit_username, 2, 1)

        label_password = QLabel('<font size="4"> Password </font>')
        self.lineEdit_password = QLineEdit()
        self.lineEdit_password.setPlaceholderText('Please enter your password')
        layout.addWidget(label_password, 3, 0)
        layout.addWidget(self.lineEdit_password, 3, 1)

        label_city = QLabel('<font size="4"> City </font>')
        self.lineEdit_city = QLineEdit()
        self.lineEdit_city.setPlaceholderText('Please enter your city')
        layout.addWidget(label_city, 4, 0)
        layout.addWidget(self.lineEdit_city, 4, 1)

        label_state = QLabel('<font size="4"> State </font>')
        self.lineEdit_state = QLineEdit()
        self.lineEdit_state.setPlaceholderText('Please enter your state')
        layout.addWidget(label_state, 5, 0)
        layout.addWidget(self.lineEdit_state, 5, 1)

        button_register = QPushButton('Register')
        button_register.clicked.connect(self.register)
        layout.addWidget(button_register, 6, 0, 1, 2)
        layout.setRowMinimumHeight(2, 75)

        back_button = QPushButton('(have account) Back to Login')
        back_button.clicked.connect(self.back_to_login)
        layout.addWidget(back_button, 7, 0, 1, 2)

        self.setLayout(layout)

    def closeEvent(self, event):
        self.back_to_login()

    def register(self):
        qmsg = QMessageBox()
        if not client1:
            print('FFFFFFFFFFFF')
        firstname = self.lineEdit_firstname.text()
        lastname = self.lineEdit_lastname.text()
        username = self.lineEdit_username.text()
        password = self.lineEdit_password.text()
        city = self.lineEdit_city.text()
        state = self.lineEdit_state.text()
        if not firstname:
            qmsg.setText('please enter firstname')
            qmsg.exec_()
            return
        if not lastname:
            qmsg.setText('please enter lastname')
            qmsg.exec_()
            return
        if not username:
            qmsg.setText('please enter username')
            qmsg.exec_()
            return
        if not password:
            qmsg.setText('please enter password')
            qmsg.exec_()
            return
        if not city:
            qmsg.setText('please enter city')
            qmsg.exec_()
            return
        if not state:
            qmsg.setText('please enter state')
            qmsg.exec_()
            return

        res, msg = client1.register(username, password, firstname, lastname, city, state)
        # print(msg)
        if res:
            qmsg.setText('data inserted successfully')
            qmsg.exec_()
            self.back_to_login()
        else:
            qmsg.setText('data insertion failed!')
            qmsg.exec_()

    def back_to_login(self):
        self.login_form.show()
        self.close()


class DashboardWindow(QWidget):
    def __init__(self):
        super(DashboardWindow, self).__init__()

        self.setWindowTitle('Home')
        self.resize(600, 430)

        sig.sig.connect(self.on_my_signal_dict)
        self.going_to_game = False
        self.going_to_login = False

        # self.login_form = parent
        self.answer = None
        self.b = None

        layout = QGridLayout()

        res, msg = client1.my_info()
        # print(msg)
        my_info_layout = QVBoxLayout()
        self.point = msg['point']
        self.name = msg['fullname']
        self.address = msg['address']
        self.username = msg['username']
        label_point = QLabel(f'<font size="6"> my point : {round(self.point, 2)} </font>')
        my_info_layout.addWidget(label_point)
        label_name = QLabel(f'<font size="4"> my name : {self.name} </font>')
        my_info_layout.addWidget(label_name)
        label_address = QLabel(f'<font size="4"> my address : {self.address} </font>')
        my_info_layout.addWidget(label_address)
        label_username = QLabel(f'<font size="4"> my username : {self.username} </font>')
        my_info_layout.addWidget(label_username)

        res, msg = client1.top_10()

        top_layout = QVBoxLayout()
        for p in msg:
            top_p_layout = QHBoxLayout()
            top_p_layout.addWidget(QLabel(p[1]))
            top_p_layout.addWidget(QLabel(p[0]))
            top_layout.addItem(top_p_layout)

        label_username = QLabel('<font size="5" color="red"> waiting rooms : </font>')
        self.refresh_rooms_button = QPushButton('refresh rooms')
        self.refresh_rooms_button.clicked.connect(self.update_room_list)
        res, msg = client1.get_rooms()
        # print(msg)
        self.rooms_table = QTableWidget()
        self.rooms_table.setColumnCount(2)
        self.rooms_table.setRowCount(0)
        i = 0
        for r in msg:
            room_name = r['name']
            room_id = r['id']
            nb = r['nb_players']
            if nb == 1 and room_name[:-5] != self.username:
                self.rooms_table.insertRow(i)
                item_name = QTableWidgetItem(f'room {room_name}')
                self.rooms_table.setItem(i, 0, item_name)
                item_button = QPushButton('join')
                item_button.clicked.connect(lambda: self.join_room(room_id, item_button))
                self.rooms_table.setCellWidget(i, 1, item_button)
                i += 1
        if i == 0:
            self.rooms_table.insertRow(i)
            self.rooms_table.setItem(0, 0, QTableWidgetItem('empty'))
            self.rooms_table.setItem(0, 1, QTableWidgetItem('=('))

        button_create_room = QPushButton('create room')
        button_create_room.clicked.connect(self.create_room)

        button_logout = QPushButton('Logout')
        button_logout.clicked.connect(self.logout)

        layout.addWidget(QLabel('<font size="5" color="green">My Profile:</font>'), 0, 0)
        layout.addItem(my_info_layout, 1, 0, 2, 1)
        layout.addWidget(QLabel('<font size="5" color="yellow">Top 10:</font>'), 3, 0)
        layout.addItem(top_layout, 4, 0, 2, 1)

        layout.addWidget(button_create_room, 2, 1)
        layout.addWidget(button_logout, 4, 1)

        layout.addWidget(QLabel('<font size="5" color="red"> waiting rooms : </font>'), 0, 2)
        layout.addWidget(self.refresh_rooms_button, 1, 2)
        layout.addWidget(self.rooms_table, 2, 2, 4, 1)

        self.setLayout(layout)

    def closeEvent(self, event):
        print(self.going_to_game, self.going_to_login)
        if not self.going_to_game and not self.going_to_login:
            try:
                client1.logout()
                client1.leave()
                print('ok. left')
            except Exception as e:
                print('failed leave', str(e))
        event.accept()

    def update_room_list(self):
        for i in range(self.rooms_table.rowCount()):
            self.rooms_table.removeRow(0)
        res, msg = client1.get_rooms()
        i = 0
        for r in msg:
            room_name = r['name']
            room_id = r['id']
            nb = r['nb_players']
            if nb == 1 and room_name[:-5] != self.username:
                self.rooms_table.insertRow(i)
                item_name = QTableWidgetItem(f'room {room_name}')
                self.rooms_table.setItem(i, 0, item_name)
                item_button = QPushButton('join')
                item_button.clicked.connect(lambda: self.join_room(room_id, item_button))
                self.rooms_table.setCellWidget(i, 1, item_button)
                i += 1
        if i == 0:
            self.rooms_table.insertRow(i)
            self.rooms_table.setItem(0, 0, QTableWidgetItem('empty'))
            self.rooms_table.setItem(0, 1, QTableWidgetItem('=('))
        # self.rooms_layout.update()
        # self.layout().update()

    def create_room(self):
        res, msg = client1.create_room(self.username + '_room')
        self.room_id = msg
        # print(self.room_id)
        qmsg = QMessageBox()
        if res:
            qmsg.setText('you created a room. id: ' + msg)
            qmsg.exec_()
            self.going_to_game = True
            self.go_to_game_room(force=True)
        else:
            qmsg.setText('Failed!')
            qmsg.exec_()

    def join_room(self, room_id, b):
        self.b = b

        self.room_id = room_id
        qmsg = QMessageBox()
        # if msg:
        qmsg.setText('your request will send (10s)... room. id: ' + room_id)
        qmsg.exec_()
        client1.join_request(room_id)

        self.timer = 10
        self.tmr = QTimer()
        self.tmr.timeout.connect(lambda: self.go_to_game_room(False))
        self.tmr.start(1000)
        # print('aloo')

        # else:
        #     qmsg.setText('Error')
        #     qmsg.exec_()

    def go_to_game_room(self, force=False):
        if force:
            sig.sig.disconnect()
            self.going_to_game = True
            game_room = GameRoom(self.username, self)
            game_room.show()
            # self.setVisible(False)
            self.close()
            return

        if self.b:
            if self.timer != 0 and not self.answer:
                self.b.setDisabled(True)
                self.refresh_rooms_button.setDisabled(True)
                self.b.setText(str(self.timer))
                self.timer -= 1
            else:
                self.timer = 0
                self.tmr.stop()
                self.tmr.disconnect()
                self.b.setText('join')
                self.b.setEnabled(True)
                self.refresh_rooms_button.setEnabled(True)

        if self.answer:
            self.b = None
            res, msg = client1.join_room(self.room_id)
            client1.send('joined')
            if res:
                sig.sig.disconnect()
                self.going_to_game = True
                game_room = GameRoom(self.username, self)
                game_room.show()
                self.setVisible(False)
            else:
                qmsg = QMessageBox()
                qmsg.setText(msg)
                qmsg.exec_()

    def logout(self):
        res, msg = client1.logout()
        qmsg = QMessageBox()
        if res:
            qmsg.setText(msg)
            qmsg.exec_()
            self.going_to_login = True
            self.login_form = LoginForm()
            self.login_form.show()
            self.close()
        else:
            qmsg.setText('logout failed!')
            qmsg.exec_()

    @pyqtSlot(dict)
    def on_my_signal_dict(self, value):
        # print(value)
        for user_uuid in value:
            if value[user_uuid][1] == 'yes':
                self.answer = True
                # self.go_to_game_room()
            else:
                print('=(')
                # self.chat_text_browser.append(value[user_uuid][0] + ' :' + value[user_uuid][1])


class GameRoom(QWidget):
    def __init__(self, username, parent=None):
        super(GameRoom, self).__init__()

        self.setWindowTitle('Game')
        self.resize(400, 600)

        self.dashboard = parent
        self.layout = QGridLayout()

        self.username = username
        self.my_color = ''
        self.game_over = False

        self.chat_layout = QVBoxLayout()

        self.game_layout = QGridLayout()

        self.room_layout = QVBoxLayout()

        self.chat_layout.addWidget(QLabel('chat:'))
        self.chat_text_browser = QTextBrowser()
        send_message_layout = QHBoxLayout()
        self.chat_line_edit = QLineEdit()
        button_send_message = QPushButton('send')
        button_send_message.clicked.connect(self.send_message)
        send_message_layout.addWidget(self.chat_line_edit)
        send_message_layout.addWidget(button_send_message)
        self.chat_layout.addWidget(self.chat_text_browser)
        self.chat_layout.addItem(send_message_layout)

        sig.sig.connect(self.on_my_signal_dict)

        res, msg = client1.get_room(self.dashboard.room_id)
        # print(msg)
        board = msg['board']

        def boardClick(event):

            ex, ey = event.x(), event.y()
            gx, gy = (ex - margin) // GRID_SIZE, (ey - margin) // GRID_SIZE
            rx, ry = ex - margin - gx * GRID_SIZE, ey - margin - gy * GRID_SIZE
            if 0 <= gx < 8 and 0 <= gy < 8 and \
                    abs(rx - GRID_SIZE / 2) < PIECE_SIZE / 2 > abs(ry - GRID_SIZE / 2):
                self.onClickBoard((gx, gy))

        self.painter = PaintArea(board)
        self.painter.setFocusPolicy(Qt.StrongFocus)
        self.game_layout.addWidget(self.painter)
        self.painter.mouseReleaseEvent = boardClick

        self.init_room_layout(msg)

        self.layout.addItem(self.chat_layout, 0, 0)
        self.layout.addItem(self.game_layout, 0, 1)
        self.layout.addItem(self.room_layout, 0, 2)
        self.setLayout(self.layout)

    def closeEvent(self, event):
        if self.game_over:
            client1.leave_room()
            self.back_to_dashboard()
        else:
            qmsg = QMessageBox()
            qmsg.setText('Game Not Over')
            qmsg.exec_()
            event.ignore()

    def back_to_dashboard(self):
        sig.sig.disconnect()
        self.dashboard = DashboardWindow()
        self.dashboard.show()

        self.close()

    def init_room_layout(self, msg):
        self.my_turn = msg['turn']
        room_id = msg['id'][:5] + '...'
        room_name = msg['name']
        players = msg['players']
        r_layout = QVBoxLayout()
        self.turn_label = QLabel(f'Turn: {"You" if self.my_turn else "Not You"}')
        r_layout.addWidget(self.turn_label)
        r_layout.addWidget(QLabel(f'room id : {room_id}'))
        r_layout.addWidget(QLabel(f'room name : {room_name}'))

        self.room_layout.addItem(r_layout)
        player1_layout = QVBoxLayout()
        p_name = players[0]['fullname']
        p_point = players[0]['point']
        p_username = players[0]['username']
        p_address = players[0]['address']
        self.p1_color, current = players[0]['color']
        who = 'me ' if self.username == p_username else 'player name '
        self.my_color = self.p1_color if who == 'me ' else self.my_color
        self.p1_name_label = QLabel(f'<font size="5" color="{self.p1_color}"> {who}: {p_name} </font>')
        self.p1_score = QLabel('score : 0')
        self.p1_point_label = QLabel(f'point: {p_point}')
        self.p1_username_label = QLabel(f'username: {p_username}')
        self.p1_address_label = QLabel(f'address: {p_address}')
        player1_layout.addWidget(self.p1_name_label)
        player1_layout.addWidget(self.p1_score)
        player1_layout.addWidget(self.p1_point_label)
        player1_layout.addWidget(self.p1_username_label)
        player1_layout.addWidget(self.p1_address_label)
        self.room_layout.addItem(player1_layout)
        if len(players) == 1:
            p_name = 'WAITING ...'
            p_point = '...'
            p_username = '...'
            p_address = '...'
            self.p2_color = 'orange'
        else:
            p_name = players[1]['fullname']
            p_point = players[1]['point']
            p_username = players[1]['username']
            p_address = players[1]['address']
            self.p2_color, current = players[1]['color']
        player2_layout = QVBoxLayout()
        # who = "me " if ((self.my_turn and current == 2) or (not self.my_turn and current != 2)) else "player name "
        who = 'me ' if self.username == p_username else 'player name '
        self.my_color = self.p2_color if who == 'me ' else self.my_color
        self.p2_name_label = QLabel(f'<font size="5" color="{self.p2_color}"> {who}: {p_name} </font>')
        self.p2_score = QLabel('score : 0')
        self.p2_point_label = QLabel(f'point: {p_point}')
        self.p2_username_label = QLabel(f'username: {p_username}')
        self.p2_address_label = QLabel(f'address: {p_address}')
        player2_layout.addWidget(self.p2_name_label)
        player2_layout.addWidget(self.p2_score)
        player2_layout.addWidget(self.p2_point_label)
        player2_layout.addWidget(self.p2_username_label)
        player2_layout.addWidget(self.p2_address_label)
        self.room_layout.addItem(player2_layout)

    def onClickBoard(self, pos):

        x, y = pos
        res, msg = client1.put(x, y)
        status = msg['status']
        board = msg['board']
        turn = msg['turn']
        game_over = msg['game_over']
        self.game_over = game_over
        sb = msg['sb']
        sc = msg['sc']
        # print(msg)
        self.my_turn = turn

        if status != 'ok':
            qmsg = QMessageBox()
            qmsg.setText(status)
            qmsg.exec_()

        self.update_ui(sb, sc, game_over, board, True)
        # print(x)

    def update_board(self, board):
        self.painter.assignBoard(board)

        self.painter.update()

    def update_ui(self, sb, sc, game_over, board, force=False):

        self.turn_label.setText(f'Turn: {"You" if self.my_turn else "Not You"}')
        if sb or sc:
            self.p1_score.setText(f'score : {str(sb) if self.p1_color == "black" else str(sc)}')
            self.p2_score.setText(f'score : {str(sb) if self.p2_color == "black" else str(sc)}')
        if game_over:
            if sb > sc:
                winner = 'black'
            elif sb < sc:
                winner = 'white'
            else:
                winner = 'no_one'
            qmsg = QMessageBox()
            print(self.my_color)
            print(winner)
            qmsg.setText('Game Over : You Win' if winner == self.my_color else
                         'Game Over : Draw' if winner == 'no_one' else
                         'Game Over : You Lose')
            qmsg.exec_()
        self.update_board(board)
        if force:
            QApplication.instance().processEvents()

    def update_room_layout(self):
        # self.clearLayout(self.room_layout)
        res, msg = client1.get_room(self.dashboard.room_id)
        # print(msg)
        self.my_turn = msg['turn']
        players = msg['players']

        p_name = players[0]['fullname']
        p_point = players[0]['point']
        p_username = players[0]['username']
        p_address = players[0]['address']
        self.p1_color, current = players[0]['color']

        self.turn_label.setText(f'Turn: {"You" if self.my_turn else "Not You"}')
        # who = "me " if ((self.my_turn and current == 1) or (not self.my_turn and current != 1)) else "player name "
        who = 'me ' if self.username == p_username else 'player name '
        self.my_color = self.p1_color if who == 'me ' else ''
        self.p1_name_label.setText(f'<font size="5" color="{self.p1_color}"> {who}: {p_name} </font>')
        self.p1_point_label.setText(f'point: {p_point}')
        self.p1_username_label.setText(f'username: {p_username}')
        self.p1_address_label.setText(f'address: {p_address}')

        p_name = players[1]['fullname']
        p_point = players[1]['point']
        p_username = players[1]['username']
        p_address = players[1]['address']
        self.p2_color, current = players[1]['color']
        # who = "me " if ((self.my_turn and current == 2) or (not self.my_turn and current != 2)) else "player name "
        who = 'me ' if self.username == p_username else 'player name '
        self.my_color = self.p2_color if who == 'me ' else self.my_color
        self.p2_name_label.setText(f'<font size="5" color="{self.p2_color}"> {who}: {p_name} </font>')
        self.p2_point_label.setText(f'point: {p_point}')
        self.p2_username_label.setText(f'username: {p_username}')
        self.p2_address_label.setText(f'address: {p_address}')

        self.room_layout.update()
        self.layout.update()

    def send_message(self):
        text = self.chat_line_edit.text()
        client1.send(text)
        self.chat_text_browser.append(f'me: {text}')
        self.chat_line_edit.setText('')

    def request_to_join(self, username):
        qm = QMessageBox()
        ret = qm.question(self, '', f"{username} wants to join you?", qm.Yes | qm.No)
        if ret == qm.Yes:
            # print('sendtoooooooo')
            client1.sendto(username, 'yes')


    @pyqtSlot(dict)
    def on_my_signal_dict(self, value):
        # print(value)
        # print(self.dashboard.room_id)
        for user_uuid in value:
            message = value[user_uuid][1]
            username = value[user_uuid][0]
            # print(type(message))
            if type(message) == dict:
                turn = message['turn']
                # print(turn)
                board = message['board']
                game_over = message['game_over']
                self.game_over = game_over
                sb = message['sb']
                sc = message['sc']
                self.my_turn = turn
                txt = 'move: ' + str(message['move'])
                self.update_ui(sb, sc, game_over, board, True)
            elif message == 'request for join':
                self.request_to_join(username)
                txt = 'requested to join'
            elif message == 'joined':
                self.update_room_layout()
                txt = 'joined!'
            else:
                txt = message
            # print(txt)
            self.chat_text_browser.append(username + ' :' + txt)


class MySignal(QWidget):
    sig = pyqtSignal(dict)


if __name__ == '__main__':
    app = QApplication(sys.argv)

    try:
        sig = MySignal()
        client1 = client.Client("127.0.0.1", 1234, 1234, 1235, qt_signal=sig)

        print("Client 1 : %s" % client1.identifier)

    except:
        try:
            client1 = client.Client("127.0.0.1", 1234, 1234, 1236, qt_signal=sig)
            print("Client 1 : %s" % client1.identifier)
        except:
            print('FFFFFFFF')
            qmsg = QMessageBox()
            qmsg.setText('connection problem!')
            qmsg.exec_()
            exit()

    form = LoginForm()
    form.show()
    sys.exit(app.exec_())
