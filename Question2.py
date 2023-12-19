import json
import matplotlib.pyplot as plt
from collections import defaultdict
import seaborn as sns

def load_json(json_file_path):
    """Load JSON data from a file."""
    with open(json_file_path, 'r') as file:
        data = json.load(file)
    return data
from pygments.lexers import get_lexer_for_filename, guess_lexer
from pygments.util import ClassNotFound

def detect_language(code):
    try:
        # Use the guess_lexer method to automatically detect the lexer based on the code content
        lexer = guess_lexer(code)
        return lexer.name
    except ClassNotFound:
        # If automatic detection fails, you can try using get_lexer_for_filename with a dummy filename
        # Provide a filename with a known extension related to the language if possible
        lexer = get_lexer_for_filename("dummy.txt")
        return lexer.name

def preprocess_data(issue_data):
    """Clean and preprocess issue data."""
    for issue in issue_data["Sources"]:
        issue["RepoLanguage"] = clean_text(issue.get("RepoLanguage"))
        issue["State"] = clean_text(issue.get("State"))
    return issue_data

def clean_text(text):
    """Clean text by removing unwanted characters."""
    if text is not None:
        cleaned_text = text.encode('utf-8').decode('unicode-escape')
        return cleaned_text
    return None

def separate_issues_by_state(issue_data, state,path):
    """Separate issues into open and closed based on state."""
    if path==3:
       #print(issue_data["Sources"][0])
       return [issue for issue in issue_data["Sources"] if issue["Closed"] == state]
    else:
       return [issue for issue in issue_data["Sources"] if issue["State"] == state]


def calculate_total_issues_by_language(issue_data):
    """Calculate total issues for each language."""
    total_issues = defaultdict(int)
    for issue in issue_data["Sources"]:
        language = issue["RepoLanguage"]
        if language is not None:
            total_issues[language] += 1
    #print(total_issues)
    return total_issues

def calculate_precision_for_closed_issues(closed_issues):
    """Calculate precision for each language only for closed issues."""
    precision_results = {}
    for issue in closed_issues:
        language = issue["RepoLanguage"]
        if language is not None:
            precision_results[language] = precision_results.get(language, 0) + 1
    #print(precision_results)
    return precision_results

def add_entries_for_open_issues(open_issues, precision_results):
    """Add entries for languages with no closed issues."""
    for issue in open_issues:
        language = issue["RepoLanguage"]
        if language is not None and language not in precision_results:
            precision_results[language] = 0

def calculate_precision(precision_results, total_issues):
    """Calculate precision for each language."""
    for language, closed_count in precision_results.items():
        total_count = total_issues[language]
        precision_results[language] = closed_count / total_count if total_count > 0 else 0.0
    return precision_results

def plot_precision_bar_chart(languages, precision_values):
    """Plot a horizontal bar chart for precision values."""
    sns.set(style="white")
    sns.set_palette("pastel")  # Set a different color palette
    plt.figure(figsize=(10, 6))  # Set figure size for better visualization
    bar_width = 1  # Adjust the bar width here
    plt.barh(languages, precision_values, height=bar_width, color='#2BB4D4')
    plt.xlabel('Precision')
    plt.ylabel('Repository Language')
    plt.title('Precision of Issues for Each Language')
    plt.tight_layout()
    plt.show()




def CalculateandplotPrecision(json_file_path,pathno):
    issue_data = load_json(json_file_path)
    # Preprocess data
    preprocessed_data = preprocess_data(issue_data)

    # Separate issues by state
    if pathno==3:
        open_issues = separate_issues_by_state(preprocessed_data, False,3)
        closed_issues = separate_issues_by_state(preprocessed_data, True,3)
        #print(closed_issues)
    else:
        open_issues = separate_issues_by_state(preprocessed_data, 'OPEN',1)
        closed_issues = separate_issues_by_state(preprocessed_data, 'CLOSED',1)

    # Calculate total issues by language
    total_issues = calculate_total_issues_by_language(preprocessed_data)

    # Calculate precision for closed issues
    precision_results = calculate_precision_for_closed_issues(closed_issues)

    # Add entries for open issues
    add_entries_for_open_issues(open_issues, precision_results)

    # Calculate precision for each language
    precision_results = calculate_precision(precision_results, total_issues)

    # Plot precision values
    languages = list(precision_results.keys())
    precision_values = list(precision_results.values())
    plot_precision_bar_chart(languages, precision_values)


# Example usage
json_file_path1 = '/content/drive/MyDrive/devgpt snapshot/20230831_061759_issue_sharings.json'
json_file_path2 = '/content/drive/MyDrive/devgpt snapshot/20230831_060603_pr_sharings.json'
json_file_path3='/content/drive/MyDrive/devgpt snapshot/20230824_102000_discussion_sharings.json'

CalculateandplotPrecision(json_file_path1,1)
CalculateandplotPrecision(json_file_path2,2)
CalculateandplotPrecision(json_file_path3,3)

