import subprocess
from tqdm import tqdm
import pandas as pd

TA_GH_USERNAME = "abdullah-salau"


def create_repo(repo_name="test"):
    # create private repo with github cli: https://cli.github.com/manual/gh_repo_create
    # eg: `gh repo create {repo_name} --private --gitignore Python --add-readme`
    # eg: `gh repo create gh-cli-test --private --gitignore Python --add-readme`
    command = f"gh repo create {repo_name} --private --gitignore Python --add-readme"
    subprocess.run(command, shell=True, check=True)


def add_user_to_repo(repo_name="test", user_name="bmewing"):
    # add collaborator to repo
    # eg: `gh api --method=PUT 'repos/{owner_user_name}/{repo_name}/collaborators/{user_name}'`
    # eg: `gh api --method=PUT 'repos/AdamSpannbauer/gh-cli-test/collaborators/bmewing' -f permission=admin`
    command = f"gh api --method=PUT 'repos/AdamSpannbauer/{repo_name}/collaborators/{user_name}'"
    subprocess.run(command, shell=True, check=True)


student_info_url = "https://docs.google.com/spreadsheets/d/1i9mObreN9__mEoRBTeEvUBsY4A8qpyeDtl-WqSvhzD8/export?format=csv"
student_info = pd.read_csv(student_info_url)

student_info = student_info[student_info["github_username"] != ("AdamSpannbauer")]
student_info = student_info[~student_info["github_username"].isna()]
student_info = student_info.reset_index(drop=True)

for i, row in tqdm(student_info.iterrows(), total=student_info.shape[0]):
    repo_name = row["bonus_repo_name"]
    user_name = row["github_username"]

    print(f"attempting to create {repo_name} for {user_name}")

    create_repo(repo_name)
    add_user_to_repo(repo_name, user_name)
    add_user_to_repo(repo_name, TA_GH_USERNAME)
