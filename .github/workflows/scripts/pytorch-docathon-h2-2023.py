import os
import requests
import csv

token = os.environ.get("GITHUB_TOKEN")

base_url = 'https://api.github.com'

dir = "./pytorch/h2-2023"

os.makedirs(dir, exist_ok=True)
print(f"Directory '{dir}' created." if os.path.exists(dir) else f"Directory '{dir}' already exists.")


# add list of repositories
repositories = [
    {"owner": "pytorch", "repo": "pytorch"},
    {"owner": "pytorch", "repo": "tutorials"},
]

label_points = {
    "easy": 2,
    "medium": 5,
    "advanced": 10,
    "full-advanced": 20, # hack to give full credit. Can be removed later
}

manual_pull_requests = [
#     {"repo": "", "pr_number": "", "author": "", "label": ""},
]

def get_pull_requests(owner, repo):
    url = f'{base_url}/repos/{owner}/{repo}/pulls'
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
        response = requests.get(url, headers=headers, params=params)
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
        if "docathon-h2-2023" in labels:
            points = sum(label_points[label] for label in labels if label in label_points)
            pr_url = pr["html_url"]

            if author in author_data:
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

csv_filename = "./pytorch/h2-2023/leaderboard-pytorch-docathon-h2-2023.csv"

with open(csv_filename, "w", newline="") as file:
    writer = csv.writer(file)
    writer.writerows(csv_data)

print(f"Leaderboard saved to {csv_filename}")

markdown_table = "| Author | Points | PR |\n"
markdown_table += "|--- | --- | ---|\n"
for author, data in sorted_authors:
    points = data["points"]
    pr_links = f"{', '.join(data['pr_links'])} |"
    markdown_table += f"| {author} | {points} | {pr_links} \n"

markdown_filename = "./pytorch/h2-2023/leaderboard-pytorch-docathon-h2-2023.md"

with open(markdown_filename, "w", newline="") as file:
    file.write(markdown_table)

print(f"Leaderboard saved to {markdown_filename}")
