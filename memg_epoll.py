#!/usr/bin/env python
import select
import socket
from collections import defaultdict

cache = {}
writes = defaultdict(list)
fd_to_file = {}

def _server_socket():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(("127.0.0.1", 11211))
    sock.listen(5)
    return sock

def main():
    sock = _server_socket()
    epoll = select.epoll()
    epoll.register(sock, select.EPOLLIN)
    sock_fd = sock.fileno()

    while True:
        ready = epoll.poll()
        for fd, event in ready:
            if fd == sock_fd:
                conn, _ = sock.accept()
                fd_to_file[conn.fileno()] = conn.makefile()
                epoll.register(conn, select.EPOLLIN | select.EPOLLOUT)
            else:
                sockfile = fd_to_file[fd]
                if event & select.EPOLLOUT:
                    if writes[fd]:
                        sockfile.write(''.join(writes[fd]))
                        sockfile.flush()
                        writes[fd] = []
                if event & select.EPOLLIN:
                    line = sockfile.readline()
                    if line == 'quit\r\n':
                        epoll.unregister(fd)
                        sockfile.close()
                        continue
                    handle_read(fd, line, sockfile)

def handle_read(conn, line, sockfile):
    parts = line.split()
    cmd = parts[0]

    if cmd == "get":
        key = parts[1]
        try:
            val = cache[key]
            writes[conn].append("VALUE %s 0 %d\r\n" % (key, len(val)))
            writes[conn].append(val + "\r\n")
        except KeyError:
            pass
        writes[conn].append("END\r\n")
    elif cmd == "set":
        key = parts[1]
        length = int(parts[4])
        val = sockfile.read(length + 2)[:length]
        cache[key] = val
        writes[conn].append("STORED\r\n")

if __name__ == "__main__":
    main()
