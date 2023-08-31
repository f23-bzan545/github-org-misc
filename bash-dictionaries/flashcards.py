import math
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
            print(f"[WARNING]    * Unknown name: {unknown_name}")

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

    return all_dictionaries.drop_duplicates()


def break_lines(text, width):
    words = str(text).split()
    lines = []
    current_line = words[0]

    for word in words[1:]:
        if len(current_line) + len(word) + 1 <= width:
            current_line += " " + word
        else:
            lines.append(current_line)
            current_line = word

    if current_line:
        lines.append(current_line)

    return lines


def print_flashcard(text, h=4, w=30):
    lines = break_lines(text, width=w - 4)

    formatted_lines = []
    for line in lines:
        h -= 1

        n_blanks = w - len(line)
        pre_blanks = " " * (n_blanks // 2)
        post_blanks = " " * math.ceil(n_blanks / 2)
        formatted_line = "| " + pre_blanks + line + post_blanks + " |"
        formatted_lines.append(formatted_line)

    flash_card_floor = " " + "-" * (w + 2) + " "
    flash_card_rows = [flash_card_floor]

    blank_lines_below = []
    if h > 0:
        blank_line = "| " + " " * w + " |"
        n_blank_above = h // 2
        n_blank_below = math.ceil(h / 2)

        flash_card_rows.extend([blank_line] * n_blank_above)
        blank_lines_below = [blank_line] * n_blank_below

    flash_card_rows.extend(formatted_lines)
    flash_card_rows.extend(blank_lines_below)
    flash_card_rows.append(flash_card_floor)

    flash_card = "\n".join(flash_card_rows)
    print(flash_card)


# Gather and clean data
print("[INFO]    * Reading data from google sheets")
student_names = read_student_names()
dictionaries = read_bash_dictionaries()
all_dictionaries = combine_dictionaries(student_names, dictionaries)

# Find and show top 3 largest dictionaries (ties included)
print("\nLargest dictionaries:")
words_per_student = all_dictionaries.groupby("student_name").agg({"command": "count"})
words_per_student.columns = ["count"]
words_per_student["rank"] = (
    words_per_student["count"].rank(method="min", ascending=False).astype(int)
)

top_3_largest = words_per_student[words_per_student["rank"] <= 3]
print(top_3_largest[["rank", "count"]].sort_values("rank"))
print("-------------------------------------")

# print out descriptions and pause for user input to simulate flashcards
print("[INFO]    * FLASHCARD TIME!!!!\n\n")
while True:
    # pull one random row and simplify its pieces to a string
    row = all_dictionaries.sample(1)
    command = row["command"].values[0]
    description = row["description"].values[0]

    print("Definition: ")
    print_flashcard(description)
    _ = input(f"\n(enter to reveal answer)\n\n")
    print("Answer: ")
    print_flashcard(command)

    user_response = input("\n(enter to continue; type 'q'|'quit' to exit): ")
    if user_response.lower() in ["q", "quit"]:
        break
