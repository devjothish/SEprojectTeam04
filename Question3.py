from datetime import datetime
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
import json

def load_data(file_path):
    with open(file_path, 'r') as file:
        data = json.load(file)
    return data["Sources"]

def calculate_time_difference(pull_requests):
    time_diff_list = []

    for pr in pull_requests:
        created_at = datetime.strptime(pr["CreatedAt"], "%Y-%m-%dT%H:%M:%SZ")
        updated_at = datetime.strptime(pr["UpdatedAt"], "%Y-%m-%dT%H:%M:%SZ")

        # Calculate time difference in hours
        time_diff = (updated_at - created_at).total_seconds() / 3600
        if time_diff < 150:
            time_diff_list.append(time_diff)

    return time_diff_list
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

def calculate_statistics(time_diff_list):
    average_time = np.mean(time_diff_list)
    mean_time = np.mean(time_diff_list)
    median_time = np.median(time_diff_list)
    std_dev_time = np.std(time_diff_list)

    print(f"Average time taken to update a pull request: {average_time:.2f} hours")
    print(f"Mean time taken to update a pull request: {mean_time:.2f} hours")
    print(f"Median time taken to update a pull request: {median_time:.2f} hours")
    print(f"Standard deviation of time taken: {std_dev_time:.2f} hours")

    return average_time, median_time

def plot_data(time_diff_list, average_time, median_time):
    plt.figure(figsize=(18, 12))

    # Violin plot for distribution
    plt.subplot(2, 2, 1)
    sns.violinplot(x=time_diff_list, color='lightblue', inner='quartile')
    plt.title('Distribution of Time Taken to Update code')
    plt.xlabel('Time Difference (hours)')

    # Adding annotations
    plt.axvline(average_time, color='red', linestyle='dashed', linewidth=2, label='Average Time')
    plt.axvline(median_time, color='green', linestyle='dashed', linewidth=2, label='Median Time')
    plt.legend()
    plt.annotate(f'Average Time: {average_time:.2f} hours', xy=(average_time, 0.05), xytext=(average_time + 10, 0.1),
                 arrowprops=dict(facecolor='red', arrowstyle='->'), fontsize=10, color='red')
    plt.annotate(f'Median Time: {median_time:.2f} hours', xy=(median_time, 0.05), xytext=(median_time - 30, 0.1),
                 arrowprops=dict(facecolor='green', arrowstyle='->'), fontsize=10, color='green')

    # Histogram for additional distribution insight
    plt.subplot(2, 2, 2)
    plt.hist(time_diff_list, bins=20, color='#2BB4D4', edgecolor='black', alpha=0.7)
    plt.title('Histogram of Time Taken to Update code')
    plt.xlabel('Time Difference (hours)')
    plt.ylabel('Frequency')

    # Box plot for quartiles
    plt.subplot(2, 2, 3)
    sns.boxplot(x=time_diff_list, color='#2BB4D4')
    plt.title('Box Plot of Time Taken to Update code')
    plt.xlabel('Time Difference (hours)')

    # Cumulative Distribution Function (CDF) plot
    plt.subplot(2, 2, 4)
    sns.ecdfplot(x=time_diff_list, color='#2BB4D4', label='CDF')
    plt.title('Cumulative Distribution Function (CDF) of Time Taken')
    plt.xlabel('Time Difference (hours)')
    plt.ylabel('Cumulative Probability')
    plt.legend()

    plt.tight_layout()
    plt.show()

# Main program
file_path = '/content/drive/MyDrive/devgpt snapshot/20230831_060603_pr_sharings.json'
pull_requests = load_data(file_path)
time_diff_list = calculate_time_difference(pull_requests)
average_time, median_time = calculate_statistics(time_diff_list)
plot_data(time_diff_list, average_time, median_time)
