import os
import requests
import csv

token = os.environ.get("GITHUB_TOKEN")

base_url = 'https://api.github.com'

#add list of repositories
repositories = [
    {"owner": "svekars", "repo": "test-stats"},
    {"owner": "svekars", "repo": "odyssey-project"}
]

label_points = {
    "easy": 2,
    "medium": 5,
    "advanced": 15
}

half_point_pr_numbers = {
    "svekars/test-stats": [8, 11]
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
        "labels": "easy,medium,advanced",
        "per_page": 100,
    }
    merged_pull_requests = []
    for page in range(1, 6): #adding pagination to bypass 100 requests limitation of GitHub API
        params["page"] = page
        response = requests.get(url.format(owner=owner, repo=repo), headers=headers, params=params)
        pull_requests = response.json()
        merged_pull_requests += [pr for pr in pull_requests if pr.get("merged_at")]
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
            repo_key = f"{owner}/{repo}"
            pr_number = pr["number"]
            if repo_key in half_point_pr_numbers and pr_number in half_point_pr_numbers[repo_key]:
                points = sum(label_points[label] * 0.5 for label in labels if label in label_points)
            else:
                points = sum(label_points[label] for label in labels if label in label_points)
            pr_url = pr["html_url"]
            

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
