#!/usr/bin/python3
from os import error, system
import telnetlib
import time
import sys


def find(arr, substring, iter):
    for i in arr:
        if substring in i:
            val = arr.index(i)
    return '{}\n{}\n'.format(arr[val], arr[val + iter - 1])


def check_arp(ip, telnet):
    b = ''
    command = 'show iparp {}'.format(ip)
    telnet.write('{}\n'.format(command).encode())
    time.sleep(0.5)
    data = telnet.read_very_eager()
    data = data.decode('utf-8')
    b = b + data

    b = b.splitlines()
    buff = [x for x in b]
    print(find(buff, 'Destination', 2))





def connect_term(telnet):
    try:
        telnet.write(b'login\n')
        telnet.write(b'password\n')
        print('---ARP---')
    except error as e:
        print('[-] Error: ' + e)



def main():
    
    restr = 0
    if len(sys.argv) < 2:
        print('\033[31m{}\033[0m'.format('[-] Invalid aguments.'))
        sys.exit(0)

    try:

        switch = sys.argv[1]
        ip = sys.argv[2]

        system('cls||clear')
        print('Switch: \033[36m{}\033[0m  IP: \033[36m{}\033[0m'.format(switch, ip))

        telnet = telnetlib.Telnet(switch)
        connect_term(telnet)
        time.sleep(0.5)
        check_arp(ip, telnet)
        

    except KeyboardInterrupt as e:
        print('\033[36m{}\033[0m'.format('\n[+] Keyboard Interrupt. Exited.'))
        telnet.write('logo'.encode())
    except error as e:
        print(e)
        telnet.write('logo'.encode())


if __name__ == "__main__":
    main()
