import re
import json
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
    words = re.findall(r'\b\w+\b', message)
    count = 0
    for word in words:
        if word in dirtyWords:
            count += 1
    return count

def countWords(message, wordCloud):
    words = re.findall(r'\b\w+\b', message)
    for word in words:
        if word.lower() in wordCloud.keys():
            wordCloud[word.lower()] += 1
        else:
            wordCloud[word.lower()] = 1
    return len(words)

def activeTimes(mostActiveTimes, text):
    pattern = r"\[\d{2}/\d{2}/\d{2}, (\d{1,2}):\d{2}:\d{2}\s?(AM|PM)\]"
    match = re.search(pattern, text)
    if match:
        hour, am_pm = match.groups()
        mostActiveTimes[str(hour) + str(am_pm)] += 1

def newMessage(line, mostActiveTimes):
    pattern = r"\[\d{1,2}/\d{1,2}/\d{1,2}, \d{1,2}:\d{2}:\d{2}\s[AP]M\]"
    cleaned_content = line.replace("\u200e", "")
    activeTimes(mostActiveTimes, line)
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
    wordCloud = {}
    mostActiveTimes = {"12AM" : 0, "1AM" : 0, "2AM" : 0, "3AM" : 0, "4AM" : 0, "5AM" : 0, "6AM" : 0, "7AM" : 0, "8AM" : 0, "9AM" : 0,
                        "10AM" : 0, "11AM" : 0, "12PM" : 0, "1PM" : 0, "2PM" : 0, "3PM" : 0, "4PM" : 0, "5PM" : 0, "6PM" : 0, "7PM" : 0,
                        "8PM" : 0, "9PM" : 0, "10PM" : 0, "11PM" : 0}

    name = ""
    message = ""

    for line in lines:
        ifMatch, end_index, cleaned_content = newMessage(line, mostActiveTimes)
        
        if ifMatch:
            if name != "":
                members[name]["messages_sent"] = members[name]["messages_sent"] + 1 # Number of messages update
                members[name]["dirty_words_used"] = members[name]["dirty_words_used"] + countDirtyWords(message, dirtyWords)
                members[name]["average_words_per_message"] = members[name]["average_words_per_message"] + countWords(message, wordCloud)
                message = ""
            
            name = cleaned_content[int(end_index) + 1 : int(cleaned_content.find(":", end_index))]
            if name not in members.keys():
                members[name] = {"messages_sent": 0, "dirty_words_used": 0, "swear_to_messages" : 0, "average_words_per_message": 0}
            
            message += cleaned_content[int(cleaned_content.find(":", end_index)): ]
        else:
            message += cleaned_content[int(cleaned_content.find(":", end_index)): ] + "\n"

    for name in members:
        members[name]["swear_to_messages"] = round(members[name]["dirty_words_used"] / members[name]["messages_sent"], 3)
        members[name]["average_words_per_message"] = round(members[name]["average_words_per_message"]/ members[name]["messages_sent"], 3)
    
    members["general_chat"] = {}
    members["general_chat"]["most_used_words"] = dict(sorted(wordCloud.items(), key=lambda item: item[1], reverse=True))
    members["general_chat"]["most_active_times"] = mostActiveTimes

    saveDataToJson(members)
if __name__ == "__main__":
    file = handleParams()
    main(file)

    


