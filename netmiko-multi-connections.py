#! python3.6
#! netmiko==4.0.0
import netmiko
from netmiko.ssh_autodetect import SSHDetect
from netmiko.ssh_dispatcher import ConnectHandler
import csv
import datetime as dt



HOSTLIST = 'hostlist.csv'
COMMANDLIST = 'commandlist.csv'



class CSVOperator:

    def read_hostlist(self, csv_file = None):
        if not csv_file:
            csv_file = HOSTLIST

        try:
            with open(csv_file, 'r') as f:
                csv_reader = csv.reader(f)
                hostlist = list(csv_reader)
                del hostlist[0]
                return hostlist
        except IOError:
            print(f'I/O error: {csv_file}')

    def read_commandlist(self, csv_file = None):
        if not csv_file:
            csv_file = COMMANDLIST

        try:
            with open(csv_file, 'r') as f:
                csv_reader = csv.reader(f)
                commandlist = list(csv_reader)
                del commandlist[0]
                return commandlist
        except IOError:
            print(f'I/O error: {csv_file}')



class NetmikoOperator:

    def connect_autodetect(self, hostinfo):

        remote_device = {'device_type': 'autodetect',
                        'host': hostinfo[0],
                        'username': hostinfo[1],
                        'password': hostinfo[2]}

        guesser = SSHDetect(**remote_device)
        remote_device['device_type'] = guesser.autodetect()
        connection = ConnectHandler(**remote_device)
        return connection 



if __name__ == '__main__':

    csv_ope = CSVOperator()
    hlist = csv_ope.read_hostlist()
    clist = csv_ope.read_commandlist()

    netmiko_ope = NetmikoOperator()

    for hinfo in hlist:
        output = ''
        dt_now = dt.datetime.now(dt.timezone(dt.timedelta(hours=9))).strftime('%Y%m%d-%H%M%S')
        logname = f'{hinfo[0]}-{dt_now}-JST.log'

        try:
            conn = netmiko_ope.connect_autodetect(hinfo)

            for command in clist:
                # print(command) find_promptいれるとping、tracerouteできない
                # output += conn.find_prompt() + command[0] + '\n'
                # print(output)
                output += conn.send_command(command[0]) 
                print(output)
            
            with open(logname, 'a') as f:
                f.write(output)

            conn.disconnect()

        except netmiko.NetMikoAuthenticationException:
            print(f'SSH authentication error: {hinfo[0]}\n')
            logname = f'{hinfo[0]}-{dt_now}-JST-SSHAuthenticationError.log'
            with open(logname, 'a') as f:
                f.write(output)

        except netmiko.NetMikoTimeoutException:
            print(f'SSH timeout error: {hinfo[0]}\n')
            logname = f'{hinfo[0]}-{dt_now}-JST-SSHTimeoutError.log'
            with open(logname, 'a') as f:
                f.write(output)

        except:
            print(f'Error: Fail to perform commands: {hinfo[0]}\n')
            logname = f'{hinfo[0]}-{dt_now}-JST-SendCommandError.log'
            with open(logname, 'a') as f:
                f.write(output)



