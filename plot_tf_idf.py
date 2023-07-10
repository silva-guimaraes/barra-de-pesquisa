import matplotlib.pyplot as plt
import json
import sys


def plot_word_frequency(word_frequency):
    # Sort the dictionary by values in descending order
    sorted_words = sorted(word_frequency.items(), key=lambda x: x[1],
                          reverse=True)

    # Extract the first 20 words and their frequencies
    top_words = dict(sorted_words[:40])

    # Prepare data for plotting
    words = list(top_words.keys())
    frequencies = list(top_words.values())

    # Create a bar plot
    plt.bar(range(len(words)), frequencies)
    plt.xlabel('Words')
    plt.ylabel('Frequency')
    plt.title('Word Frequency')

    # Set the x-axis labels to the words
    plt.xticks(range(len(words)), words, rotation=90)
    plt.tight_layout()

    # Display the plot
    plt.show()


if len(sys.argv) < 1:
    print('len(sys.argv) < 1')
    sys.exit(1)


file = {}
with open(sys.argv[1]) as file:
    file = json.loads(file.read())

print(file['url'])
plot_word_frequency(file['tf_idf'])
