import csv
import datetime as dt
from logging import DEBUG
from logging import Formatter
from logging import getLogger
from logging import StreamHandler
import os
from typing import Callable
from typing import Dict
from typing import List

import netmiko
from netmiko.ssh_autodetect import SSHDetect
from netmiko.ssh_dispatcher import ConnectHandler
from netmiko import utilities as netutil

import ping3 as ping


HOSTLIST = 'hostlist.csv'
COMMANDLIST = 'commandlist.csv'

ping.EXCEPTIONS = True


class CSVOperator:

    def read_hostlist(self, csv_file: str = None) -> List[Dict[str, str]]:
        if not csv_file:
            csv_file = HOSTLIST

        try:
            with open(csv_file, 'r') as f:
                hostdict = csv.DictReader(f)
                hostlist = list(hostdict)
                return hostlist

        except IOError:
            print(f'I/O error: {csv_file}\n')

    def read_commandlist(self, csv_file: str = None) -> List[List[str]]:
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

    def __init__(self) -> None:
        self.logger = self.setup_logger()

    def setup_logger(self) -> Callable:
        logger = getLogger(__name__)
        logger.setLevel(DEBUG)

        sh = StreamHandler()
        sh.setLevel(DEBUG)
        sh_formatter = Formatter(
            '%(asctime)s - %(levelname)s - %(funcName)s - %(message)s',
            '%Y-%m-%d %H:%M:%S')
        sh.setFormatter(sh_formatter)

        logger.addHandler(sh)
        logger.propagate = False
        return logger

    def connect_autodetect(self, hostinfo: Dict[str, str], loginfo: str) -> Callable:
        remote_device = {'device_type': 'autodetect',
                         'host': hostinfo.get("host"),
                         'username': hostinfo.get("username"),
                         'password': hostinfo.get("password"),
                         'secret': hostinfo.get("secret"),
                         'session_log': loginfo}
        self.logger.debug(remote_device)
        detector = SSHDetect(**remote_device)
        remote_device['device_type'] = detector.autodetect()
        connection = ConnectHandler(**remote_device)
        return connection

    def make_logdir(self, timeinfo: str) -> str:
        logdir = f'log-{timeinfo}'
        netutil.ensure_dir_exists(logdir)
        return logdir

    def make_loginfo(self, timeinfo: str, **hinfo) -> str:
        dir = self.make_logdir(timeinfo)
        loginfo = f'{dir}/{hinfo.get("host")}-{timeinfo}-JST.log'
        return loginfo

    def rename_logfile(self, key: str, loginfo: str) -> None:
        loginfo_renamed = loginfo.rstrip('.log') + f'-{key}.log'
        os.rename(loginfo, loginfo_renamed)

    def ping_check(self, target_ip: str) -> None:
        try:
            # TODO linuxで実験
            ping.ping(target_ip, timeout=0.5)
        except ping.errors.Timeout:
            error_msg = 'PingTimeout'
            self.logger.error(f'{error_msg}: {target_ip}')
        except ping.errors.TimeToLiveExpired:
            error_msg = 'PingTTLExpired'
            self.logger.error(f'{error_msg}: {target_ip}')
        except ping.errors.PingError:
            error_msg = 'PingUnreachable'
            self.logger.error(f'{error_msg}: {target_ip}')
        except Exception:
            self.logger.error(f'Error: {target_ip}')
        else:
            msg = 'PingSuccess'
            self.logger.info(f'{msg}: {target_ip}')

    def multi_send_command(self, conn: Callable, commandlist: List[List[str]]) -> str:
        conn.enable()
        for command in commandlist:
            conn.enable()
            print(f'{"="*30} {command[0]} @{conn.host} {"="*30}')
            output = ''
            output += conn.send_command(command[0],
                                        strip_prompt=False,
                                        strip_command=False) + '\n'
            print(output)
            print(f'{"="*80}\n')
        return output

    def multi_connections(self, hostlist: List[Dict[str, str]], commandlist: List[List[str]]) -> None:
        dt_now = dt.datetime.now(dt.timezone(dt.timedelta(hours=9)))
        dt_now = dt_now.strftime('%Y%m%d-%H%M%S')

        for hinfo in hostlist:
            loginfo = self.make_loginfo(dt_now, **hinfo)

            try:
                conn = self.connect_autodetect(hinfo, loginfo)
                self.multi_send_command(conn, commandlist)
                conn.disconnect()

            except netmiko.NetMikoAuthenticationException:
                self.ping_check(hinfo.get("host"))
                error_msg = 'SSHAuthenticationError'
                self.logger.error(f'{error_msg}: {hinfo.get("host")}\n')
                self.rename_logfile(error_msg, loginfo)

            except netmiko.NetMikoTimeoutException:
                self.ping_check(hinfo.get("host"))
                error_msg = 'SSHTimeoutError'
                self.logger.error(f'{error_msg}: {hinfo.get("host")}\n')
                self.rename_logfile(error_msg, loginfo)

            except Exception:
                self.ping_check(hinfo.get("host"))
                error_msg = 'Error'
                self.logger.error(f'{error_msg}: {hinfo.get("host")}\n')
                self.rename_logfile(error_msg, loginfo)

            else:
                success_msg = 'SuccessfullyDone'
                self.logger.info(f'{success_msg}: {hinfo.get("host")}\n')


def main():
    csv_ope = CSVOperator()
    hlist = csv_ope.read_hostlist()
    clist = csv_ope.read_commandlist()

    netmiko_ope = NetmikoOperator()
    netmiko_ope.multi_connections(hlist, clist)


if __name__ == '__main__':
    main()
