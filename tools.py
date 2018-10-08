#!/usr/bin/env python3

import os
import sys
import subprocess
import pty
from glob import glob
import re
import argparse

from serial.serialutil import SerialException


class EspTool():

    def __init__(self, port, baud):
        from esptool import main as esp
        self.esp = esp
        self.port = port
        self.baud = baud

    def flash(self, binary_path, mode="qio", start_addr=0x00):
        args = ['']
        if self.port is not None:
            args.append("--port=/dev/%s" % self.port)
        if self.baud is not None:
            args.append("--baud=%d" % self.baud)
        args.append("write_flash")
        args.append("--flash_size=detect")
        args.append("--flash_mode=%s" % mode)
        args.append("0x%0.2X" % start_addr)
        args.append(binary_path)
        sys.argv = args
        self.esp()

    def erase(self):
        args = ['']
        if self.port is not None:
            args.append("--port=/dev/%s" % self.port)
        if self.baud is not None:
            args.append("--baud=%d" % self.baud)
        args.append("erase_flash")
        sys.argv = args
        self.esp()


class Tool():

    def __init__(self, port):
        self.port = port
        self.mpfshell = ["mpfshell", "-o", port]

        self.fw_root = "/home/daniel/workspace/esp8266/micropython/micropython/"
        self.target_root = os.path.join(self.fw_root, "ports", "esp8266")
        self.target_bin = os.path.join(self.target_root, "build", "firmware-combined.bin")
        self.host_root = os.path.join(self.fw_root, "ports", "unix")
        self.host_bin = os.path.join(self.host_root, "micropython")

    def run_host(self):
        pty.spawn([self.host_bin])

    def run_target(self):
        pty.spawn(self.mpfshell)

    def run_repl(self):
        pty.spawn(self.mpfshell + ["-c", "repl"])

    def flash_chip(self, erase=False):
        esp = EspTool(self.port, 115200)
        try:
            if erase:
                esp.erase()
            esp.flash(self.target_bin)
        except SerialException:
            print("No device connected to port")

    def reset(self):
        subprocess.Popen(self.mpfshell + ["-n", "--reset"]).wait()

    def print_files(self):
        for n, t in self.get_target_files():
            print("%s%s" % (n, " (dir)" if t else ""))

    # TODO: Only first level supported
    def get_target_files(self):
        p = subprocess.Popen(self.mpfshell + ["-n", "-c", "ls"], stdout=subprocess.PIPE)
        out, err = p.communicate()
        out_lines = [line for line in out.decode().split("\n") if len(line) > 0]
        header_index = [True if "Remote files in" in l else False for l in out_lines].index(True)
        out_lines = out_lines[header_index + 1:]
        out_lines = [re.sub(r'[\x00-\x1f\x7f-\x9f][^ ]+', '', l).strip() for l in out_lines]
        files = [(re.sub(r'<dir> ', '', l), '<dir> ' in l) for l in out_lines]
        return files

    def has_file(self, name, folder_type=False):
        files = self.get_target_files()
        return (name, folder_type) in files

    def make_dir(self, path, error_on_exist=False):
        name = path.split("/")
        for i in range(0, len(name)):
            if i == 0:
                cmd = "md %s" % name[i]
            else:
                cwd = "/".join(name[:i])
                n = name[i]
                cmd = "cd %s; md %s" % (cwd, n)
            p = subprocess.Popen(self.mpfshell + ["-n", "-c", cmd], stdout=subprocess.PIPE)
            out, err = p.communicate()
            if "Invalid directory name" in out.decode() and error_on_exist:
                print("Failed to create directory, name already exist")

    def deploy_dir(self, dir, type="*.py", cut_dir_name=False, recursive=True):
        if recursive:
            dirs = sorted([p[0] for p in os.walk(dir, followlinks=True)])
            for d in dirs:
                self.make_dir(d)
                self.deploy_dir(d, type=type, recursive=False)
        else:
            files = glob(os.path.join(dir, type))
            for f in files:
                ex_dir = "."
                if cut_dir_name:
                    f = f[len(dir) + 1:]
                    ex_dir = dir
                print("cpy %s..." % f)
                p = subprocess.Popen(self.mpfshell + ["-n", "-c", "put", f], cwd=ex_dir, stdout=subprocess.PIPE)
                out, err = p.communicate()
                if"Connected" not in out.decode():
                    print("Copy of files failed")
                    print(out)
                    sys.exit(3)
                if "No such file or directory" in out.decode():
                    raise RuntimeError("File not found: %s" % f)

    def deploy(self, project, dirs=[]):
        if not os.path.isdir(project):
            print("%s is not a project directory" % project)
            sys.exit(2)
        for d in dirs:
            self.deploy_dir(d)
        self.deploy_dir(project, cut_dir_name=True, recursive=False)
        self.deploy_dir(project, type="*.json", cut_dir_name=True, recursive=False)


if __name__ == "__main__":
    commands = ["host", "shell", "repl", "deploy", "go", "list-files", "reset", "reflash"]
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=commands)
    parser.add_argument("--port", default="ttyUSB0", help="Which port to use (ttyUSB0)")
    args, other = parser.parse_known_args()

    tool = Tool(args.port)

    if args.command == "host":
        tool.run_host()

    elif args.command == "shell":
        tool.run_target()

    elif args.command == "repl":
        tool.run_repl()

    elif args.command == "deploy" or args.command == "go":
        project = other[0]
        dirs = other[1:]
        tool.deploy(project, dirs)
        if args.command == "go":
            tool.run_repl()

    elif args.command == "list-files":
        tool.print_files()

    elif args.command == "reset":
        tool.reset()

    elif args.command == "reflash":
        tool.flash_chip(erase=True)

    else:
        raise RuntimeError("Unknown command")
