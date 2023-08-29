import pandas as pd


def read_student_names(
    student_info_url="https://docs.google.com/spreadsheets/d/1i9mObreN9__mEoRBTeEvUBsY4A8qpyeDtl-WqSvhzD8/export?format=csv",
):
    student_info = pd.read_csv(student_info_url)
    student_info = student_info[student_info["github_username"] != ("AdamSpannbauer")]

    student_names = student_info["first_name"] + student_info["last_name"]
    student_names = student_names.str.replace("'", "").tolist()

    return student_names


def read_bash_dictionaries(
    dictionaries_url="https://docs.google.com/spreadsheets/d/1hMq5J5g2K9PYgmp8Eyo3WJ4okGtxE1z2C3xccoJ5jvY/export?format=xlsx",
):
    dictionaries = pd.read_excel(dictionaries_url, sheet_name=None)

    # Flag unknown names in data
    unknown_names = set(dictionaries.keys()).difference(student_names)
    unknown_names = unknown_names.difference({"CoverSheet"})

    if unknown_names:
        for unknown_name in unknown_names:
            print(f"[INFO]    * Unknown name: {unknown_name}")

    return dictionaries


def combine_dictionaries(student_names, dictionaries):
    # clean dfs, calc summary stats, & combine
    clean_dictionaries = []

    for student_name in student_names:
        dictionary = dictionaries[student_name]

        # Drop blank command rows and blank description rows
        dictionary = dictionary[dictionary["command"].str.strip() != ""]
        dictionary = dictionary[dictionary["description"].str.strip() != ""]
        dictionary = dictionary[dictionary["description"].str.strip() != "..."]

        # Ensure correct columns and skip if not as expected
        try:
            dictionary = dictionary[["command", "description"]]
        except KeyError:
            print(f"[WARNING]    * Unexpected columns for {student_name}")
            continue

        # Add student name and save
        dictionary["student_name"] = student_name
        clean_dictionaries.append(dictionary)

    all_dictionaries = pd.concat(clean_dictionaries)

    return all_dictionaries


# Gather and clean data
student_names = read_student_names()
dictionaries = read_bash_dictionaries()
all_dictionaries = combine_dictionaries(student_names, dictionaries)

# Find and show top 3 largest dictionaries (ties included)
print("Largest dictionaries:")
words_per_student = all_dictionaries.groupby("student_name").agg({"command": "count"})
words_per_student.columns = ["count"]
words_per_student["rank"] = words_per_student["count"].rank(method="min").astype(int)

top_3_largest = words_per_student[words_per_student["rank"] <= 3]
print(top_3_largest[["rank", "count"]].sort_values("rank"))


# print out descriptions and pause for user input to simulate flashcards
while True:
    # pull one random row and simplify its pieces to a string
    row = all_dictionaries.sample(1)
    command = row["command"].values[0]
    description = row["description"].values[0]

    print("What bash command relates to the below description?\n")
    print(f"{description}\n")

    user_response = input("(enter to reveal answer; 'quit' to exit)")
    if user_response == "quit":
        break

    print(f"{command}\n")
