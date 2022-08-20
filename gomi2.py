from netmiko import ConnectHandler
from collections import OrderedDict
import csv
import re

class MultiNetmiko:
    def __init__(self):
        hostlist = 'hostlist.csv'
        commandlist = 'commandlist.csv'

    def read_hostlist(self, csv_file):
        try:
            with open(csv_file, 'r') as f:
                csv_reader = csv.reader(f)
                hostlist = list(csv_reader)
        except IOError:
            print("I/O error")

    def read_commandlist(self, csv_file):
        try:
            with open(csv_file, "r") as f:
                commandlist = list(csv_reader)
        except IOError:
            print("I/O error")

    def main(self):
        mn = MultiNetmiko()
        # input ? 
        mn.read_hostlist(mn.read_hostlist)
        

if __name__ == "__main__":
    mn = MultiNetmiko()
    mn.main()


    try:
        # with open('ping_list copy.csv', 'r') as f:
        with open('ping_list.csv', 'r') as f:
            csv_reader = csv.reader(f)
            ping_list = list(csv_reader)
    except IOError:
        print("I/O error")
    del ping_list[0]

    g21j = {
        "device_type": "juniper_junos",
        "host": "10.0.220.1",
        "username": "hanabi", #### Who is the suitalbe user ?
        "password": "hanabi2008", #### Does ISPWars policy allow writing password with plain text?
    }
    
    g22j = {
        "device_type": "juniper_junos",
        "host": "10.0.220.2",
        "username": "hanabi", #### Who is the suitalbe user ?
        "password": "hanabi2008", #### Does ISPWars policy allow writing password with plain text?
    }

    g21j_conn = ConnectHandler(**g21j)
    g22j_conn = ConnectHandler(**g22j)

    g21j_vrf_list = ["GIN_AS2914-VRF", "KDDI_AS2516-VRF", "SOFTBANK_AS17676-VRF"]
    g22j_vrf_list = ["IIJ_AS2497-VRF", "OCN_AS4713-VRF", "TELSTRA_AS4637-VRF"]

    result = []

    for ping_dest in ping_list:
        result_for_each = OrderedDict()
        result_for_each["Destination"] = ping_dest[0]
        print("##########################################")
        print("##########################################")
        print("##########################################")

        for vrf in g21j_vrf_list:
            command = "ping " + ping_dest[0] + " routing-instance " + vrf + " count 5 rapid"
            output = g21j_conn.send_command(command, expect_string=">")
            print(output)
            print("##########################################")
            try:
                roundtriptime_ave = re.findall("\d*\.\d*/", output)[1].rstrip("/") #[1] is average
                result_for_each[vrf] = roundtriptime_ave
            except:
                result_for_each[vrf] = "U"

        for vrf in g22j_vrf_list:
            command = "ping " + ping_dest[0] + " routing-instance " + vrf + " count 5 rapid"
            output = g22j_conn.send_command(command, expect_string=">")
            print(output)
            print("##########################################")
            try:
                roundtriptime_ave = re.findall("\d*\.\d*/", output)[1].rstrip("/") #[1] is average
                result_for_each[vrf] = roundtriptime_ave
            except:
                result_for_each[vrf] = "U"

        result.append(result_for_each)

    g21j_conn.disconnect()
    g22j_conn.disconnect()

    # csv
    print(result)
    vrf_label = g21j_vrf_list + g22j_vrf_list
    vrf_label.insert(0, "Destination")

    try:
        with open('result.csv', 'w+') as f:
            writer = csv.DictWriter(f, fieldnames=vrf_label)
            writer.writeheader()
            for elem in result:
                writer.writerow(elem)
    except IOError:
        print("I/O error")






##### 参考 #####

# 入力
# 〇宛先リストはcsvでもらって読み込んだ
# 〇VRFも三つにする

# 処理
# 〇同じ宛先に対して3つのVRFでpingをうつ
# 〇リスト内のリストに入れ込んでいく
# 〇pingが打てなかった場合はtry:except:で拾ってUを入れる

# 出力
# 〇リストをcsv出力
# 〇列は宛先、行がVRFで3つ。左上から右下にいくイメージ

# ping 153.146.171.82 routing-instance GIN_AS2914-VRF count 5
# ping 153.146.171.82 routing-instance KDDI_AS2516-VRF count 5
# ping 153.146.171.82 routing-instance SOFTBANK_AS17676-VRF count 5
# 変数は宛先とrouting-instance


# takuya.toma@g21j.akbu> ping 153.146.171.82 routing-instance SOFTBANK_AS17676-VRF count 5                                   
# PING 153.146.171.82 (153.146.171.82): 56 data bytes
# 64 bytes from 153.146.171.82: icmp_seq=0 ttl=52 time=4.012 ms
# 64 bytes from 153.146.171.82: icmp_seq=1 ttl=52 time=4.642 ms
# 64 bytes from 153.146.171.82: icmp_seq=2 ttl=52 time=6.884 ms
# 64 bytes from 153.146.171.82: icmp_seq=3 ttl=52 time=4.495 ms
# 64 bytes from 153.146.171.82: icmp_seq=4 ttl=52 time=4.638 ms

# --- 153.146.171.82 ping statistics ---
# 5 packets transmitted, 5 packets received, 0% packet loss
# round-trip min/avg/max/stddev = 4.012/4.934/6.884/1.002 ms




# パラメータの設定 device_typeはここでは autodetect にしておく
remote_device = {'device_type': 'autodetect',
                 'host': '192.168.0.254',
                 'username': 'user',
                 'password': 'passwordpassword'}

# 自動検出
guesser = SSHDetect(**remote_device)
best_match = guesser.autodetect()

# 検出結果のデバッグ出力
print("device_type: " + best_match)

# 自動検出した device_type を再設定する
remote_device['device_type'] = best_match
connection = ConnectHandler(**remote_device)

# コマンド実行結果の出力
print(connection.send_command('show version'))

# 切断
connection.disconnect()
