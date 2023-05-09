from datetime import datetime, timedelta
from github import Github

g = Github("<add-token>")

repo_name = "svekars/test-stats"
repo = g.get_repo(repo_name)

unassigned_issues = []

issues = repo.get_issues(labels=["test"])

for issue in issues:
    if issue.assignee is not None:
        assignee = issue.assignee
        assignee_login = assignee.login
        for pr in repo.get_pulls(state="all"):
            if assignee_login == pr.user.login and issue.number in [int(i.number) for i in pr.get_issue_comments()]:
                print(f"Issue #{issue.number} is assigned and has a related PR")
                break
        else:
            assignee_time = assignee.created_at
            if assignee_time > datetime.utcnow() - timedelta(days=3):
                issue.edit(assignee=None)
                unassigned_issues.append(issue.number)
                print("Issue #{issue.number} has an unresponsive assignee and was unnasigned.")
            else:
                print("Issue #{issue.number} has been assigned on {assignee_time} UTC)")


if unassigned_issues:
    print(f"The following issues have been unassigned due to lack of activity and they are now up for grabs:")
    for issue_number in unassigned_issues:
        issue_url = f"{repo.html_url}/issues/{issue_number}"
        print(f"- [Issue #{issue_number}]({issue_url})")
else:
    print("No issues have been unassigned due to lack of activity.")
