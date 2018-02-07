import os

PATH_MS_CONTINUE_FLAG = 'ms_keys_continue_flag'


def main():
    while True:
        with open(PATH_MS_CONTINUE_FLAG, "r") as file:
            for line in file:
                if "#" in line:
                    continue
                if "Stop" in line:
                    exit()
        os.system("python3 ms_for_ovpn_users.py")
        os.system("python3 ms_for_ovpn_keys.py")


if __name__ == '__main__':
    main()