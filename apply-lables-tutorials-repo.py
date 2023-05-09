import requests
import json
token = "<add-your-token>"

owner = "pytorch"
repo = "tutorials"

labels = "my-test-label"

issue_numbers = [TBA]

for issue_number in issue_numbers:
    url = f"https://api.github.com/repos/pytorch/tutorials/issues/{issue_number}/labels"
    headers =  {"Authorization": f"Token {token}", "Accept": f"application/vnd.github.v3+json"}
    payload = [labels]
    response = requests.post(url, headers=headers, json=payload)
    if response.status_code == 200:
        print(f"Label '{labels}' applied")
    else:
        print(f"Error: {response.content}")
