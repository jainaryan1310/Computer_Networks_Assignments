import socket
import errno
import re
import sys
import time
from _thread import *
from helper import *

HEADER_LENGTH = 10

IP = "127.0.0.1"
PORT = 1234

my_username = input("Username : ")

socket_to_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
socket_to_server.connect((IP, PORT))
socket_to_server.setblocking(False)

send_registration_message = "REGISTER TOSEND " + my_username + "\n\n"
send_msg(socket_to_server, send_registration_message)

time.sleep(1)

send_confirmation_message = recv_msg(socket_to_server)['data'].decode('utf-8')
if send_confirmation_message[0:17] != "REGISTERED TOSEND":
  print("Please enter a valid username")
  sys.exit()

print("client registered to send")


socket_from_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
socket_from_server.connect((IP, PORT))
socket_from_server.setblocking(False)

recv_registration_message = "REGISTER TORECV " + my_username + "\n\n"
send_msg(socket_from_server, recv_registration_message)

time.sleep(1)

recv_confirmation_message = recv_msg(socket_from_server)['data'].decode('utf-8')
if recv_confirmation_message[0:17] != "REGISTERED TORECV":
  print("Please enter a valid username")
  sys.exit()

print("client registered to receive")

status = 0


def handle_input(k):
  status = 0

  while True:

    if status:
      response = recv_msg(socket_from_server)
      if response:
        confirmation_message = response['data'].decode('utf-8')
        status = 0
        print("confirmation message", confirmation_message)
        if confirmation_message[0:4] != "SEND":
          print("The message wasn't delivered successfully, please check the recepient username")

      continue

    input_text = sys.stdin.readline()

    if input_text:

      if not bool(re.match("@[A-Za-z0-9]+\ [A-Za-z0-9]+", input_text)):
        print("Please re-enter the message in the correct format/nCorrect format is:/n@[recepient username] [message]")
        continue

      recepient_username = input_text[1:input_text.find(" ")]
      message = input_text[input_text.find(" ")+1:]

      send_message = "SEND " + recepient_username + "\nContent-length: " + str(len(message)) + "\n\n" + message
      send_msg(socket_to_server, send_message)
      
      status = 1


def handle_message(k):
  status = 0
  
  while True:

    if status == 1:
      continue

    try:
      message = recv_msg(socket_from_server)

      if message == False:
        continue
      msg_data = message['data'].decode('utf-8')

      if not bool(re.match("FORWARD\ [A-Za-z0-9]+\nContent-length:\ [0-9]+\n\n.*", msg_data)):
        print(msg_data)
        send_msg(socket_from_server, "ERROR 103 Header Incomplete\n\n")
        continue

      msg_data = msg_data[msg_data.find(" ")+1:]
      sender_username = msg_data[:msg_data.find("\n")]
      print(sender_username)
      
      send_msg(socket_to_server, f"RECEIVED {sender_username}\n\n")

      print("111111111")

      msg_data = msg_data[msg_data.find("\n")+1:]
      
      msg_data = msg_data[msg_data.find(" ")+1:]
      length = int(msg_data[0:msg_data.find("\n")])
      msg_data = msg_data[msg_data.find("\n\n")+2:]
      msg_text = msg_data[0:length]

      output = sender_username + " > " + msg_text
      print(output)

      
    except IOError as e:
      if e.errno != errno.EAGAIN and e.errno != errno.EWOULDBLOCK:
        print("IO Error", str(e))
        sys.exit()
      continue

    except Exception as e:
      print("General Error", str(e))
      sys.exit()

start_new_thread(handle_input, (1,))
start_new_thread(handle_message, (1,))

while True:
  continue  



