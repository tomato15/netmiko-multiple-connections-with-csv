import os
import csv
import datetime as dt
from logging import getLogger, StreamHandler, Formatter, DEBUG
import netmiko
from netmiko import utilities as netutil
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


    def __init__(self):
        self.logger = self.setup_logger()


    def setup_logger(self):
        logger = getLogger(__name__)
        logger.setLevel(DEBUG)

        sh = StreamHandler()
        sh.setLevel(DEBUG)
        sh_formatter = Formatter('%(asctime)s - %(levelname)s - %(funcName)s - %(message)s', '%Y-%m-%d %H:%M:%S')
        sh.setFormatter(sh_formatter)

        logger.addHandler(sh)
        logger.propagate = False
        return logger


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


    def make_logdir(self, timeinfo):
        logdir = f'log-{timeinfo}'
        netutil.ensure_dir_exists(logdir)
        return logdir


    def make_loginfo(self, timeinfo, **hinfo):
        dir = self.make_logdir(timeinfo)
        loginfo = f'{dir}/{hinfo.get("host")}-{timeinfo}-JST.log'
        return loginfo


    def rename_logfile(self, key, loginfo):
        loginfo_renamed = loginfo.rstrip('.log') + f'-{key}.log'
        os.rename(loginfo, loginfo_renamed)


    def multi_send_command(self, conn, commandlist):
        for command in commandlist:
            print(f'{"="*30} {command[0]} @{conn.host} {"="*30}')
            output = ''
            output += conn.find_prompt() + command[0] + '\n'
            output += conn.send_command(command[0]) + '\n'            
            print(output)
        return output


    def multi_connections(self, hostlist, commandlist):
        dt_now = dt.datetime.now(dt.timezone(dt.timedelta(hours=9))).strftime('%Y%m%d-%H%M%S')

        for hinfo in hostlist:
            loginfo = self.make_loginfo(dt_now, **hinfo)

            try:
                conn = self.connect_autodetect(hinfo, loginfo)
                self.multi_send_command(conn, commandlist)                
                conn.disconnect()

            except netmiko.NetMikoAuthenticationException as e:
                self.logger.error(f'SSHAuthenticationError: {conn.host}\n')
                self.rename_logfile('SSHAuthenticationError', loginfo)

            except netmiko.NetMikoTimeoutException as e:
                self.logger.error(f'SSHTimeoutError: {conn.host}\n')
                self.rename_logfile('SSHTimeoutError', loginfo)

            except Exception as e:
                self.logger.error(f'Error: {conn.host}\n')
                self.rename_logfile('Error', loginfo)

            else:
                self.logger.info(f'SuccessfullyDone: {conn.host}\n')



def main():
    csv_ope = CSVOperator()
    hlist = csv_ope.read_hostlist()
    clist = csv_ope.read_commandlist()

    netmiko_ope = NetmikoOperator()
    netmiko_ope.multi_connections(hlist, clist)


if __name__ == '__main__':
    main()
