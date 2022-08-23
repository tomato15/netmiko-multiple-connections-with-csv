import csv
import datetime as dt
import os
import netmiko
from netmiko.ssh_autodetect import SSHDetect
from netmiko.ssh_dispatcher import ConnectHandler



HOSTLIST = 'hostlist.csv'
COMMANDLIST = 'commandlist.csv'



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
            print(f'I/O error: {csv_file}\n')


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
            print(f'I/O error: {csv_file}\n')



class NetmikoOperator:


    def connect_autodetect(self, hostinfo, loginfo):
        remote_device = {'device_type': 'autodetect',
                        'host': hostinfo.get("host"),
                        'username': hostinfo.get("username"),
                        'password': hostinfo.get("password"),
                        'session_log': loginfo}
        detector = SSHDetect(**remote_device)
        remote_device['device_type'] = detector.autodetect()
        connection = ConnectHandler(**remote_device)
        return connection 


    def make_loginfo(self, timeinfo, **hinfo):
        dir = f'log-{timeinfo}'
        if not (os.path.exists(dir)):
            os.mkdir(dir)
        loginfo = f'{dir}/{hinfo.get("host")}-{timeinfo}-JST.log'
        return loginfo


    def notify_except(self, keyword, exception, loginfo, **hinfo):
        msg_str = f'{keyword}: {hinfo.get("host")}\n'
        print(f'{"="*60}\n {exception}\n {msg_str}\n')
        loginfo_error = loginfo.rstrip('.log') + f'-{keyword}.log'
        os.rename(loginfo, loginfo_error)


    def multi_connections(self, hostlist, commandlist):
        dt_now = dt.datetime.now(dt.timezone(dt.timedelta(hours=9))).strftime('%Y%m%d-%H%M%S')

        for hinfo in hostlist:
            loginfo = self.make_loginfo(dt_now, **hinfo)

            try:
                conn = self.connect_autodetect(hinfo, loginfo)

                for command in commandlist:
                    output = ''
                    output += conn.find_prompt() + command[0] + '\n'
                    output += conn.send_command(command[0]) + '\n'
                    print(f'{"="*60}\n {output}\n')
                
                conn.disconnect()

            except netmiko.NetMikoAuthenticationException as e:
                self.notify_except('SSHAuthenticationError', e, loginfo, **hinfo)

            except netmiko.NetMikoTimeoutException as e:
                self.notify_except('SSHTimeoutError', e, loginfo, **hinfo)

            except Exception as e:
                self.notify_except('PerformCommandErros', e, loginfo, **hinfo)



def main():
    csv_ope = CSVOperator()
    hlist = csv_ope.read_hostlist()
    clist = csv_ope.read_commandlist()

    netmiko_ope = NetmikoOperator()
    netmiko_ope.multi_connections(hlist, clist)



if __name__ == '__main__':
    main()
