import socket
import threading
from time import sleep, time

# the host of this server
from max_info import get_max

host = "192.168.186.128"
# the port to recv and send the msg
port = 12345
# the time when this server recv the cascade msg
recv_time = ""
# the path of the max_info file
max_file_path = "/home/server-1/max_info"
time_compare = 0
is_master = 0

# send the message that want to cascade with other server to broadcast
def send_msg_cascade():
    global recv_time
    desc = ('<broadcast>', port)
    s_send = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s_send.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    while True:
        s_send.sendto("send cascade".encode(), desc)
        if recv_time != "":
            break
        sleep(1)
    s_send.close()
    print("send_msg_cascade over")

# recv the message from the other server that want to cascade
def recv_msg_cascade():
    global recv_time, is_master, time_compare
    s_recv = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s_recv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s_recv.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    s_recv.bind((host, port))
    while True:
        sock, addr = s_recv.recvfrom(8192)
        if addr[0] == host:
            continue
        elif sock.decode() == "send cascade":
            print(sock.decode(), addr)
            recv_time = time()
            s_recv.sendto(str(recv_time).encode(), addr)
            break
    recv_time_other, _ = s_recv.recvfrom(8192)
    # this server is master node
    if float(recv_time_other) > float(recv_time):
        is_master = 1
    time_compare = 1
    s_recv.close()
    print("recv_msg_cascade over")

if __name__ == '__main__':
    send_msg_cascade_threading = threading.Thread(target=send_msg_cascade)
    recv_msg_cascade_threading = threading.Thread(target=recv_msg_cascade)
    send_msg_cascade_threading.start()
    recv_msg_cascade_threading.start()

    while True:
        if time_compare == 1:
            # this server is master node
            if is_master == 1:
                get_max(max_file_path)

            # this server is not master node
            else:
                print("this server is not master node")
        sleep(5)

