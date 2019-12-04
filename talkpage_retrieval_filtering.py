import csv
import glob
import csv
import json

'''
Combination of step 2 and 3 of the pipeline.

First, retrieve all the page_id with at least 1 annotated comment using the files generated at step 1.
Then, read all the raw data from WikiConv. Filters actions so that only creation, addition and modification are retained and group actions by conversation_id.
If the action is not part of a conversation with 1 or more annotated comment, the action is discarded. Else, the action is saved and written to a file.

IN:
    - annotated_abusetype.csv: Files generated at step 1. Used to list all conversation_id we have to retain.
    - wikiconv/7376003/*: Raw data from WikiConv in JSON. 500 files containing all the actions available in the english part of WikiConv. 

OUT:
    talk_pages/page_id.txt: All the actions of the pages containing an annotated comment grouped by page. talk_pages/111.txt corresponding to all the actions posted on page #111.
'''


#List of all page_id containing annotated messages in the 3 datasets
annotated_pageid = []
for filename in ["GeneratedData/annotated_attack.csv", "GeneratedData/annotated_aggression.csv", "GeneratedData/annotated_toxicity.csv"]:
    with open(filename, mode='r') as f:
        reader = csv.reader(f)
        for row in reader:
            #conv_id
            if row[1] not in annotated_pageid:
                annotated_pageid.append(row[1])
annotated_pageid = set(annotated_pageid)


# Dict containing all the actions to save, indexed by the page_id they have to be written in.
to_save = {}
j = 0
i = 0
# All raw files from WikiConv
files = glob.glob('Data/wikiconv/7376003/*')
for f in files:
    for line in open(f, 'r'):
        action = json.loads(line)
        #filter actions by their type
        if action['type'] in ['CREATION', 'ADDITION', 'MODIFICATION']:
            #If the considered action belongs to a page where an annotated comment was posted, we keep the action 
            if action['page_id'] in annotated_pageid:
                if action['page_id'] not in to_save:
                    to_save[action['page_id']] = [action]
                else:
                    to_save[action['page_id']].append(action)
                # Write to file every 50,000 comments 
                i+=1
                if i % 50000 == 0:
                    for page in to_save:
                        with open('GeneratedData/talk_pages/%s.txt' % page, 'a') as outfile:
                            for comment in to_save[page]:
                                json.dump(comment, outfile)
                                outfile.write('\n')
                        outfile.close()
                    to_save = {}
    # number of input file computed
    j += 1
    print ('%s / %s' % (j, len(files)))

#Save last part of comments
for page in to_save:
    with open('GeneratedData/talk_pages/%s.txt' % page, 'a') as outfile:
        for message in to_save[page]:
            json.dump(message, outfile)
            outfile.write('\n')
    outfile.close()