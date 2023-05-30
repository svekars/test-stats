import requests
import os

pr_number = os.getenv("GITHUB_REF").split("/")[-1]
pr_url = f"https://api.github.com/repos/{os.getenv('GITHUB_REPOSITORY')}/pulls/{pr_number}"

response = requests.get(pr_url)
response.raise_for_status()
pr_data = response.json()
issue_number = None

if pr_data["body"]:
    for word in pr_data["body"].split():
        if word.startswith("#"):
            issue_number = word.strip("#")
            break

if issue_number:
    # Get the labels of the referenced issue
    issue_url = f"https://api.github.com/repos/{os.getenv('GITHUB_REPOSITORY')}/issues/{issue_number}"
    response = requests.get(issue_url)
    response.raise_for_status()
    issue_data = response.json()
    
    if "test" in [label["name"] for label in issue_data["labels"]]:
        # Assign labels from the issue to the pull request
        labels_url = f"https://api.github.com/repos/{os.getenv('GITHUB_REPOSITORY')}/issues/{pr_number}/labels"
        labels = [label["name"] for label in issue_data["labels"]]
        payload = {"labels": labels}
        response = requests.post(labels_url, json=payload, headers={"Authorization": f"Bearer {os.getenv('GITHUB_TOKEN')}"})
        response.raise_for_status()
    else:
        print(f"No 'test' label in issue #{issue_number}")
