import socket
import sys
import io
import struct


class _FlushFile(io.FileIO):
    def __init__(self, f):
        self.f = f

    def write(self, x):
        self.f.write(x)
        self.f.flush()


def create_udp_socket(ttl: int) -> socket.socket:
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    udp_socket.setsockopt(socket.SOL_IP, socket.IP_TTL, ttl)
    return udp_socket


def create_icmp_socket(port: int) -> socket.socket:
    icmp_socket = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP)
    timeout = struct.pack("ll", 5, 0)
    icmp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_RCVTIMEO, timeout)
    icmp_socket.bind(("", port))
    return icmp_socket


def receive_packages(rec_socket: socket.socket, curr_address, curr_name, finished):
    tries = 3
    while not finished and tries > 0:
        try:
            _, curr_addresses = rec_socket.recvfrom(512)
            finished = True
            curr_address = curr_addresses[0]
            try:
                curr_name = socket.gethostbyaddr(curr_address)[0]
            except socket.error:
                curr_name = curr_address
        except socket.error:
            tries -= 1
            sys.stdout.write("* ")
    return curr_name, curr_address, finished


def trace_route(dest_name):
    sys.stdout = _FlushFile(sys.stdout)
    dest_address = ""

    try:
        dest_address = socket.gethostbyname(dest_name)
    except socket.gaierror:
        print(f"Name or service {dest_name} is not known, please, try again")
        exit(1)

    print(f"trace route to {dest_name} ({dest_address}), 30 hops max")

    port = 64444
    max_hops = 30

    ttl = 1
    while True:
        receiver_socket = create_icmp_socket(port)
        sender_socket = create_udp_socket(ttl)

        sys.stdout.write(" %d   " % ttl)
        sender_socket.sendto(bytes("", "utf-8"), (dest_name, port))

        curr_address, curr_name, finished = None, None, False

        curr_name, curr_address, finished = receive_packages(receiver_socket, curr_name, curr_address, finished)

        sender_socket.close()
        receiver_socket.close()

        if not finished:
            pass

        if curr_address is not None:
            curr_host = "%s (%s)" % (curr_name, curr_address)
        else:
            curr_host = ""
        sys.stdout.write("%s\n" % (curr_host))

        ttl += 1
        if curr_address == dest_address or ttl > max_hops:
            break
