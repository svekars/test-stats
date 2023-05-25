import os
from github import Github

token = os.environ['GITHUB_TOKEN']

g = Github(token)

pr_number = os.environ['INPUT_PR_NUMBER']

repo = g.get_repo(os.environ['GITHUB_REPOSITORY'])
pr = repo.get_pull(int(pr_number))

issue_number = pr.title.split('#')[-1].strip()
issue = repo.get_issue(int(issue_number))

labels = [label.name for label in issue.labels]

pr.set_labels(*labels)
