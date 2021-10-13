import socket
import sys
from _thread import *
from helper import *

HEADER_LENGTH = 10
IP = "127.0.0.1"
PORT = 1234

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

server_socket.bind((IP, PORT))

server_socket.listen()

sockets_to_clients = {}
sockets_from_clients = {}
clients = {}
status = {}

def client_thread(from_socket, to_socket, username):
  username = sockets_from_clients[from_socket]

  while True:

    if status[username] == 3:
      continue

    message = recv_msg(from_socket)

    if message == False:
      break

    msg_data = message['data'].decode('utf-8')

    if msg_data[0:msg_data.find(" ")] == "SEND":
      msg_data = msg_data[msg_data.find(" ")+1:]
      recepient_username = msg_data[0:msg_data.find("\n")]
      msg_data = msg_data[msg_data.find("\n")+1:]

      if msg_data[0:msg_data.find(" ")] != "Content-length:":
        send_msg(to_socket, "ERROR 103 Header incomplete \n\n")
        continue

      msg_data = msg_data[msg_data.find(" ")+1:]
      length = int(msg_data[0:msg_data.find("\n")])
      msg_data = msg_data[msg_data.find("\n\n")+2:]
      msg_text = msg_data[0:length]

      if recepient_username not in sockets_to_clients.keys():
        send_msg(to_socket, "ERROR 102 Unable to send\n\n")
        continue

      forwarded_message = "FORWARD " + username + "\nContent-length: " + str(length) + "\n\n" + msg_text
      print(forwarded_message)
      clients[recepient_username] = (clients[recepient_username][0], clients[recepient_username][1], 3)
      send_msg(sockets_to_clients[recepient_username], forwarded_message)
      status[username] = 3

    elif msg_data[0:msg_data.find(" ") == "RECEIVED"]:
      msg_data = msg_data[msg_data.find(" ")+1:]
      sender_username = msg_data[0:msg_data.find("\n")]

      send_msg(sockets_to_clients[sender_username], f"SEND {username}\n\n")
      status[sender_username] = 2

    else:
      continue

  # while True:

  #   if status[username] == 3:
  #     continue

  #   message = recv_msg(from_socket)
  #   if message == False:
  #     break

  #   status[username] = 3

  #   msg_data = message['data'].decode('utf-8')

  #   if msg_data[0:msg_data.find(" ")] == "SEND":
  #     msg_data = msg_data[msg_data.find(" ")+1:]
  #     recepient_username = msg_data[0:msg_data.find("\n")]
  #     msg_data = msg_data[msg_data.find("\n")+1]

  #     if msg_data[0:msg_data.find(" ")] != "Content-length:":
  #       clients[username] = (from_socket, to_socket, 2)
  #       send_msg(to_socket, "ERROR 103 Header incomplete \n\n")

  #     else:
  #       msg_data = msg_data[msg_data.find(" ")+1:]
  #       length = int(msg_data[0:msg_data.find("\n")])
  #       msg_data = msg_data[msg_data.find("\n\n")+1]
  #       msg_text = msg_data[0:length]

  #       if recepient_username not in sockets_to_clients.keys():
  #         clients[username] = (from_socket, to_socket, 2)
  #         send_msg(to_socket, "ERROR 102 Unable to send\n\n")

  #       elif recepient_username == "ALL":
  #         recepient_list = sockets_to_clients.key()

  #         for recepient_username in recepient_list:

  #           if recepient_username == username:
  #             continue

  #           else:
  #             recepient_to_socket = sockets_to_clients[recepient_username]

  #             forwarded_message = "FORWARD " + username + "\nContent-length: " + str(length) + "\n\n" + msg_text
  #             clients[recepient_username] = (clients[recepient_username][0], clients[recepient_username][1], 3)
  #             send_msg(recepient_to_socket, forwarded_message)

  #             recepient_from_socket = clients[recepient_username][0]
  #             receiver_confirmation_message = recv_msg(recepient_from_socket)['data'].decode('utf-8')

  #             clients[recepient_username] = (clients[recepient_username][0], clients[recepient_username][1], 2)
  #             clients[username] = (from_socket, to_socket, 2)

  #             if receiver_confirmation_message[0:8] == "RECEIVED":
  #               sender_username = receiver_confirmation_message[9:receiver_confirmation_message.find("\n")]

  #               if sender_username == username:
  #                 sender_confirmation_message = "SEND " + recepient_username + "\n\n"
  #                 send_msg(to_socket, sender_confirmation_message)

  #               else:
  #                 send_msg(to_socket, "ERROR 102 Unable to send\n\n")
  #                 break

  #             else:
  #               send_msg(to_socket, "ERROR 102 Unable to send\n\n")
  #               break

  #       else:
  #         recepient_to_socket = sockets_to_clients[recepient_username]

  #         forwarded_message = "FORWARD " + username + "\nContent-length: " + str(length) + "\n\n" + msg_text
  #         clients[recepient_username] = (clients[recepient_username][0], clients[recepient_username][1], 3)
  #         send_msg(recepient_to_socket, forwarded_message)

  #         recepient_from_socket = clients[recepient_username][0]
  #         receiver_confirmation_message = recv_msg(recepient_from_socket)

  #         clients[recepient_username] = (clients[recepient_username][0], clients[recepient_username][1], 2)
  #         clients[username] = (from_socket, to_socket, 2)

  #         if receiver_confirmation_message[0:8] == "RECEIVED":
  #           sender_username = receiver_confirmation_message[9:receiver_confirmation_message.find("\n")]

  #           if sender_username == username:
  #             sender_confirmation_message = "SEND " + recepient_username + "\n\n"
  #             send_msg(to_socket, sender_confirmation_message)

  #           else:
  #             send_msg(to_socket, "ERROR 102 Unable to send\n\n")

  #         else:
  #           send_msg(to_socket, "ERROR 102 Unable to send\n\n")
      
  #   else:
  #     clients[username] = (from_socket, to_socket, 2)
  #     send_msg(to_socket, "ERROR 103 Header incomplete \n\n")
      
  print(f"Closed connection from {username}")
  del sockets_from_clients[from_socket]
  del sockets_to_clients[username]
  del clients[username]
  from_socket.close()
  to_socket.close()


while True:
  
  client_socket, client_address = server_socket.accept()

  registration_message = recv_msg(client_socket)
  if registration_message is False:
    continue

  msg_data = registration_message['data'].decode('utf-8')
  username = msg_data[16:int(msg_data.find("\n"))]

  if not username.isalnum():
    msg_to_client = "ERROR 100 Malformed username\n\n".encode('utf-8')
    message_header = f"{len(msg_to_client):<{HEADER_LENGTH}}"
    client_socket.send(message_header + msg_to_client)

  if msg_data[0:15] == "REGISTER TOSEND" and client_socket not in sockets_from_clients.keys():
    sockets_from_clients[client_socket] = username
    clients[username] = (client_socket, client_socket)
    status[username] = 1

    send_msg(client_socket, f"REGISTERED TOSEND {username}\n\n")

  elif msg_data[0:15] == "REGISTER TORECV" and status[username] == 1:
    sockets_to_clients[username] = client_socket
    from_socket = clients[username][0]
    clients[username] = (from_socket, client_socket)
    status[username] = 2


    send_msg(client_socket, f"REGISTERED TORECV {username}\n\n")
    print("Accepted connection from ", username)

    start_new_thread(client_thread, (from_socket, client_socket, username))


  else:
    send_msg(client_socket, "ERROR 101 No user registered\n\n")


  