import os.path

import requests
import subprocess
from api import get_data

def handle_data(data, config):
    for user_info in data:
        username, public_key = user_info['username'], user_info['public_key']
        userdir = os.path.join(config['client']['base_dir'], username)

        # 检查用户是否存在
        user_exists = subprocess.call(['id', username], stdout=subprocess.PIPE, stderr=subprocess.PIPE) == 0
        authorized_keys_file = f'{userdir}/.ssh/authorized_keys'
        if user_exists:
            result = subprocess.check_output(['getent', 'passwd', username], universal_newlines=True)

            # 分析输出以获取登录 shell
            user_info = result.strip().split(':')
            login_shell = user_info[-1]

            # 检查登录 shell 是否是禁止登录的
            if login_shell == '/usr/sbin/nologin':
                subprocess.call(["usermod", "-s", "/bin/bash", username])
            # 如果用户存在，检查公钥是否一致
            with open(authorized_keys_file, 'r') as f:
                existing_keys = f.read()

            if public_key not in existing_keys:
                # 公钥不一致，替换系统上的公钥
                with open(authorized_keys_file, 'a') as f:
                    f.write(public_key + '\n')
        else:
            # 如果用户不存在，创建用户并复制公钥
            subprocess.call(['useradd', username])
            subprocess.call(['mkdir -p', userdir])
            subprocess.call(['chown', f'{username}:{username}', userdir])
            subprocess.call(['chmod', '700', f'{userdir}/.ssh'])
            with open(authorized_keys_file, 'w') as f:
                f.write(public_key + '\n')
            subprocess.call(['chown', f'{username}:{username}', authorized_keys_file])
            subprocess.call(['chmod', '600', authorized_keys_file])

            # 检查是否有用户需要禁用
    known_username_list = [user_info['username'] for user_info in data] + config['white_list']
    current_users = subprocess.check_output(['awk', '-F:', '{print $1}', '/etc/passwd'], text=True).split(
        '\n')

    for user in current_users:
        if user not in known_username_list:
            subprocess.call(["usermod","-s","/usr/sbin/nologin",user])


def job(config):
    print("fetching data")
    data = get_data(config)
    if data:
        handle_data(data['data'], config)
