#!/usr/bin/env python
from gevent.server import StreamServer

cache = {}

def handle_con(conn, client):
    sockfile = conn.makefile()
    while True:
        line = sockfile.readline()
        if line == "quit\r\n":
            sockfile.close()
            break

        parts = line.split()
        cmd = parts[0]

        if cmd == "get":
            key = parts[1]
            buffer = []
            if cache.get(key):
                val = cache[key]
                buffer.append("VALUE %s 0 %d\r\n" % (key, len(val)))
                buffer.append("%s\r\n" % val)
            buffer.append("END\r\n")
            sockfile.write(''.join(buffer))
            sockfile.flush()
        elif cmd == "set":
            key = parts[1]
            length = int(parts[4])
            val = sockfile.read(length + 2)[:length]
            cache[key] = val
            sockfile.write("STORED\r\n")
            sockfile.flush()

if __name__ == "__main__":
    StreamServer(("127.0.0.1", 11211), handle_con).serve_forever()
