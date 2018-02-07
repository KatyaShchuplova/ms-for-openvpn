import os
import pymysql

PATH_MS_CONTINUE_FLAG = 'ms_continue_flag'


def get_connection():
    connection = pymysql.connect(host='192.168.0.61', user='admin', password='admin', db='openvpn',
                                 cursorclass=pymysql.cursors.DictCursor)
    return connection


def create_docker(name, port):
    try:
        OVPN_DATA = "ovpn-data-" + name
        VPN_ADDRESS = '192.168.0.61'
        # initialize the OVPN_DATA container
        os.system('docker volume create --name %s' % OVPN_DATA)
        os.system('docker run -v %s:/etc/openvpn --rm kylemanna/openvpn ovpn_genconfig -u udp://%s' % (
        OVPN_DATA, VPN_ADDRESS))
        os.system("echo 'set_var EASYRSA_CERT_EXPIRE     3' > /var/lib/docker/volumes/%s/_data/vars" % OVPN_DATA)
        os.system("echo 'set_var EASYRSA_REQ_CN          \"%s\"' >> /var/lib/docker/volumes/%s/_data/vars" % (
        name, OVPN_DATA))
        os.system("echo 'set_var EASYRSA_BATCH           \"\"' >> /var/lib/docker/volumes/%s/_data/vars" % OVPN_DATA)
        os.system("unix2dos /var/lib/docker/volumes/%s/_data/vars" % (OVPN_DATA))
        os.system('docker run -v %s:/etc/openvpn --rm -it kylemanna/openvpn ovpn_initpki nopass' % OVPN_DATA)
        # start OpenVPN server process
        os.system(
            'docker run -v %s:/etc/openvpn -d -p %d:1194/udp --cap-add=NET_ADMIN kylemanna/openvpn' % (OVPN_DATA, port))
    except:
        print("docker wasn't created")


def main():
    while True:
        with open(PATH_MS_CONTINUE_FLAG, "r") as file:
            for line in file:
                if "#" in line:
                    continue
                if "Stop" in line:
                    exit()
        connection = get_connection()
        try:
            with connection.cursor() as cursor:
                sql_select = "SELECT * FROM users WHERE vpnCreated = False LIMIT 1"
                cursor.execute(sql_select)
                for row in cursor:
                    try:
                        create_docker(row['login'], row['port'])
                        sql_update = "Update users SET vpnCreated = 1 WHERE id = %d " % (row['id'])
                        cursor.execute(sql_update)
                        connection.commit()
                    except:
                        print("docker wasn't created")
        finally:
            connection.close()


if __name__ == '__main__':
    main()