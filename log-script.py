#!/usr/bin/python3
from os import error, system
import telnetlib
import time
from multiprocessing import Process
import sys



def check_anim():
    for i in range(4):
        print('\r[+] Checking logs ', end='')
        time.sleep(0.12) 
        print('\r[<] Checking logs ', end='')
        time.sleep(0.12) 
        print('\r[-] Checking logs ', end='')
        time.sleep(0.12) 
        print('\r[>] Checking logs ', end='')
        time.sleep(0.12) 
        print('\r[+] Checking logs ', end='')
        time.sleep(0.12) 
        print('\r[<] Checking logs ', end='')
        time.sleep(0.12) 
        print('\r[-] Checking logs ', end='')
        time.sleep(0.12) 
        print('\r[>] Checking logs ', end='')
    print('\r[+] Complete.          ')



def check_log(telnet, port, restr):
    res = check(port, telnet)
    print('\n')
    if restr == 1:
        for i in res[0:1]:
            for j in i:
                print(j)
    else:
        for i in res:
            for j in i:
                print(j)
        
    if not res:
        print('[-] No logs found for \033[36m{}\033[0m port'.format(port))
    sys.exit()



def find(arr, substring):
    buff = list()
    substring_case = substring.casefold()
    for i in arr:
        if substring in i or substring_case in i:
            buff.append(i.strip())
    return buff



def check(port, telnet):
    
    main_buff = list()
    telnet.write('show log\n'.encode())

    for i in range(30):
        time.sleep(0.1)
        data = telnet.read_very_eager()
        data = data.decode('utf-8')
        data = data.splitlines()

        res = find(data, 'Port {} '.format(port))
        main_buff.append(res)
        telnet.write(b'n\n')
  
  
    
    telnet.write(b'q\n')
    main_buff = [j for j in main_buff if j]
    return main_buff



def connect_term(telnet):
    try:
        telnet.write(b'login\n')
        telnet.write(b'password\n')
        print('[+] Connected Telnet')
    except error as e:
        print('[-] Error: ' + e)



def main():
    
    restr = 0
    if len(sys.argv) < 3:
        print('\033[31m{}\033[0m'.format('[-] Invalid aguments.'))
        sys.exit(0)

    if len(sys.argv) == 4:
        if sys.argv[3] == '-q':
            restr = 1

    try:

        switch = sys.argv[1]
        port = sys.argv[2]

        system('cls||clear')
        print('Switch: \033[36m{}\033[0m  Port: \033[36m{}\033[0m port'.format(switch, port))

        telnet = telnetlib.Telnet(switch)
        connect_term(telnet)
        time.sleep(0.5)

        Process(target=check_log, args=(telnet, port, restr)).start()
        Process(target=check_anim).start()
        

    except KeyboardInterrupt as e:
        print('\033[36m{}\033[0m'.format('\n[+] Keyboard Interrupt. Exited.'))
        telnet.write('logo'.encode())
    except error as e:
        print(e)
        telnet.write('logo'.encode())


if __name__ == "__main__":
    main()
