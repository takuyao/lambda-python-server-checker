import json
import requests
import boto3

BUCKET_NAME = 'xxxxxxxxxx'
OBJECT_NAME = 'xxxxxxxxxx/servers.json'
SLACK_POST_URL = 'https://hooks.slack.com/services/xxxxxxxxxx/xxxxxxxxxx/xxxxxxxxxxxxxxxxxxxx'

def lambda_handler(event, context):
    json_data = __getServers()
    __check_server(json_data)

def __getServers():
   s3 = boto3.resource('s3')
   obj = s3.Object(BUCKET_NAME, OBJECT_NAME)
   response = obj.get()
   body = response['Body'].read()
   return body.decode('utf-8')

def __check_server(json_data):
    data = json.loads(json_data)
    servers = data['servers']

    has_error = False

    for server in servers:
        name = server['name']
        url = server['url']
        print("Check: " + name)

        try:
            r = requests.get(url)
            if r.status_code != 200:
                __send_error_message(name, url)
                has_error = True
        except requests.exceptions.RequestException as e:
            __send_request_error_message(name, url)
            has_error = True

    if has_error == False:
        __send_success_message()

def __send_error_message(name, url):
    payload = {
        "text": name + '\n' + url + '\n' + '*ERROR!*',
        "icon_emoji": ":x:"
    }
    __send_message(payload)

def __send_request_error_message(name, url):
    payload = {
        "text": name + '\n' + url + '\n' + '*Request Error!*',
        "icon_emoji": ":warning:"
    }
    __send_message(payload)

def __send_success_message():
    payload = {
        "text": "All Servers OK!",
        "icon_emoji": ":o:"
    }
    __send_message(payload)

def __send_message(payload):
    try:
        return requests.post(SLACK_POST_URL, json=payload)
    except requests.exceptions.RequestException as e:
        return None
