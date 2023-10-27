import requests
token = ""


def get_token(config):
    url = f"{config['server']['addr']}/api/token/"

    response = requests.post(url=url,
                             data={
                                 'username': config['server']['username'],
                                 'password': config['server']['password']
                             })

    if response.status_code != 200:
        print(f"get token error with status code {response.status_code}")
        return None

    data = response.json()
    if data['code'] != 0:
        print(f"get token failed with code {data['code']},msg:{data['msg']}")
        return None
    print(f"get token success")
    return data['data']['access_token']


def get_data(config):
    server_name = config['client']['name']
    global token
    if token == "":
        token = get_token(config)
    retries = 0
    max_retries = 2
    while retries < max_retries:
        retries += 1

        # 发起http请求
        url = f"{config['server']['addr']}/api/server-use-list/?server_name={server_name}"
        print(token)
        headers = {
            'User-Agent': 'Apifox/1.0.0 (https://apifox.com)',
            'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNjk4NDA5MDQyLCJpYXQiOjE2OTg0MDg3NDIsImp0aSI6ImVjOTk0NWQwMTljNjQzYTE5MTEwMTQ2ZDA3NTgxNmMxIiwidXNlcl9pZCI6Mn0.H8YObA_TzWBp5MBSJ3Hj4MuTXMY5T3OtuP6Jv4gp6aw',
            'Accept': '*/*',
            'Host': 'localhost:8000',
            'Connection': 'keep-alive'
        }

        server_use = requests.get(url=url, headers=headers)
        if server_use.status_code != 200:
            print(f"run error with status code {server_use.status_code}")
            return None
        data = server_use.json()

        if data['code'] == 4003 and retries == 1:
            token = get_token(config)
            continue

        if data['code'] != 0:
            print(f"get data error with code {data['code']},msg:{data['msg']}")
            return None

        print(f"fetching data success")
        print(f"get {len(data['data'])} data")
        return data

    return None
