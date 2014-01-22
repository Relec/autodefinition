# AutoDefinition Bot
# A Reddit bot for automatically defining words.
# Copyright Zach Johnson 2013
'''
 This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.


    Please also refer to the stipulations defined in the README file.
'''

# Imports
import threading
import praw
import time
from nltk.corpus import wordnet
from multiprocessing.pool import ThreadPool

pool = ThreadPool(processes=1)

# Constants
footer = "\n***\n ^^This ^^definition ^^was ^^generated ^^by ^^a ^^bot."
header = ""


blacklist = []

# Login to Reddit
r = praw.Reddit('AutoDefinition Bot by u/_Heckraiser2_ v 1')
print("Logging in...")
r.login("username", "password")
print("Login success.")
print("Importing Ids...")

# Import IDs
with open('ids.txt', 'r') as f:
    already_done = [line.strip() for line in f]
print("Ids imported.")

# Write already commented comment id's to a text file.
def write_id(comment):
    with open("ids.txt", "a") as text_file:
        text_file.write(comment.id + "\n")
        text_file.close()


# Send the comment reply to reddit
def reply_to_comment(comment, text):
    comment.reply(header + text + footer)
    already_done.append(comment.id)


# Check comment and look up definition and other data
def parse_comment(comment):
    if comment.id not in already_done:
        comment1 = comment.body.lower()
        if ":" in comment1:
            param, value = comment1.split(":", 1)
            value = value.strip()
            value = value.split(' ', 1)[0]
            if not value == "":
                value = value.replace(" ", "")
                print value
                async_result = pool.apply_async(lookup_word, (value,))
                res = async_result.get()
                print res
                if res != "Not found":
                    threading.Thread(target=reply_to_comment, args=(comment, res)).start()
                    write_id(comment)

# Look up word using nltk
def lookup_word(word):
    wordset = wordnet.synsets(word)
    joined = ""
    if len(wordset) != 0:
        for i in wordset:
            joined += "-" * 10 + "\n\n" + "**" + str(word.capitalize()) + "**" + " " + "*" + str(i.lexname) + "*" \
                      + "\n\n" + "Definition: " + str(i.definition) + '\n\n'
            for example in i.examples:
                joined += "Example: " + example + '\n\n'
        return joined
    else:
        return "Not found"


# Main loop for comment searching
def main_loop():
    # Main loop start here...
    print("Starting...")
    while True:
        # Read the blacklist and place it into an array
        with open("blacklist.txt", 'r') as f:
            del blacklist[:]
            for entry in f.readlines():
                blacklist.append(entry.strip())

        # Start the comment loop
        try:
            # Grab as many comments as we can and loop through them
            for comment in r.get_comments("all", limit=None):
                # Check if the comment meets the basic criteria
                if "define:" in comment.body.lower():
                    print("Comment found. Parsing...")
                    threading.Thread(target=parse_comment, args=(comment,)).start()

            # Finally wait 30 seconds
            print("Sleeping...")
            time.sleep(30)
            print("Starting..")
        except Exception as e:
            print(e)

# Threads!
main_thread = threading.Thread(target=main_loop)
# Start threads!
main_thread.start()