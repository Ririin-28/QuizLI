import os
import sqlite3
from docx import Document
import pyfiglet
from rich.console import Console
from rich.text import Text

DB_FILE = "quizli_results.db"

def list_word_files(folder):
    return [f for f in os.listdir(folder) if f.endswith(".docx")]

def parse_quiz(file_path):
    document = Document(file_path)
    quiz = []
    current_question = None

    for paragraph in document.paragraphs:
        text = paragraph.text.strip()
        if text:
            if text.startswith("Q:"): # Question
                if current_question:
                    quiz.append(current_question)
                current_question = {"question": text[2:].strip(), "options": [], "answer": None}
            elif text.startswith("-") and current_question:  # Multiple Choices
                current_question["options"].append(text[1:].strip())
            elif text.startswith("A:") and current_question:  # Answer
                current_question["answer"] = text[2:].strip()

    if current_question:
        quiz.append(current_question)

    return quiz

def run_quiz(quiz):
    score = 0
    for idx, item in enumerate(quiz, start=1):
        print(f"Question {idx}: {item['question']}")
        if item["options"]: 
            for opt_idx, option in enumerate(item["options"], start=0):
                letter = chr(65 + opt_idx)
                print(f"{letter}. {option}")

        user_answer = input("Your Answer: ").strip().upper()
        correct_answer = item["answer"]

        if user_answer in "ABCD":
            opt_idx = ord(user_answer) - 65
            if 0 <= opt_idx < len(item["options"]):
                user_answer = item["options"][opt_idx]
        if user_answer.lower() == correct_answer.lower():
            print("Correct!\n")
            score += 1
        else:
            print(f"Wrong! The correct answer is: {correct_answer}\n")
    print(f"\nYour Final Score is: {score}/{len(quiz)}")
    return score

def save_results(file_name, score, total_questions):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO results (file_name, score, total_questions)
        VALUES (?, ?, ?)
    """, (file_name, score, total_questions))
    conn.commit()
    conn.close()

def display_title():
    console = Console()


    figlet_title = pyfiglet.figlet_format("QuizLI")

    gradient_colors = ["red", "yellow", "green", "cyan", "blue", "magenta"]
    figlet_lines = figlet_title.splitlines()
    for i, line in enumerate(figlet_lines):
        color = gradient_colors[i % len(gradient_colors)]
        console.print(Text(line, style=color))

    print("=" * 50)
    print("Welcome to QuizLI - A CLI Quiz Experience!")
    print("=" * 50)

def main():
    display_title()

    start_choice = input("Type 'start' to play or 'exit' to quit: ").strip().lower()
    if start_choice != "start":
        print("Goodbye!")
        return

    folder = input("Enter the folder path containing Word files: ").strip()
    if not os.path.exists(folder):
        print("Folder does not exist.")
        return

    word_files = list_word_files(folder)
    if not word_files:
        print("No Word files found in the folder.")
        return

    print("Available Word files:")
    for idx, file_name in enumerate(word_files, start=1):
        print(f"{idx}. {file_name}")

    choice = input("Select a file by number: ").strip()
    if not choice.isdigit() or int(choice) < 1 or int(choice) > len(word_files):
        print("Invalid choice.")
        return

    selected_file = word_files[int(choice) - 1]
    file_path = os.path.join(folder, selected_file)

    quiz = parse_quiz(file_path)
    if not quiz:
        print("No questions found in the selected file.")
        return

    print("\nStarting the quiz...\n")
    score = run_quiz(quiz)

    save_results(selected_file, score, len(quiz))
    print(f"Results saved! File: {selected_file}, Score: {score}/{len(quiz)}")

if __name__ == "__main__":
    main()