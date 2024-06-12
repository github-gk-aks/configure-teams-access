from github import Github
import pandas as pd
import os
import sys

github_token = os.environ.get("GITHUB_TOKEN")
github_workspace = os.getenv('GITHUB_WORKSPACE')
repo_path = './source-repo'

# Read and replace teams in the CODEOWNERS file
excel_path = os.path.join(github_workspace, repo_path, "data/Input.xlsx")

if github_token is None:
    raise ValueError("GitHub token not found. Please set the GITHUB_TOKEN environment variable.")

# Authenticate with your GitHub token
g = Github(github_token)

# Your organization or enterprise name
org_name = 'github-gk-aks'
org = g.get_organization(org_name)

# Load data from your Excel file into a Pandas DataFrame
data = pd.read_excel(excel_path)

# Create an empty dictionary to keep track of team permissions
team_permissions = {}

# Create a list to keep track of the results
results = []

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
    try:
        repo = org.get_repo(repo_name)
        repo_result = {"repository": repo_name, "teams": []}

        for team_data in teams:
            team_name = team_data["team"]
            permission = team_data["permission"]

            try:
                team = org.get_team_by_slug(team_name)
                if team:
                    if permission == "push":
                        team.update_team_repository(repo, "push")
                    elif permission == "admin":
                        team.update_team_repository(repo, "admin")
                    elif permission == "pull":
                        team.update_team_repository(repo, "pull")
                    else:
                        repo_result["teams"].append({"team": team_name, "status": f"Invalid permission: {permission}"})
                        continue
                    repo_result["teams"].append({"team": team_name, "status": "success"})
                else:
                    repo_result["teams"].append({"team": team_name, "status": "Team not found"})
                    continue
            except GithubException as e:
                # Handle exception if the team is not found or other errors
                if e.status == 404:
                    repo_result["teams"].append({"team": team_name, "status": "Team not found"})
                else:
                    repo_result["teams"].append({"team": team_name, "status": f"Failed: {str(e)}"})

        results.append(repo_result)
    except GithubException as e:
        results.append({"repository": repo_name, "status": f"Failed: {str(e)}"})

# Write the results to a CSV file
results_df = pd.DataFrame(results)
results_df.to_csv("data/team_update_results.csv", index=False)

# Print the results
for result in results:
    print(result)
