'''1.What is the typical structure of conversations between developers and ChatGPT? How many turns does it take on average to reach a conclusion? '''

import json
import matplotlib.pyplot as plt
import numpy as np
import re
from datetime import datetime
import html
from bs4 import BeautifulSoup
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer


def load_json(json_file_path):
    """Load JSON data from a file."""
    with open(json_file_path, 'r') as file:
        data = json.load(file)
    return data

nltk.download('stopwords')
nltk.download('punkt')
nltk.download('wordnet')

def preprocess_and_clean(json_data):
    # Define a function to clean text
    def clean_text(text):
        if text is not None:
            # Remove HTML tags
            cleaned_text = BeautifulSoup(text, 'html.parser').get_text()
            # Decode HTML entities
            cleaned_text = html.unescape(cleaned_text)
            # Convert to lowercase
            cleaned_text = cleaned_text.lower()
            # Remove non-alphanumeric characters
            cleaned_text = re.sub(r'[^a-zA-Z0-9\s]', '', cleaned_text)
            # Remove stopwords
            stop_words = set(stopwords.words('english'))
            word_tokens = word_tokenize(cleaned_text)
            cleaned_text = ' '.join([word for word in word_tokens if word not in stop_words])
            # Lemmatization
            lemmatizer = WordNetLemmatizer()
            cleaned_text = ' '.join([lemmatizer.lemmatize(word) for word in word_tokens])
            # Remove extra whitespaces
            cleaned_text = re.sub(r'\s+', ' ', cleaned_text).strip()
            return cleaned_text
        return None


    # Clean and handle null values for top-level attributes
    json_data['Title'] = clean_text(json_data.get('Title'))
    json_data['Body'] = clean_text(json_data.get('Body'))

    return json_data

def issuecategorization(data):
  pull_requests = data["Sources"]

  for pr in data:
    # Access the ChatGPT conversations
    conversations = pr["ChatgptSharing"][0]["Conversations"]

    # Loop through each conversation
    for conversation in conversations:
        # Analyze the answer for complex pattern matching
        answer = conversation["Answer"].lower()

        # Define complex patterns for an open state
        open_patterns = [r'\b(?:Concerns|Revisit|Review|Thoroughly|Additional information|Reconsider|Alternative|Explore|Possibilities|Not on the same page|Not reached a resolution|Collaboration|Issue|Investigate|Progress|Insights|Not the same page|Alternative solutions|Challenge|Less-than-ideal situation)\b'
        ]

        # Define complex patterns for a closed state
        closed_patterns = [
            r'\b(?:Closed|Result|Gratitude|Appreciate|Information|Confirmation|Closure|Assistance|Future|Reach out)\b',
            r'\b(?:Closed|Implement|Thanks|Discussing|Collaboration|Consider|Understanding|Alternative|Approaches|Solutions|Investigating|Progress|Insights|Follow up|Circle back|Findings)\b'
        ]

        # Check for complex patterns suggesting an open state
        if any(re.search(pattern, answer) for pattern in open_patterns):
            pr_state = "Open"
        else:
            # Check for complex patterns suggesting a closed state
            if any(re.search(pattern, answer) for pattern in closed_patterns):
                pr_state = "Closed"
            else:
                pr_state = "Uncertain"

    return data
def extract_prompt_counts(source, state):
    """Extract the prompt counts from the given source and state."""
    prompts = []
    for entry in source['ChatgptSharing']:
        if 'NumberOfPrompts' in entry and entry['NumberOfPrompts'] is not None:
            prompts.append(entry['NumberOfPrompts'])
    return prompts

def calculate_average(prompt_list):
    """Calculate the average of a list of prompt counts."""
    if not prompt_list:
        return 0
    return round(sum(prompt_list) / len(prompt_list))

def plot_side_by_side_bar_chart_multi(categories, bar_series_list, chart_title, series_names, colors=None):
    """Plot side-by-side bar charts with multiple bar series and optional colors."""
    bar_width = 0.2  # Define the width of the bars
    bar_height = 0.35

    fig, ax = plt.subplots()

    num_series = len(bar_series_list)

    for i, (bar_series, series_name) in enumerate(zip(bar_series_list, series_names)):
        if colors and i < len(colors):
            color = colors[i]
        else:
            color = None

        bars = ax.bar(np.arange(len(categories)) + i * bar_width, bar_series, bar_width, label=series_name, color=color)

    # Adding labels and title

    ax.set_xlabel('Issue State')
    ax.set_ylabel('Avg Prompt Count')
    ax.set_title(chart_title)
    ax.set_xticks(np.arange(len(categories)) + (num_series - 1) * bar_width / 2)
    ax.set_xticklabels(categories)
    ax.legend()

    # Show the bar chart
    plt.show()

def AvgPromptCount(json_file_path_pr, json_file_path_issue, json_file_path_discussions, series):
    """Calculate and plot the average prompt counts for open and closed states."""

    data_pr = load_json(json_file_path_pr)
    cleaned_data_pr = preprocess_and_clean(data_pr)

    data_issue = load_json(json_file_path_issue)
    cleaned_data_issue = preprocess_and_clean(data_issue)

    data_discussions = load_json(json_file_path_discussions)
    cleaned_data_discussions = preprocess_and_clean(data_discussions)

    opened_pr, closed_pr = [], []
    opened_issue, closed_issue = [], []
    opened_discussions, closed_discussions = [], []

    for source in cleaned_data_pr['Sources']:
       if source['State'] == "CLOSED":
            closed_pr.extend(extract_prompt_counts(source, 'CLOSED'))
       else:
            opened_pr.extend(extract_prompt_counts(source, 'OPEN'))

       avg_opened_pr = calculate_average(opened_pr)
       avg_closed_pr = calculate_average(closed_pr)

    for source in cleaned_data_issue['Sources']:
         if source['State'] == "CLOSED":
            closed_issue.extend(extract_prompt_counts(source, 'CLOSED'))
         else:
            opened_issue.extend(extract_prompt_counts(source, 'OPEN'))

         avg_opened_issue = calculate_average(opened_issue)
         avg_closed_issue = calculate_average(closed_issue)

    for source in cleaned_data_discussions['Sources']:
        if source['Closed'] == True :
           closed_discussions.extend(extract_prompt_counts(source, 'CLOSED'))
        else:
           opened_discussions.extend(extract_prompt_counts(source, 'OPEN'))

        avg_opened_discussions = calculate_average(opened_discussions)
        avg_closed_discussions = calculate_average(closed_discussions)

    categories = ['Open', 'Closed']

    # Use the new function to plot with three bar series
    plot_side_by_side_bar_chart_multi(
        categories,
        [
            [avg_opened_pr, avg_closed_pr],
            [avg_opened_issue, avg_closed_issue],
            [avg_opened_discussions, avg_closed_discussions]
        ],
        '',
        series_names=series,
        colors=['#2BB4D4', '#5CE1E6', '#004AAD']  # Optional: specify colors for each series
    )


#  usage with six input file paths
json_file_path_pr = '/content/drive/MyDrive/devgpt snapshot/20230831_060603_pr_sharings.json'
json_file_path_issue = '/content/drive/MyDrive/devgpt snapshot/20230831_061759_issue_sharings.json'
json_file_path_discussions='/content/drive/MyDrive/devgpt snapshot/20230824_102000_discussion_sharings.json'
json_file_path_commit = '/content/drive/MyDrive/devgpt snapshot/20230831_061759_issue_sharings.json'

json_file_path_file = '/content/drive/MyDrive/devgpt snapshot/20230831_060603_pr_sharings.json'
json_file_path_hackernews='/content/drive/MyDrive/devgpt snapshot/20230824_102000_discussion_sharings.json'

series=['Pull Request', 'Issue', 'Discussions']
series2=['File sharings','Hacker News','Commit sharings']
AvgPromptCount(json_file_path_pr, json_file_path_issue,json_file_path_discussions,series)
AvgPromptCount(json_file_path_commit,json_file_path_file,json_file_path_hackernews,series2)
