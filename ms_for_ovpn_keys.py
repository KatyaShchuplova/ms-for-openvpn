import os
import pymysql
import shlex
import subprocess


def get_connection():
    connection = pymysql.connect(host='192.168.0.61', user='admin', password='admin', db='openvpn',
                                 cursorclass=pymysql.cursors.DictCursor)
    return connection


def get_login_on_id(connection, owner_id):
    with connection.cursor() as cursor:
        sql_select_login = "SELECT login FROM users WHERE id = %d" % owner_id
        cursor.execute(sql_select_login)
        for row in cursor:
            login = row['login']
            return login


def get_port_on_id(connection, owner_id):
    with connection.cursor() as cursor:
        sql_select_port = "SELECT port FROM users WHERE id = %d" % owner_id
        cursor.execute(sql_select_port)
        for row in cursor:
            port = int(row['port'])
            return port


def run_command(command):
    key = []
    process = subprocess.Popen(shlex.split(command), stdout=subprocess.PIPE)
    while True:
        output = process.stdout.readline()
        if process.poll() is not None:
            break
        if output:
            key.append(output.strip())
    return key


def get_key_as_list(name, key_name):
    ovpn_data = "ovpn-data-" + name
    os.system('docker run -v %s:/etc/openvpn --rm -it kylemanna/openvpn easyrsa build-client-full %s nopass' %
              (ovpn_data, key_name))
    command_create_key = 'docker run -v %s:/etc/openvpn --rm kylemanna/openvpn ovpn_getclient %s' %\
                         (ovpn_data, key_name)
    key = run_command(command_create_key)
    print('key created!')
    return key


# key creation function
def create_new_key():
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            sql_select = "SELECT * FROM `keys` WHERE isCreated = False"
            cursor.execute(sql_select)
            for row in cursor:
                try:
                    print(row)
                    login = get_login_on_id(connection, row['owner_id'])
                    port = get_port_on_id(connection, row['owner_id'])
                    new_key = get_key_as_list(login, row['unique_name'])
                    key_in_db = ''
                    for i in new_key:
                        if "1194 udp" in i.decode('ascii'):
                            new_port = "remote 192.168.0.61 %d udp" % (port)
                            key_in_db += new_port
                        else:
                            key_in_db += i.decode('ascii')
                            key_in_db += '\n'
                    sql_update_key = "Update `keys` SET `key` = '%s' WHERE id = %d" % (key_in_db, row['id'])
                    cursor.execute(sql_update_key)
                    sql_update_is_created = "Update `keys` SET isCreated = True WHERE id = %d" % row['id']
                    cursor.execute(sql_update_is_created)
                    connection.commit()
                except:
                    print("Error. No key created")
    finally:
        connection.close()


# key revocation function
def revoke_key():
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            sql_select = "SELECT * FROM `keys` WHERE status like 'delete' and is_revoked like '0'"
            cursor.execute(sql_select)
            for row in cursor:
                try:
                    login = get_login_on_id(connection, row['owner_id'])
                    ovpn_data = "ovpn-data-" + login
                    os.system('docker run --rm -it -v %s:/etc/openvpn kylemanna/openvpn ovpn_revokeclient %s'
                              % (ovpn_data, row['unique_name']))
                    sql_update_is_retrieved = "Update `keys` SET is_revoked = True WHERE id = %d" % row['id']
                    cursor.execute(sql_update_is_retrieved)
                    connection.commit()
                    print("Key is revoked")
                except:
                    print("Error. Key not revoked")
    finally:
        connection.close()


def main():
    create_new_key()
    revoke_key()


if __name__ == '__main__':
    main()