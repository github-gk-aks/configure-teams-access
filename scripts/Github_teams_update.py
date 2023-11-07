from github import Github
import pandas as pd
import os

github_token = os.environ.get("GITHUB_TOKEN")

if github_token is None:
    raise ValueError("GitHub token not found. Please set the GITHUB_TOKEN environment variable.")

# Authenticate with your GitHub token
g = Github(github_token)

# Your organization or enterprise name
org_name = "github-gk-aks"
org = g.get_organization(org_name)

# Load data from your Excel file into a Pandas DataFrame
data = pd.read_excel("data/Input.xlsx")

# Create an empty dictionary to keep track of team permissions
team_permissions = {}

# Iterate through the data rows
for _, row in data.iterrows():
    repo_name = row["Repository Name"]
    team_name = row["Team Names"]
    permission = row["Permission"]

    # If the repository is not in the dictionary, create an empty list
    if repo_name not in team_permissions:
        team_permissions[repo_name] = []

    # Add the team and permission to the list
    team_permissions[repo_name].append({"team": team_name, "permission": permission})

# Iterate through the dictionary and associate teams with repositories
for repo_name, teams in team_permissions.items():
    repo = org.get_repo(repo_name)

    for team_data in teams:
        team_name = team_data["team"]
        permission = team_data["permission"]

        team = org.get_team_by_slug(team_name)

        if team:
            if permission == "push":
                team.update_team_repository(repo, "push")
            elif permission == "admin":
                team.update_team_repository(repo, "admin")
            elif permission == "pull":
                team.update_team_repository(repo, "pull")
            else:
                print(f"Invalid permission for team {team_name}: {permission}")
        else:
            print(f"Team {team_name} not found in the organization.")
