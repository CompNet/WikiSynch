import json
import csv
import glob
import os
from difflib import SequenceMatcher
import sys
sys.setrecursionlimit(3500)

class message():
    def __init__(self, m,):
        self.data = m
        self.answers = []
        self.parent = None

    def output(self, indent):
    	#change indentation value to reflect the structure of the reconstructed conversation. Each message in the conversation is an answer to the first previous message with 1 less indentation
    	#Returns the conversation 
        self.data["indentation"] = indent
        ret = [self.data]
        for ans in self.answers:
            ret.extend(ans.output(indent+1))
        return ret

    def get_conv_origin(self):
    	#returns the first message (root) of the conversation
        msg = self
        while msg.parent != None:
            msg = msg.parent
        return msg

'''
Combination of step 4 and 5 of the reconstruction pipeline.


Reconstruct all conversations from pages containing annotated comments. When several comments have the same rev_id, compute the LCS to determine the actual
annotated comment. One comment is retained and the others have their rev_id modified (add 0 at the end) to ensure that annotated rev_id are unique.
Filter all the reconstructed conversations to retain only those containing an annotated comment.
Conversations are structured and rev_id of annotated comments are unique in the output files.

IN:
    - annotated_abusetype.csv: Files generated at step 1. Used to list all rev_id we have to retain and the textual content of each annotated comment in WCC.
    - talk_pages/*: files generated at previous step containing all the actions of the pages containing an annotated comment grouped by page. 

OUT:
    - conversations/revid_conversation.txt: 1 file per annotated comment. Contains the structured conversation in which the annotated comment was posted. 
    885_conversation.txt contains the conversation of comment with rev_id 885. Rev_id of annotated comments are unique in these files. 

'''


def load_annotated_comments():
    #Dict of all the annotated comments' rev_id indexed by their page_id
    annotated_revids = {}
    # Textual content of labeled comments indexed by their rev_id
    text_labeled_msg = {}
    files = ['GeneratedData/annotated_attack.csv', 'GeneratedData/annotated_aggression.csv', 'GeneratedData/annotated_toxicity.csv']
    for file in files:
        with open(file, mode='r') as f:
            reader = csv.DictReader(f)
            #fieldnames=("rev_id", "page_id", "comment", annotations ...))
            for annotated_action in reader:
                #
                text_labeled_msg[annotated_action['rev_id']] = annotated_action["comment"]
                if annotated_action["page_id"] in annotated_revids:
                    # add the rev_id to the list if it is not already in
                    if annotated_action["rev_id"] not in annotated_revids[annotated_action["page_id"]]:
                        annotated_revids[annotated_action["page_id"]].append(annotated_action["rev_id"])
                else:
                    annotated_revids[annotated_action["page_id"]] = [annotated_action["rev_id"]]
        f.close()
    return annotated_revids, text_labeled_msg


#annotated_revids = Dict of all the annotated comments' rev_id indexed by their page_id
#text_labeled_msg = Textual content of labeled comments indexed by their rev_id
annotated_revids, text_labeled_msg = load_annotated_comments()
# For each page containing 1 or more action with the same rev_id as a labeled comment
for file in glob.glob("GeneratedData/talk_pages/*"):
    #page_id from the filename
    page_id = file.split("/")[-1].replace(".txt", "")

    #Dict of all actions with the same rev_id as a labeled comment on this page. Indexed by the rev_id
    possible_labeled_messages = {}
    for annotated_revid in annotated_revids[page_id]:
        possible_labeled_messages[annotated_revid] = []

    #All messages on the current talk page indexed by their id
    messages = {}
    
    #Read the file containing all actions of the current talk page
    #Create all message objects and list all possible labeled messages
    for line in open(file, 'r'):
        data = json.loads(line)
        #Create all message objects
        msg = message(data)
        messages[msg.data["id"]] = msg
        #if the message's rev_id is a labeled rev_id
        if msg.data["rev_id"] in possible_labeled_messages:
            possible_labeled_messages[msg.data["rev_id"]].append(msg)



    #Determine labeled messages in case the rev_id is not unique in data
    #Labeled_messages of this page indexed by their unique rev_id
    labeled_messages = {}
    # If multiple messages with same labeled rev_id, compute the LCS between each message and the original annotated message to determine the actual annotated message.
    for rev_id in possible_labeled_messages:
        if len(possible_labeled_messages[rev_id]) > 1:
            max_lcs = -1
            selected_message = None
            targeted_message_text = text_labeled_msg[rev_id]
            #for all possible annotated messages, compute LCS
            for msg in possible_labeled_messages[rev_id]:
                message_text = msg.data['content']
                #Compute LCS for each message
                match = SequenceMatcher(None, targeted_message_text, message_text).find_longest_match(0, len(targeted_message_text), 0, len(message_text))
                #Change all rev_id so that the labeled message has a unique rev_id
                msg.data['rev_id'] = msg.data['rev_id'] + '0'
                if match.size > max_lcs:
                    selected_message = msg
                    max_lcs = match.size
                        
            #Change back the rev_id of the actual annotated message (now the rev_id is unique)
            selected_message.data['rev_id'] = rev_id
            #Keep only the actual labeled message
            labeled_messages[rev_id] = selected_message
        elif len(possible_labeled_messages[rev_id]) == 1:
            #If the rev_id is already unique, there is no need to compute LCS
            labeled_messages[rev_id] = possible_labeled_messages[rev_id][0]

    #At this point, conversations contains all messages of each conversation known to contain a labeled message but unstructured
    #Rebuild conversation structure based on several attributes
    #List of all first messages of a conversation on the page indexed by conversation_id
    conversations_head = {}
    for msg in messages.values():
        #If it's the first post of a conversation
        if msg.data['id'] == msg.data['ancestor_id'] == msg.data['conversation_id'] and msg.data["type"] != "MODIFICATION":
            conversations_head[msg.data['conversation_id']] = msg

        elif msg.data["type"] == "MODIFICATION" and 'replyTo_id' not in msg.data:
            targeted_id = msg.data['parent_id']
            messages[targeted_id].answers.append(msg)
            msg.parent = messages[targeted_id]
        else:
            targeted_id = msg.data['replyTo_id']
            messages[targeted_id].answers.append(msg)
            msg.parent = messages[targeted_id]
     
    #Conversations are now structured correctly
    #Save to files
    for lab_message in labeled_messages.values():
        conv_origin_id = lab_message.get_conv_origin().data["conversation_id"]
        conv = conversations_head[conv_origin_id]
        with open("GeneratedData/conversations/%s_conversation.txt" % (lab_message.data['rev_id']), 'w') as outfile:
        	#write the structured conversation to file
            for msg in conv.output(-1):
                json.dump(msg, outfile)
                outfile.write('\n')
        outfile.close()