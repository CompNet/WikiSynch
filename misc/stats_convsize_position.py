import glob
import json
import gzip
import csv
import sys
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

csv.field_size_limit(sys.maxsize)

'''
Compute the average size of conversations and the relative position of annotated messages in the conversation.
Used to plot figure 5 and 6 of the paper.
'''

def compute_size_position():
    rev_ids = {}
    for abuse_type in ["attack", "aggression", "toxicity"]:
        with open("GeneratedData/annotated_%s.csv" % abuse_type, "r") as f:
            reader = csv.DictReader(f)
            for message in reader:
                #general annotation indexed by rev_id
                if message["rev_id"] in rev_ids:
                    rev_ids[message["rev_id"]].extend(message["%s" % abuse_type])
                else:
                    rev_ids[message["rev_id"]] = [message["%s" % abuse_type]]

    computed_revid = []
    conv_size = []
    #distinguish between abusive and non-abusive messages
    annotated_position_zero = []
    annotated_position_one = []

    files = glob.glob("GeneratedData/conversations/*.txt")
    for file in files:
        with open(file, 'r') as f:
            # test if this is the first annotated message from this conversation that we process
            first_line = f.readline()
            message = json.loads(first_line)
            if message["rev_id"] not in computed_revid:
                computed_revid.append(message["rev_id"])
                new = True
            else:
                new = False

            rev_id = file.split("/")[-1].replace("_conversation.txt", "")
            #count messages before and after the annotated message
            len_before = 0
            len_after = 0
            before = True
            for line in f:
                message = json.loads(line)
                if message["rev_id"] == rev_id:   
                    before = False
                elif before:
                    len_before += 1
                else:
                    len_after += 1
        f.close()
  
        #only consider conversations with at least 5 messages for the figures
        if len_before+len_after+1 > 4:
            # percentage of the conversation before the annotated message
            position = float(len_before/(len_before+len_after)) * 100.0

            #append the position in the list (multiple times if the message is annotated for 2 or 3 abuse types)
            for i in range(rev_ids[rev_id].count("0")):
                #if int(rev_ids[rev_id]) == 0:
                annotated_position_zero.append(position)
            for i in range(rev_ids[rev_id].count("1")):
                #elif int(rev_ids[rev_id]) == 1:
                annotated_position_one.append(position)
            # only consider new conversations to avoid counting X times a conversation if there are X annotated messages in it.
            if new:
                # +1 for the annotated message itself
                conv_size.append(len_before+len_after+1)
    return conv_size, annotated_position_zero, annotated_position_one



if __name__ == "__main__": 
    conv_size, pos_zero, pos_one = compute_size_position()
    pos_total = []
    pos_total.extend(pos_zero + pos_one)

    plt.hist(pos_total, bins=33)
    plt.xlabel('Relative position of the annotated message in the conversation (%)')
    plt.ylabel('Number of conversations')
    plt.title('All annotated messages')
    plt.savefig('pos_conversation_total.pdf', bbox_inches='tight')
    plt.clf()

    plt.hist(pos_zero, bins=33)
    plt.xlabel('Relative position of the annotated message in the conversation (%)')
    plt.ylabel('Number of conversation')
    plt.title('Non abusive messages')
    plt.savefig('pos_conversation_zero.pdf')
    plt.clf()

    plt.hist(pos_one, bins=33)
    plt.xlabel('Relative position of the annotated message in the conversation (%)')
    plt.ylabel('Number of conversation')
    plt.title('Abusive messages')
    plt.savefig('pos_conversation_one.pdf')
    plt.clf()

    plt.hist(conv_size, bins=33)
    plt.xlabel('Total length of the conversation in number of messages')
    plt.ylabel('Number of conversation')
    plt.yscale("log")
    plt.savefig('length_conversation.pdf')
