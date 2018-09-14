from time import time

try:
    import struct
except ImportError:
    import ustruct as struct

try:
    import socket
except ImportError:
    import usocket as socket


class SimpleNTP:
    TIME70 = 2208988800
    OFFSET = 0

    def __init__(self, server="192.168.0.80", port=123):
        self.port = port
        self.server = server


    def get_local_time(self):
        return SimpleNTP.OFFSET + time()


    def get_offset(self):
        return SimpleNTP.OFFSET


    def request_time(self):
        try:
            data =  struct.pack("B", self._set_li_vn_mode(0, 3, 3)) + 47 * b"\0"
            client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            client.settimeout(1.0)
            client.sendto(data, (self.server, self.port))
            resp, (s, p) = client.recvfrom(1024)
            client.close()
            if len(resp) != 48:
                print("Unknown response from NTP-server")
                return 0
            self._unpack(resp)
            self._set_offset()
            return self.ntp_time
        except OSError:
            print("Failed to contact NTP-server")
            return self.get_local_time()


    def _set_offset(self):
        SimpleNTP.OFFSET = self.ntp_time - time()


    def _unpack(self, data):
        data = struct.unpack("!4B11I", data)
        t_tx = data[13]
        self.ntp_time = t_tx - self.TIME70


    def _set_li_vn_mode(self, li, vn, mode):
        assert((li & ~3) == 0)
        assert((vn & ~7) == 0)
        assert((mode & ~7) == 0)
        byte = 0
        byte |= (li << 6)
        byte |= (vn << 3)
        byte |= mode
        return byte


    def _get_li_vn_mode(self, byte):
        li = (byte & 0b11000000) >> 6
        vn = (byte & 0b00111000) >> 3
        mode = (byte & 0b00000111)
        return (li, vn, mode)
