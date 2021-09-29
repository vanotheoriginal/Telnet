#!/usr/bin/python3
from os import error, system
import telnetlib
import time
import sys
from mdlog import log
import subprocess
import re
import asyncio


mac_address = ''

def getmac(buff):
    buff = buff.split('\n')
    mac = buff[2].split()
    mac = mac[2]
    return mac



def find(arr, substring):

    val = 0
    if substring == 'MAC Address':
                
        pattern = re.compile(r'(?:[0-9a-fA-F]-?){12}')
        res = []
        for i in arr:
            res.append(re.findall(pattern, str(i).lower()))
        
        res = [x for x in res if x]
        if len(res) > 1:
            return '\033[31m{}\033[0m'.format('\n[!] More than one mac address found.\n')
        else:
            for i in arr:
                if substring in i:
                    val = arr.index(i)
            return '{}\n{}\n{}\n'.format(arr[val], arr[val + 1], arr[val + 2])
    
    else:
        for i in arr:
            if substring in i:
                val = arr.index(i)
        return '{}\n{}\n{}\n'.format(arr[val], arr[val + 1], arr[val + 2])
    


def subcheck(i, command, port, telnet, sep, watch_string):

    telnet.write('{}\n'.format(command.format(port)).encode())
    time.sleep(0.5)
    
    print('Iteration: ', i, '\nCommand:', command, '\nWatch string:', watch_string)
    if i < 3:
        telnet.write(b'q\n')

    data = telnet.read_very_eager()
    data = data.decode('utf-8')
    data = data.splitlines()
    #buff = [x for x in data if x]
    print(data)
    
    print(sep)
    print(find(data, watch_string))

    if i == 4:
        global mac_address
        mac_address = find(buff, 'MAC Address')




async def check(port, telnet):
    
    commands_q = ['show ports {}', 'show error ports {}', 'show fdb port {}', 'show vlan ports {}']
    watch_strings = ['MDI', 'RX Frames', 'Untagged', 'MAC Address']
    separator = '=' * 76
    
    async_tasks = []
    
    for i in range(len(commands_q)): 
        async_tasks.append(subcheck(i, commands_q[i], port, telnet, separator, watch_strings[i]))
    
    wait_tasks = asyncio.wait(async_tasks)
    await wait_tasks
    print(separator)


    

def reload_port(port, telnet):
    commands_q = ['config ports {} state disable', 'clear counters ports {}', 'config ports {} state enable']
    for i in commands_q:
        telnet.write('{}\n'.format(i.format(port)).encode())
        time.sleep(0.5)

    print('\n[+] Port {} has been restarted.\n'.format(port))
    
    
    
def change_vlan(port, telnet, vlanid_old, vlanid_new):
    commands_q = ['config vlan vlanid {} delete {}', 'config vlan vlanid {} add untagged {}']

    telnet.write('{}\n'.format(commands_q[0].format(vlanid_old, port)).encode())
    time.sleep(0.5)
    telnet.write('{}\n'.format(commands_q[1].format(vlanid_new, port)).encode())
    time.sleep(0.5)

    print('\n[+] Port: \033[36m{}\033[0m  Vlan \033[36m{}\033[0m changed to \033[36m{}\033[0m.\n'.format(port, vlanid_old, vlanid_new))



def cab_diag(port, telnet, var):

    bind = ['   OK   ', 'Pair1', 'Pair2', 'Pair3', 'Pair4', 'Pair 1', 'Pair 2', 'Pair 3', 'Pair 4', 'No Cable']
    res = ''
    b = ''
    if var == 0:
        command = 'cable diagnostic port {}'
    else:
        command = 'cable_diag ports {}'

    telnet.write('{}\n'.format(command.format(port)).encode())
    time.sleep(0.5)

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
        separator = '--------------------------------------------------------------------------'
        print(separator)
        print('Cable Diagnostics Port: \033[34m{}\033[0m'.format(port))
        print(res)
        print(separator, '\n')
    else:
        cab_diag(port, telnet, 1)
    
 


def connect_term(telnet, host='10.3.12.8'):
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




def main():
    
    try:

        if len(sys.argv) < 3:
            print('\033[31m{}\033[0m'.format('[-] Invalid aguments.'))
            sys.exit(0)

        switch = sys.argv[1]
        port = sys.argv[2]

        print('Switch: {}  Port: {}'.format(switch, port))
        
        try:
            telnet = telnetlib.Telnet(switch)
            connect_term(telnet, switch)
        except TimeoutError as e:
            print('\033[31m{}\033[0m'.format('[-] Timeout error, switch unavailable.'))
            

        re = ''


        while True:

            requestline = '\033[34m<r>\033[0m - reload port | \033[34m<c>\033[0m - cab diag | \033[34m<l>\033[0m - last logs | \033[34m<d>\033[0m - dhcp\n\033[34m<v>\033[0m - change vlan | \033[34m<Enter>\033[0m - refresh \n'

            if re == 'r':
                reload_port(port, telnet)
                print(requestline)
                re = input('[+] > ')

            elif re == 'c':
                cab_diag(port, telnet, 0)
                print(requestline)
                re = input('[+] > ')

            elif re == 'l':
                log(telnet, switch, port)
                print(requestline)
                re = input('[+] > ')

            elif re == 'd':
                system('cls||clear')
                dhcp(getmac(mac_address))
                print(requestline)
                re = input('[+] > ')
                
            elif re == 'v':
                vlanid_old = input('[+] Old vlan id > ')
                vlanid_new = input('[+] New vlan id > ')
                change_vlan(port, telnet, vlanid_old, vlanid_new)
                print(requestline)
                re = input('[+] > ')

            else:
                system('cls||clear')
                print('[+] Telnet Connected')

                loop = asyncio.get_event_loop()
                loop.run_until_complete(check(port, telnet))
                loop.close()

                print('Switch: \033[36m{}\033[0m  Port: \033[36m{}\033[0m'.format(switch, port))
                print(requestline)
                re = input('[+] > ')
    
    except KeyboardInterrupt as e:
        system('cls||clear')
        print('[+] Keyboard Interrupt. Exited.')
        telnet.write('logo'.encode())  
    except BrokenPipeError as e:
        system('cls||clear')
        print('\033[31m{}\033[0m'.format('[-] Error. Switch session terminated'))
    except EOFError as e:
        system('cls||clear')
        print('\033[31m{}\033[0m'.format('[-] Error. Telnet connection closed'))
    except error as e:
        system('cls||clear')
        print(e)
        telnet.write('logo'.encode())


if __name__ == "__main__":
    main()
