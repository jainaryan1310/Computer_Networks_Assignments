import socket
import select
import errno
import sys

HEADER_LENGTH = 10

IP = "127.0.0.1"
PORT = 1234

my_username = input("Username : ")

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((IP, PORT))
client_socket.setblocking(False)

username_msg = my_username.encode("utf-8")
username_header = f"{len(username_msg):<{HEADER_LENGTH}}".encode("utf-8")

client_socket.send(username_header + username_msg)


while True:
  sockets_list = [sys.stdin, client_socket]
  # message = input(f"{my_username} > ")

  read_sockets, _, exception_sockets = select.select(sockets_list, [], sockets_list)

  for notified_socket in read_sockets:
    if notified_socket == sys.stdin:
      message = sys.stdin.readline()
      if message:
        message = message.encode("utf-8")
        message_header = f"{len(message):<{HEADER_LENGTH}}".encode("utf-8")
        client_socket.send(message_header + message)

    else:
      try:
        while True:

          username_header = client_socket.recv(HEADER_LENGTH)

          if not len(username_header):
            print("connection closed by server")
            sys.exit()

          username_length = int(username_header.decode("utf-8").strip())
          username = client_socket.recv(username_length).decode("utf-8")

          message_header = client_socket.recv(HEADER_LENGTH)

          message_length = int(message_header.decode("utf-8").strip())
          message = client_socket.recv(message_length).decode("utf-8")
          
          print(f"{username} > {message}")

      except IOError as e:
        if e.errno != errno.EAGAIN and e.errno != errno.EWOULDBLOCK:
          print("IO Error", str(e))
          sys.exit()
        continue

      except Exception as e:
        print("General Error", str(e))
        sys.exit()
