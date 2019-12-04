import gzip, pickle, csv, time, datetime, glob, re, os
from time import mktime
from datetime import datetime

'''
Step 1 of the pipeline.
Extract all the gold annotations for the annotated messages.

IN:
	- abusetype_all.csv: files genrated from the WCC data. Contains 1 line per annotated comment in WCC.
	Columns are: rev_id, page_id, comment, year, logged_in, ns, sample, split and all annotations (depending on the abuse type considered).
	Annotations are the summary of the 10 judgments in WCC i.e. average value for scores and majoritary value for binary.
	- WCC/*.csv: files generated from the WCC data. 1 file per page containing at least 1 annotated comment. 
	WCC/xx.csv contains all the messages posted on the xx page (in the WCC data).
	Attributes are: rev_id, comment, cleaned_comment, timestamp, conv_id, conv_name, author_id, author name, bot, admin
	When the author was not logged in, author_id is missing and author name is its ip address. 

OUT:
	- annotated_abusetype.csv: files containing all the available annotated comments from the 3 WCC datasets and their gold annotations.
	Attributes are: rev_id, page_id, comment, all gold annotations
'''

def strip_message(message):
	message = re.sub('NEWLINE_TOKEN', '', message)
	message = re.sub('NEWLINE', '', message)
	
	return message

def load_annotated(abuse_type):
	annotated_msg = {}
	with open('Data/%s_all.csv' % abuse_type, mode='r') as csvfile:
		reader = csv.DictReader(csvfile, delimiter='	')
		for row in reader:
			#some messages don't have any page_id. We can't use them
			if len(row['page_id']) > 0:
				#remove unused attributes	
				del row['year']
				del row['logged_in']
				del row['ns']
				del row['sample']
				del row['split']
				annotated_msg[row['rev_id']] = row
	return annotated_msg



def create_annotated_file(abuse_type):
	# Get dict of all annotated messages indexed by their rev_id
	annotated_msg = load_annotated(abuse_type)
	# name of the columns (rev_id, page_id, comment, all annotations)
	column_names = list(annotated_msg.values())[0].keys()
	with open('GeneratedData/annotated_%s.csv' % abuse_type, mode='w') as outfile:
		writer = csv.writer(outfile)
		writer.writerow(column_names)
		#All conversation files from WCC
		files = glob.glob("Data/WCC/*.csv")
		for file in files:
			with open(file, mode='r') as f:
				reader = csv.DictReader(f, fieldnames=("rev_id", "message_text", "message", "date", "conv_id", "conv_name", "user_id", "user_text", "bot", "mod"), delimiter='	')
				for row in reader:
					#If current message is an annotated message
					if row['rev_id'] in annotated_msg:
						annotated_message = annotated_msg[row['rev_id']]
						msg = strip_message(row['message_text'])

						#for attack: rev_id, conv_id, text, quoting_attack, recipient_attack, third_party_attack, other_attack, attack
						#for aggression: rev_id, conv_id, text, aggression_score, aggression
						#for toxicity: rev_id, conv_id, text, toxicity_score, toxicity
						message = [int(annotated_message['rev_id']), int(annotated_message['page_id']), msg]
						for annotation in list(annotated_message.values())[3:]:
							message.append(annotation)
						writer.writerow(message)
			f.close()
	outfile.close()


if __name__ == "__main__":
	create_annotated_file('attack')
	create_annotated_file('aggression')
	create_annotated_file('toxicity')