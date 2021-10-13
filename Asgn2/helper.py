import socket

HEADER_LENGTH = 10

def recv_msg(socket):
  try:
    message_header = socket.recv(HEADER_LENGTH)

    if not len(message_header):
      return False

    message_length = int(message_header.decode('utf-8').strip())
    return {'header': message_header, 'data': socket.recv(message_length)}

  except:
    return False

def send_msg(socket, message):
  try:
    message = message.encode('utf-8')
    message_header = f"{len(message):<{HEADER_LENGTH}}".encode('utf-8')
    socket.send(message_header + message)
  except:
    return False