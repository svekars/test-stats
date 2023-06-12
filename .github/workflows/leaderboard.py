import os
import requests
import csv
from datetime import datetime

token = os.environ.get("GITHUB_TOKEN")

base_url = 'https://api.github.com'

#add list of repositories
repositories = [
    {"owner": "pytorch", "repo": "tutorials"},
    {"owner": "pytorch", "repo": "examples"}
]

label_points = {
    "easy": 2,
    "medium": 5,
    "advanced": 10
}

manual_pull_requests = [
     {"repo": "test-stats", "pr_number": "8", "author": "svekars", "label": "easy"},
     {"repo": "test-stats", "pr_number": "11", "author": "svekars", "label": "medium"}
]

def get_pull_requests(owner, repo):
    url = f'{base_url}/repos/{owner}/{repo}/pulls?state=closed'
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    params = {
        "state": "closed",
        "base": "main",
        "labels": "easy,medium,advanced",
        "per_page": 100,
    }
    merged_pull_requests = []
    for page in range(1, 6): #adding pagination to bypass 100 requests limitation of GitHub API
        params["page"] = page
        response = requests.get(url.format(owner=owner, repo=repo), headers=headers, params=params)
        pull_requests = response.json()
        for pr in pull_requests:
            opened_at = pr.get("created_at")
            merged_at = pr.get("merged_at")
            if opened_at and merged_at:
                opened_date = datetime.strptime(opened_at, "%Y-%m-%dT%H:%M:%SZ").date()
                merged_date = datetime.strptime(merged_at, "%Y-%m-%dT%H:%M:%SZ").date()

                start_open_date = datetime(2023, 5, 31).date()
                end_open_date = datetime(2023, 5, 11).date()
                start_merge_date = datetime(2023, 5, 31).date()
                end_merge_date = datetime(2023, 6, 15).date()

                pst = timezone("US/Pacific")
                start_open_date = pst.localize(datetime.combine(start_open_date, datetime.min.time()))
                end_open_date = pst.localize(datetime.combine(end_open_date, datetime(17, 0)))
                start_merge_date = pst.localize(datetime.combine(start_merge_date, datetime.min.time()))
                end_merge_date = pst.localize(datetime.combine(end_merge_date, datetime.max.time()))

                if start_open_date <= opened_date <= end_open_date and start_merge_date <= merged_date <= end_merge_date:
                    merged_pull_requests.append(pr)
    return merged_pull_requests
    
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
                if pr_url not in author_data[author]["pr_links"]:
                    author_data[author]["points"] += points
                    author_data[author]["pr_links"].append(pr_url)
            else:
                author_data[author] = {"points": points, "pr_links": [pr_url]}
            
for pr in manual_pull_requests:
     pr_number = pr["pr_number"]
     repo = pr["repo"]
     author = pr["author"]
     label = pr["label"]

     points = label_points.get(label, 0)
     if author in author_data:
         points = (points + 1) // 2 # Give half points to the PRs listed in manual_pull_requests
     pr_url = f"https://github.com/{owner}/{repo}/pull/{pr_number}"

     if author in author_data:
         author_data[author]["points"] += points
         author_data[author]["pr_links"].append(pr_url)
     else:
         author_data[author] = {"points": points, "pr_links": [pr_url]}

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

print(f"Leaderboard saved to {csv_filename}")

markdown_table = "| Author | Points | PR |\n"
markdown_table += "|--- | --- | ---|\n"
for author, data in sorted_authors:
    points = data["points"]
    pr_links = f"{', '.join(data['pr_links'])} |"
    markdown_table += f"| {author} | {points} | {pr_links} |\n"

markdown_filename = "leaderboard.md"

with open(markdown_filename, "w", newline="") as file:
    file.write(markdown_table)

print(f"Leaderboard saved to {markdown_filename}")
