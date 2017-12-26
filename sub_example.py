import shlex
import subprocess


def run_command(command):
    key = []
    process = subprocess.Popen(shlex.split(command), stdout=subprocess.PIPE)
    while True:
        output = process.stdout.readline()
        if process.poll() is not None:
            break
        if output:
            key.append(output.strip())
    #rc = process.poll()
    return key


if __name__ == '__main__':
    command_create_key = 'docker run -v ovpn-data-FirstUser:/etc/openvpn --rm kylemanna/openvpn ovpn_getclient CLIENTNAME'
    key = run_command(command_create_key)
    for row in key:
        print(row.decode('ascii'))