import requests
import json
token = "add-your-token"

owner = "pytorch"
repo = "tutorials"

issues = {2: "Easy", 3: "Medium", 4: "Hard"}
difficulty_map = {"Easy": "easy", "Medium": "medium", "Hard": "hard"}

issues = {11111: "Medium", TBA}

for issue, difficulty in issues.items():
    url = f"https://api.github.com/repos/pytorch/tutorials/issues/{issue}/labels"
    headers =  {"Authorization": f"Token {token}", "Accept": f"application/vnd.github.v3+json"}
    label = difficulty_map.get(difficulty)
    if label:
        payload = [label]
        try:
            response = requests.post(url, headers=headers, json=payload)
            if response.status_code == 200:
                print(f"Label '{label}' applied")
            else:
                print(f"Error: {response.content}")
        except requests.exceptions.RequestException as e:
            print(f"Failed to apply label to issue {issue}. Error: {e}")
    else:
        print(f"No label for issue {issue} with difficulty '{difficulty}'.")
