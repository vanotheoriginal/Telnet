#!/usr/bin/python3
from os import error, system
import telnetlib
import time
import sys
from mdlog import log
import subprocess
import re




mac_address = ''

def getmac(buff):
    return buff.split('\n')[2].split()[2]



def find(arr, substring):
    for i in arr:
        if substring in i:
            val = arr.index(i)
    return '{}\n{}\n{}\n'.format(arr[val], arr[val + 1], arr[val + 2])



def connect_term(telnet):
    try:
        telnet.write(b'login\n')
        telnet.write(b'password\n')
    except error as e:
        print('[-] Error: ' + e)



def dhcp(mac):
    mac = mac.replace('-', ':')	
    subprocess.call(['dhcpd', mac])
    subprocess.call(['dhcpd2', mac])
    print('\n')



def reload_port(port, telnet):
    commands_q = ['config ports {} state disable', 'clear counters ports {}', 'config ports {} state enable']
    for i in commands_q:
        telnet.write('{}\n'.format(i.format(port)).encode())
        time.sleep(0.25)

    print('\n[+] Port {} has been restarted.\n'.format(port))
    
    
    
def change_vlan(port, telnet, vlanid_old, vlanid_new):
    commands_q = ['config vlan vlanid {} delete {}', 'config vlan vlanid {} add untagged {}']

    telnet.write('{}\n'.format(commands_q[0].format(vlanid_old, port)).encode())
    time.sleep(0.25)
    telnet.write('{}\n'.format(commands_q[1].format(vlanid_new, port)).encode())
    time.sleep(0.25)

    print('\n[+] Port: \033[36m{}\033[0m  Vlan \033[36m{}\033[0m changed to \033[36m{}\033[0m.\n'.format(port, vlanid_old, vlanid_new))




def find_mac(arr, substring):
    for i in arr:
        if substring in i:
            val = arr.index(i)
            
    pattern = re.compile(r'(?:[0-9a-fA-F]-?){12}')
    res = list()

    for i in arr:
        mac = re.findall(pattern, str(i).lower())
        res.append(mac)
    
    res = [x for x in res if x]
    if len(res) > 1:
        return '\033[31m{}\033[0m'.format('\n[!] More than one mac address found.\n')
    else:
        for i in arr:
            if substring in i:
                val = arr.index(i)
        return '{}\n{}\n{}\n'.format(arr[val], arr[val + 1], arr[val + 2])

    



def check(port, telnet, timer):
    b = ''
    commands_q = ['show ports {}', 'show error ports {}', 'show fdb port {}', 'show vlan ports {}']
    for i in commands_q:
        telnet.write('{}\n'.format(i.format(port)).encode())
        time.sleep(timer)
        data = telnet.read_very_eager()
        data = data.decode('utf-8')
        b = b + data

        if int(commands_q.index(i)) < 2:
            telnet.write(b'q\n')

    b = b.splitlines()
    buff = [x for x in b if x]

    separator = '='*88
    global mac_address
    mac_address = find_mac(buff, 'MAC Address')

    print(separator, '\n', find(buff, 'MDI'), '\n', separator, sep='')
    print(find(buff, 'RX Frames'), '\n', separator, sep='')
    print(find(buff, 'Untagged'), '\n', separator, sep='')
    print(mac_address, '\n', separator, sep='')
  



def cab_diag(port, telnet, var):

    bind = ['   OK   ', 'Pair1', 'Pair2', 'Pair3', 'Pair4', 'Pair 1', 'Pair 2', 'Pair 3', 'Pair 4', 'No Cable']
    res = ''
    b = ''
    if var == 0:
        command = 'cable diagnostic port {}'
    else:
        command = 'cable_diag ports {}'

    telnet.write('{}\n'.format(command.format(port)).encode())
    time.sleep(0.25)

    data = telnet.read_very_eager()
    data = data.decode('utf-8')
    b = b + data

    b = b.splitlines()
    buff = [x for x in b if x]

    for i in buff:
        for j in bind:
            if j in i:
                res = res + '\n' + i

    if len(res) > 1:
        separator = '-'*88
        print(separator)
        print('Cable Diagnostics Port: \033[34m{}\033[0m'.format(port))
        print(res)
        print(separator, '\n')
    else:
        cab_diag(port, telnet, 1)
    



def main(index=0):    
    try:

        if len(sys.argv) < 3:
            print('\033[31m{}\033[0m'.format('[-] Invalid aguments.'))
            sys.exit(0)

        switch = sys.argv[1]
        port = sys.argv[2]

        print('Switch: {}  Port: {}'.format(switch, port))
        
        try:
            telnet = telnetlib.Telnet(switch)
            connect_term(telnet)
        except TimeoutError as e:
            print('\033[31m{}\033[0m'.format('[-] Timeout error, switch unavailable.'))
            

        re = ''
        timer = 0.25
        if index != 0:
            timer = 0.5

        while True:

            requestline = '\033[34m<r>\033[0m - reload port | \033[34m<c>\033[0m - cab diag | \033[34m<l>\033[0m - last logs | \033[34m<d>\033[0m - dhcp | \033[34m<v>\033[0m - change vlan\n\033[34m<Enter>\033[0m - refresh \n'
            console_line = 'input:\033[34m~\033[0m$ '
            
            if re == 'r':
                reload_port(port, telnet)
                print(requestline)
                re = input(console_line)

            elif re == 'c':
                cab_diag(port, telnet, 0)
                print(requestline)
                re = input(console_line)

            elif re == 'l':
                log(telnet, switch, port)
                print(requestline)
                re = input(console_line)

            elif re == 'd':
                system('cls||clear')
                dhcp(getmac(mac_address))
                print(requestline)
                re = input(console_line)
                
            elif re == 'v':
                vlanid_old = input('[+] Old vlan id > ')
                vlanid_new = input('[+] New vlan id > ')
                change_vlan(port, telnet, vlanid_old, vlanid_new)
                print(requestline)
                re = input(console_line)

            else:
                system('cls||clear')
                print('[+] Connected')
                check(port, telnet, timer)
                print('Switch: \033[36m{}\033[0m  Port: \033[36m{}\033[0m'.format(switch, port))
                print(requestline)
                re = input(console_line)
    
    except KeyboardInterrupt as e:
        system('cls||clear')
        telnet.write('logo'.encode())  
    except BrokenPipeError as e:
        system('cls||clear')
        print('\033[31m{}\033[0m'.format('[-] Error. Switch session terminated'))
    except EOFError as e:
        system('cls||clear')
        print('\033[31m{}\033[0m'.format('[-] Error. Telnet connection closed'))
    except UnboundLocalError as e:
        main(index=1)
    except error as e:
        system('cls||clear')
        print('\033[31m{}\033[0m'.format('[-] Error: {}'.format(e)))
        telnet.write('logo'.encode())


if __name__ == "__main__":
    main()
