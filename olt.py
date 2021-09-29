#!/usr/bin/python3
from os import error, system
import telnetlib
import time
import sys



def find(arr, substring, iter):
    for i in arr:
        if substring in i:
            val = arr.index(i)
    if iter == 1:
        return '{}\n'.format(arr[val])
    else:
        return '{}\n{}\n{}\n'.format(arr[val], arr[val + iter - 2], arr[val + iter - 1])


def check(port, telnet):
    b = ''
    commands_q = ['en', 'show ont optical-info {}', 'show ont mac-address-table {}', 'show ont port-status {} port 1']
    for i in commands_q:
        telnet.write('{}\n'.format(i.format(port)).encode())
        time.sleep(0.5)
        data = telnet.read_very_eager()
        data = data.decode('utf-8')
        b = b + data

    b = b.splitlines()
    buff = [x for x in b if x]

    separator = '============================================================================'

    print(separator)
    print(find(buff, 'Power Feed Voltage', 3))
    print(separator)
    time.sleep(1)
    print(find(buff, 'MAC-Address', 3))
    print(separator)
    time.sleep(1)
    print(find(buff, 'Port status', 1))
    print(separator)

 


def connect_term(telnet):
    try:
        telnet.write(b'login\n')
        telnet.write(b'password\n')

    except error as e:
        print('[-] Error: ' + e)




def main():
    

    try:

        if len(sys.argv) < 3:
            print('[-] Invalid aguments.')
            raise KeyboardInterrupt

        switch = sys.argv[1]
        port = sys.argv[2]

        print('Switch: {}  Port: {}'.format(switch, port))

        telnet = telnetlib.Telnet(switch)
        connect_term(telnet)

        re = ''
        while True:

            system('cls||clear')
            print('[+] Olt Connected')

            check(port, telnet)
            print('Switch: \033[36m{}\033[0m  Port: \033[36m{}\033[0m'.format(switch, port))

            print('\033[34m<Enter>\033[0m - refresh \n')
            re = input('[+] > ')


    except KeyboardInterrupt as e:
        system('cls||clear')
        print('[+] Keyboard Interrupt. Exited.')
        telnet.write('exit'.encode())
        telnet.write('exit'.encode())
    except UnboundLocalError as e:
        system('cls||clear')
        print('\033[31m{}\033[0m'.format('[-] Error. Onu is unavailable.'))
        telnet.write('exit'.encode())
        telnet.write('exit'.encode())
    except error as e:
        print(e)
        telnet.write('exit'.encode())
        telnet.write('exit'.encode())


if __name__ == "__main__":
    main()

