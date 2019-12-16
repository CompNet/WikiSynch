import json
import csv
import glob
import sys
sys.setrecursionlimit(3500)

'''
Transform conversations from https://doi.org/10.6084/m9.figshare.11299118 into conversations usable by our classification methods.
The 3 methods allows to create conversations in different fashion. 

output: 1 file per annotated message with revid.csv as filename. Each file containing the conversation of an annotated message with 4 rows per message: [revid, timestamp, authorid, message]
'''


class comment:
    def __init__(self, data):
        self.data = data
        self.replies = []

    '''
    recursive method to return all the branches in the conversation
    '''
    def get_branches(self):
        authorid = self.data['authors'].split(':')[0]
        if authorid == "ANONYMOUS":
            authorid = self.data['authors'].split(':')[1].replace(".", "")
        if not authorid.isdigit():
            authorid = hash(authorid)   
        msg = [self.data["rev_id"], self.data["timestamp"], authorid, self.data["cleaned_content"]]

        if len(self.replies) == 0:
            return [[msg]]
        else: 
            result = []
            for i in range(len(self.replies)):
                ret = self.replies[i].get_branches()
                
                for j in range(len(ret)):
                    branch = [msg]
                    for k in range(len(ret[j])):
                        branch.append(ret[j][k])
                    result.append(branch)
            return result

'''
Create a conversation with the full sub-conversation before a leaf in the conversation tree. A message can thus be in several
sub-conversations. For example the creation message (the very first message in the conversation) is the first message of each sub-conversation.
The generated file contains all the sub-conversations separated by an empty line.
'''
def branches_conversation():
    conversations_head = None
    files = glob.glob("conversations-part*/*.txt")
    for file in files:
        rev_id = file.split("/")[-1].replace("_conversation.txt", "")
        with open("csv_branches/%s.csv" % rev_id, "w") as output:
            outputwriter = csv.writer(output)
            outputwriter.writerow(["rev_id", "timestamp", "author", "comment"])
            #all messages in the conversation indexed by their respective id
            messages = {}
            #reconstruct the messages tree
            for line in open(file, 'r'):
                data = json.loads(line)
                msg = comment(data)
                messages[data["id"]] = msg
                # only the creation message has an indentation equals to -1
                if data["indentation"] == -1:
                    conversations_head = msg
                # if the current message is not the creation, he is a reply to an other message.
                elif data["indentation"] != -1 and data["type"] == "MODIFICATION" and 'replyTo_id' not in data:
                    #sometimes, replyTo_id is not available. In this case we use parent_id
                    messages[data["parent_id"]].replies.append(msg)
                else:
                    messages[data["replyTo_id"]].replies.append(msg)

            # recursively run through the tree to get all the branches of the tree
            branches = conversations_head.get_branches()
            # writes branches with 1 empty line separating them
            for branch in branches:
                for i in range(len(branch)):
                    outputwriter.writerow(branch[i])
                outputwriter.writerow([])
        output.close()



'''
Create a linear conversation. All messages in the conversation are listed in the order of a pre-order traversal in the tree of messages.
'''
def linear_conversation():
    for file in glob.glob("conversations-part*/*.txt"):
        rev_id = file.split("/")[-1].replace("_conversation.txt", "")
        with open("csv_linear/%s.csv" % rev_id, "w") as output:
            outputwriter = csv.writer(output)
            outputwriter.writerow(["rev_id", "timestamp", "author", "comment"])
            for line in open(file, 'r'):
                data = json.loads(line)
                #retrieve the author id
                authorid = data['authors'].split(':')[0]
                #If the author was anonymous (not logged in), we use its ip address stripped from '.' as author id
                if authorid == "ANONYMOUS":
                	authorid = data['authors'].split(':')[1].replace(".", "")
                #sometimes the id is alphanumeric
                if not authorid.isdigit():
                    authorid = hash(authorid)
                text = [data['rev_id'], data['timestamp'], authorid, data['cleaned_content']]
                outputwriter.writerow(text)
        output.close()

'''
Create a bigger conversation containing all the conversations from the same page. Requires the files generated
by branches_conversation(). Concatenate all the conversations generated by this method which are extracted from the same page
as the annotated message.
'''
def fullpage_conversation():
    #all annotated rev_id grouped by the page (page_id) they were posted on
    pages = {}
    files = glob.glob("conversations-part*/*.txt")
    for file in files:
        rev_id = file.split("/")[-1].replace("_conversation.txt", "")
        with open(file, 'r') as f:
            first_line = f.readline()
            data = json.loads(first_line)
            if data["page_id"] in pages:
                pages[data["page_id"]].append(rev_id)
            else:
                pages[data["page_id"]] = [rev_id]
        f.close()

    #save the dict of rev_id indexed by page_id
    with open("pageid_revid.pkl", "wb") as f:
        pickle.dump(pages, f)

    #reads all the conversations from a same page and concatenates them
    for page_id in pages:
        filenames = [pages[page_id][i] for i in range(len(pages[page_id]))]
        with open("csv_fullpages/%s.csv" % page_id, mode='w') as file:
            outputwriter = csv.writer(file)

            for j in range(len(filenames)):
                rev_id = filenames[j]
                with open('csv/%s.csv' % rev_id, mode='r') as f:
                    reader = csv.reader(f)
                    next(reader)
                    for line in reader:
                        outputwriter.writerow(line)
                f.close()
        file.close()


if __name__ == "__main__":
    branches_conversation()
    linear_conversation()
    fullpage_conversation()