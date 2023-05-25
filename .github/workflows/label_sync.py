import os
import sys
from github import Github

token = os.environ['GITHUB_TOKEN']

g = Github(token)

pr_number = sys.argv[1]

repo = g.get_repo(os.environ['GITHUB_REPOSITORY'])
pr = repo.get_pull(int(pr_number))

issue_number = pr.title.split('#')[-1].strip()
issue = repo.get_issue(issue_number)

labels = [label.name for label in issue.labels]

pr.set_labels(*labels)
