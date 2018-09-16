#!/usr/bin/env python3

import os
import sys
import subprocess
import pty
from glob import glob
import re

port = "ttyUSB0"
mpfshell = ["mpfshell", "-o", port]

fw_root = "/home/daniel/workspace/esp8266/micropython/micropython/"
target_root = os.path.join(fw_root, "ports", "esp8266")
target_bin = os.path.join(target_root, "build", "firmware-combined.bin")
host_root = os.path.join(fw_root, "ports", "unix")
host_bin = os.path.join(host_root, "micropython")


def flash_chip(erase=False):
    esptool = ["esptool.py", "--port", "/dev/%s" % port, "--baud", "115200"]
    if erase:
        subprocess.Popen(esptool + ["erase_flash"]).wait()
    subprocess.Popen(esptool + ["write_flash", "--verify", "--flash_size=detect", "--flash_mode=qio", "0x00", target_bin]).wait()


# TODO: Only first level supported
def get_target_files():
    p = subprocess.Popen(mpfshell + ["-n", "-c", "ls"], stdout=subprocess.PIPE)
    out, err = p.communicate()
    out_lines = [line for line in out.decode().split("\n") if len(line) > 0]
    header_index = [True if "Remote files in" in l else False for l in out_lines].index(True)
    out_lines = out_lines[header_index + 1 : ]
    out_lines = [re.sub(r'[\x00-\x1f\x7f-\x9f][^ ]+', '', l).strip() for l in out_lines]
    files = [(re.sub(r'<dir> ', '', l), '<dir> ' in l) for l in out_lines]
    return files


def has_file(name, folder_type=False):
    files = get_target_files()
    return (name, folder_type) in files


def make_dir(path, error_on_exist=False):
    name = path.split("/")
    for i in range(0, len(name)):
        if i == 0:
            cmd = "md %s" % name[i]
        else:
            cwd = "/".join(name[:i])
            n = name[i]
            cmd = "cd %s; md %s" % (cwd, n)
        p = subprocess.Popen(mpfshell + ["-n", "-c", cmd], stdout=subprocess.PIPE)
        out, err = p.communicate()
        if "Invalid directory name" in out.decode() and error_on_exist:
            print("Failed to create directory, name already exist")


def deploy_dir(dir, type="*.py", cut_dir_name=False, recursive=True):
    if recursive:
        dirs = sorted([p[0] for p in os.walk(dir, followlinks=True)])
        for d in dirs:
            make_dir(d)
            deploy_dir(d, type=type, recursive=False)
    else:
        files = glob(os.path.join(dir, type))
        for f in files:
            ex_dir = "."
            if cut_dir_name:
                f = f[len(dir) + 1 : ]
                ex_dir = dir
            print("cpy %s..." % f)
            p = subprocess.Popen(mpfshell + ["-n", "-c", "put", f], cwd=ex_dir, stdout=subprocess.PIPE)
            out, err = p.communicate()
            if not "Connected" in out.decode():
                print("Copy of files failed")
                print(out)
                sys.exit(3)
            if "No such file or directory" in out.decode():
                raise RuntimeError("File not found: %s" % f)


def deploy(project, dirs=[]):
    if not os.path.isdir(project):
        print("%s is not a project directory" % project)
        sys.exit(2)
    for d in dirs:
        deploy_dir(d)
    deploy_dir(project, cut_dir_name=True, recursive=False)
    deploy_dir(project, type="*.json", cut_dir_name=True, recursive=False)


def help():
    print("Usage %s <command>" % sys.argv[0])
    sys.exit(1)


if __name__ == "__main__":
    try:
        cmd = sys.argv[1]
    except IndexError:
        help()


    if cmd == "host":
        pty.spawn([host_bin])

    elif cmd == "shell":
        pty.spawn(mpfshell)

    elif cmd == "repl":
        pty.spawn(mpfshell + ["-c", "repl"])

    elif cmd == "deploy" or cmd == "go":
        project = sys.argv[2]
        dirs = sys.argv[3:]
        deploy(project, dirs)
        if cmd == "go":
            pty.spawn(mpfshell + ["-c", "repl"])

    elif cmd == "list-files":
        for n, t in get_target_files():
            print("%s%s" % (n, " (dir)" if t else ""))

    elif cmd == "reset":
        subprocess.Popen(mpfshell + ["-n", "--reset"]).wait()

    elif cmd == "reflash":
        flash_chip(erase=True)

    elif cmd == "mkdir":
        try:
            make_dir(sys.argv[2], error_on_exist=True)
        except IndexError:
            help()

    else:
        help()
