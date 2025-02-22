import re
import json
from collections import Counter
import sys
from pathlib import Path

'''
Data to collect:

Most Messages (index 0)
Least Messages (index 0)
Number of swears (index 1)

'''

def readFile(filepath):
    with open(filepath, 'r', encoding="utf-8") as file:
        lines = file.readlines()
    return lines


# List of dirty words from https://github.com/tural-ali
def collectSwear():
    dirty_words = []
    f = open('DirtyWords.json')
    data = json.load(f)
    for word in data["RECORDS"]:
        if word["language"] == "en":
            dirty_words.append(word["word"])
    return dirty_words

def countDirtyWords(message, dirtyWords):
    words_in_text = re.findall(r'\b\w+\b', message.lower())
    word_counts = Counter(words_in_text)
    total_count = sum(word_counts[word] for word in dirtyWords)
    return total_count

def newMessage(line):
    pattern = r"\[\d{1,2}/\d{1,2}/\d{1,2}, \d{1,2}:\d{2}:\d{2}\s[AP]M\]"
    cleaned_content = line.replace("\u200e", "")
    match = re.search(pattern, cleaned_content)
    if match:
        return True, match.end(), cleaned_content
    else:
        return False, None, cleaned_content
    
def saveDataToJson(data):
    file_path = "my_data.json"

    with open(file_path, 'w') as json_file:
        json.dump(data, json_file, indent=4)

    
def handleParams():
    n = len(sys.argv)
    if n != 2:
        raise Exception("Wrong number of parameters")
   
    script_dir = Path(__file__).parent

    # Relative path to check
    relative_path = Path(sys.argv[1])

    # Construct the absolute path
    absolute_path = script_dir / relative_path

    # Check if the file exists
    if not absolute_path.is_file():
        raise Exception("File does not exist")
    
    return sys.argv[1]

def main(file):
    members = {}
    dirtyWords = collectSwear()
    lines = readFile(file)

    name = ""
    message = ""

    for line in lines:  
        ifMatch, end_index, cleaned_content = newMessage(line)
        
        if ifMatch:
            if name != "":
                members[name]["messages_sent"] = members[name]["messages_sent"] + 1 # Number of messages update
                members[name]["dirty_words_used"] = members[name]["dirty_words_used"] + countDirtyWords(message, dirtyWords)
                message = ""
            
            name = cleaned_content[int(end_index) + 1 : int(cleaned_content.find(":", end_index))]
            if name not in members.keys():
                members[name] = {"messages_sent": 0, "dirty_words_used": 0}
            
            message += cleaned_content[int(cleaned_content.find(":", end_index)): ]
        else:
            message += cleaned_content[int(cleaned_content.find(":", end_index)): ] + "\n"

    saveDataToJson(members)
if __name__ == "__main__":
    file = handleParams()
    main(file)

    


