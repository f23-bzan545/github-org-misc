import pandas as pd

student_info_url = "https://docs.google.com/spreadsheets/d/1i9mObreN9__mEoRBTeEvUBsY4A8qpyeDtl-WqSvhzD8/export?format=csv"
student_info = pd.read_csv(student_info_url)
student_info = student_info[student_info["github_username"] != ("AdamSpannbauer")]

student_names = student_info["first_name"] + student_info["last_name"]

starter_dictionary = pd.DataFrame(
    [
        {
            "command": "pwd",
            "description": "prints the path to current working directory",
        },
        {
            "command": "cd",
            "description": "changes working directory; allows to navigate the file system",
        },
        {
            "command": "ls",
            "description": "...",
        },
        {
            "command": "ls -a",
            "description": "...",
        },
        {
            "command": "ls -l",
            "description": "...",
        },
    ]
)

with pd.ExcelWriter("bash-dictionaries.xlsx") as writer:
    for student_name in student_names:
        starter_dictionary.to_excel(writer, index=False, sheet_name=student_name)
