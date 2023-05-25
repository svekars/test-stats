import os
from github import Github

token = os.environ['GITHUB_TOKEN']

g = Github(token)

pr_number = os.environ['{{ github.event.pull_request.number }}']
repo = g.get_repo('{{ github.repository }}')
pr = repo.get_pull(pr_number)

issue_number = pr.title.split('#')[-1].strip()

issue = repo.get_issue(issue_number)

labels = [label.name for label in issue.labels]

pr.set_labels(*labels)
