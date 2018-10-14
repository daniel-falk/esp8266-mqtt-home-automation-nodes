import network
import machine
import ubinascii
from time import sleep

from .logging import FileLogger


def wait_for_connect(allow_restart=False):
    failed_count = 0
    while True:
        ip = get_ip()
        if ip is not None:
            FileLogger.log("Connected with IP: %s" % ip)
            break
        failed_count += 1
        FileLogger.log("Failed to connect to wifi %d times..." % failed_count)
        sleep(1)
        if failed_count > 60 and allow_restart:
            machine.reset()


def access_point(enable=False, disable=False):
    ap = network.WLAN(network.AP_IF)
    if enable:
        ap.active(True)
    if disable:
        ap.active(False)

    return ap.active()


def connect(ssid, password, wait=False, **kwargs):
    con = network.WLAN(network.STA_IF)
    if not con.active():
        con.active(True)
        con.connect(ssid, password)
    if wait:
        wait_for_connect(**kwargs)


def disconnect():
    con = network.WLAN(network.STA_IF)
    con.active(False)


def get_ip():
    con = network.WLAN(network.STA_IF)
    if not con.active():
        return None
    if not con.isconnected():
        return None
    return con.ifconfig()[0]


def get_mac():
    mac = network.WLAN().config('mac')
    return ubinascii.hexlify(mac, ':').decode()
