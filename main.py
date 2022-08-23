import csv
import datetime as dt
import os
import netmiko
from netmiko.ssh_autodetect import SSHDetect
from netmiko.ssh_dispatcher import ConnectHandler



HOSTLIST = 'netmiko-multiple-connections-with-csv/hostlist.csv'
COMMANDLIST = 'netmiko-multiple-connections-with-csv/commandlist.csv'



class CSVOperator:

    def read_hostlist(self, csv_file = None):
        if not csv_file:
            csv_file = HOSTLIST

        try:
            with open(csv_file, 'r') as f:
                hostdict = csv.DictReader(f)
                hostlist = list(hostdict)
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
                        'host': hostinfo.get("host"),
                        'username': hostinfo.get("username"),
                        'password': hostinfo.get("password")}
        detector = SSHDetect(**remote_device)
        remote_device['device_type'] = detector.autodetect()
        connection = ConnectHandler(**remote_device)
        return connection 

    def make_loginfo(self, **hinfo):
        dt_now = dt.datetime.now(dt.timezone(dt.timedelta(hours=9))).strftime('%Y%m%d-%H%M%S')
        dir = f'log-{dt_now}'
        if not (os.path.exists(dir)):
            os.mkdir(dir)
        logfile = f'{dir}/{hinfo.get("host")}-{dt_now}-JST.log'
        return logfile

    def notify_except(self, keyword, logfile, **hinfo):
        message = f'{keyword}: {hinfo.get("host")}\n'
        print(message)
        logfile = logfile.rstrip('.log') + f'-{keyword}.log'
        with open(logfile, 'a') as f:
            f.write(message)

    def multi_connections(self, hostlist, commandlist):
        for hinfo in hostlist:
            output = ''
            logfile = self.create_loginfo(**hinfo)

            try:
                conn = self.connect_autodetect(hinfo)

                for command in commandlist:
                    output += conn.find_prompt() + command[0] + '\n'
                    output += conn.send_command(command[0]) + '\n'
                    print(output)
                
                with open(logfile, 'a') as f:
                    f.write(output)

            except netmiko.NetMikoAuthenticationException:
                self.notify_except('SSHAuthenticationError', logfile, **hinfo)

            except netmiko.NetMikoTimeoutException:
                self.notify_except('SSHTimeoutError', logfile, **hinfo)

            except:
                self.notify_except('PerformCommandErros', logfile, **hinfo)
            
            conn.disconnect()




def main():
    csv_ope = CSVOperator()
    hlist = csv_ope.read_hostlist()
    clist = csv_ope.read_commandlist()

    netmiko_ope = NetmikoOperator()
    netmiko_ope.multi_connections(hlist, clist)



if __name__ == '__main__':
    main()
