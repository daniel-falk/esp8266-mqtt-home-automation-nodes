import network

def access_point(enable=False, disable=False):
    ap = network.WLAN(network.AP_IF)
    if enable:
        ap.active(True)
    if disable:
        ap.active(False)

    return ap.active()


def connect():
    con = network.WLAN(network.STA_IF)
    con.active(True)
    con.connect("<SSID>", "<PASS>")


def get_ip():
    con = network.WLAN(network.STA_IF)
    if not con.active():
        return None
    if not con.isconnected():
        return None
    return con.ifconfig()[0]
