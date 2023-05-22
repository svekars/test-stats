import os
import requests
import csv

token = os.environ.get("GITHUB_TOKEN")

url = "https://api.github.com/repos/{owner}/{repo}/pulls?state=closed"

#add least of repositories
repositories = [
    {"owner": "svekars", "repo": "test-stats"},
    {"owner": "svekars", "repo": "odyssey-project"}
]

label_points = {
    "easy": 2,
    "medium": 5,
    "advanced": 15
}

def get_pull_requests(owner, repo):
    url = f'{base_url}/repos/{owner}/{repo}/pulls?state=closed'
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    params = {
        "state": "closed",
        "base": "main",
        "labels": "test,easy,medium,advanced",
        "per_page": 100,
    }
    
    response = requests.get(url, headers=headers, params=params)
    pull_requests = []
    if response.status_code == 200:
        data = response.json()
        for pull_request in data:
            labels = [label['name'] for label in pull_request['labels']]
            if 'test' in labels and any(label in labels for label in ['easy', 'medium', 'advanced']):
                if pull_request.get('merged', False):
                    pr_number = pull_request['number']
                    pr_url = pull_request['html_url']
                    title = pull_request['title']
                    pull_requests.append((pr_number, title, pr_url))
    else:
        print(f'Error: {response.status_code} - {response.text}')

    return pull_requests
    
author_data = {}

for repository in repositories:
    owner = repository["owner"]
    repo = repository["repo"]
    pull_requests = get_pull_requests(owner, repo)
    for pr in pull_requests:
        if "user" in pr and "login" in pr["user"]:
            author = pr["user"]["login"]
        elif "author" in pr and "login" in pr["author"]:
            author = pr["author"]["login"]
        else:
            continue

        labels = [label["name"] for label in pr["labels"]]
        if "test" in labels:
            points = sum(label_points[label] for label in labels if label in label_points)
            pr_url = pr["html_url"]

            if author in author_data:
                author_data[author]["points"] += points
                author_data[author]["pr_links"].append(pr_url)
            else:
                author_data[author] = {"points": points, "pr_links": [pr_url]}
            #author_points[author] = author_points.get(author, 0) + points

sorted_authors = sorted(author_data.items(), key=lambda x: x[1]["points"], reverse=True)

csv_data = [("Author", "Points", "Pull Requests")]
for author, data in sorted_authors:
    points = data["points"]
    pr_links = ",\n".join(data["pr_links"])
    csv_data.append((author, points, pr_links))

csv_filename = "leaderboard.csv"

with open(csv_filename, "w", newline="") as file:
    writer = csv.writer(file)
    writer.writerows(csv_data)

print(f"Leaderoard saved to {csv_filename}")

markdown_table = "| Author | Points | PR |\n"
markdown_table += "|--- | --- | ---|\n"
for author, data in sorted_authors:
    points = data["points"]
    pr_links = f"{', '.join(data['pr_links'])} |"
    markdown_table += f"| {author} | {points} | {pr_links} \n"
    
markdown_filename = "leaderboard.md"

with open(markdown_filename, "w", newline="") as file:
    file.write(markdown_table)

print(f"Leaderoard saved to {markdown_filename}") 
