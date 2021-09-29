#!/usr/bin/python3
from os import error, system
import telnetlib
import time
import sys

 

def connect_term(telnet):
    try:
        telnet.write(b'login\n')
        telnet.write(b'password'\n')
    except error as e:
        print('[-] Error: ' + e)




def check(telnet):
    b = ''
    commands = ['en', 'show ont-find list interface gpon all']
                  
    for i in commands:
        telnet.write('{}\n'.format(i).encode())
        time.sleep(0.5)
        data = telnet.read_very_eager()
        data = data.decode('utf-8')
        b = b + data

    b = b.splitlines()
    buff = [x for x in b if x]
    
    return buff
    

def find(arr, substring):
    for i in arr:
        if substring in i:
            val = arr.index(i)
    return val



def filter_ports(vport, telnet):
    
    port_buff = list()
    telnet.write('show ont brief interface gpon all\n'.encode())

    for i in range(30):
        time.sleep(0.1)
        data = telnet.read_very_eager()
        data = data.decode('utf-8')
        data = data.splitlines()
        
        for i in data:
            if vport in i:
                port_buff.append(i)
        telnet.write(b'n\n')
        
    return port_buff




def register_onu(port, serial, telnet, ip_type):
    commands = ['configure terminal', 'deploy profile rule', 
                'aim {}', 'permit sn string-hex {} line 1 default line 1', 'active',
                'exit', 'exit', 'exit', 'copy running-config startup-config', 'y']
                  
    for i in commands[:2]:
        telnet.write('{}\n'.format(i).encode())
        time.sleep(0.2)
        
    telnet.write('{}\n'.format(commands[2].format(port)).encode())
    time.sleep(0.2)
    
    if ip_type == 'r':
        telnet.write('{}\n'.format(commands[3].format(serial)).encode())
    else:
        telnet.write('{}\n'.format(commands[3].format(serial).replace('1', '4')).encode())
    time.sleep(0.2)
    
    b = ''
    
    for i in commands[4:]:
        telnet.write('{}\n'.format(i).encode())
        time.sleep(0.2)
        #data = telnet.read_very_eager()
        #data = data.decode('utf-8')
        #b = b + data
        
    #b = b.splitlines()
    buff = [x for x in b if x]
    #for j in buff:
    #    print(j)
    #print(find_result(buff, 'Config success'))
    
    
    #Update startup config successfully.





    
def find_result(buff, substring):
    success = ''
    for i in buff:
        if substring in i:
            success = i
    return '{}\n'.format(success)




def main():
        
    stack = dict()

    try:

        if len(sys.argv) < 2:
            print('\033[31m{}\033[0m'.format('[-] Invalid aguments.'))
            raise KeyboardInterrupt

        olt = sys.argv[1]
        
        telnet = telnetlib.Telnet(olt)
        connect_term(telnet)
 
        system('cls||clear')
        print('Olt: \033[36m{}\033[0m'.format(olt))

        
        buff = check(telnet)
        up_border = find(buff, 'Port')
        down_border = find(buff, 'Total entries')
        
        
        buff = buff[up_border + 1: down_border]
        
        for i in range(len(buff)):
            print(' \033[36m{}\033[0m. {}'.format(i, buff[i]))
            vport = buff[i].split()[0]
            sn = buff[i].split()[2]
            stack['{}'.format(i)]=(vport, sn)
            
        choise = input('[+] Choose ont > ')
        ip_type = input('[+] Real IP or NAT? r/n > ')
        
        if int(choise) in [i for i in range(len(buff))]:
         
            vport = stack['{}'.format(int(choise))][0]
            print('Virtual port: \033[36m{}\033[0m'.format(vport))
            
            vport = vport[1:]
            port_buff = filter_ports(vport, telnet)
            
            for i in port_buff:
                print(i)
                
            last_port = port_buff[-1].split()[0]
            print('Last port: ', last_port)
            
            commit = last_port.split('/')
            commit = commit[-1]
            
            port_to_commit = last_port[:-1] + str((int(commit) + 1))
            
            print('Port to be chosen: \033[36m{}\033[0m'.format(port_to_commit))
            confirm = input('[+] Commit onu registration? y/N > ')
            
            if confirm == 'y':
                serial = stack['{}'.format(int(choise))][1]
                register_onu(port_to_commit, serial, telnet, ip_type)
                print('\n[+] Registered \033[36m{}\033[0m  Port: \033[36m{}\033[0m\n'.format(serial, port_to_commit))
            else:
                print('\033[31m{}\033[0m'.format('[-] Operation canceled.'))
                time.sleep(1)
                raise KeyboardInterrupt
             
        else:
            print('\033[31m{}\033[0m'.format('[-] Invalid input.'))
            raise KeyboardInterrupt


    except KeyboardInterrupt as e:
        system('cls||clear')
        print('[+] Keyboard Interrupt. Exited.')
        telnet.write('exit'.encode())
        telnet.write('exit'.encode())
    except error as e:
        print(e)
        telnet.write('exit'.encode())
        telnet.write('exit'.encode())


if __name__ == "__main__":
    main()

