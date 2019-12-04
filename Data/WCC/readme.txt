Contains 3 files:
	- attack_all.csv: csv file with columns (rev_id, page_id, comment, year, logged_in, ns, sample, split, quoting_attack, recipient_attack, third_party_attack, other_attack, attack)
	- aggression_all.csv: csv file with columns (rev_id, page_id, comment, year, logged_in, ns, sample, split, aggression, aggression_score)
	- toxicity_all.csv: csv file with columns (rev_id, page_id, comment, year, logged_in, ns, sample, split, toxicity, toxicity_score)

	These files are created by combining data from the full corpus and data from the annotated part of the corpus. Columns about the page and the author are only available in the full corpus. Annotations in these files are the gold annotations (average score among judgments for scores and majority annotation for binary annotations).

	Full corpus available at https://doi.org/10.6084/m9.figshare.4264973
	Annotated corpora available at:
		attack 		https://doi.org/10.6084/m9.figshare.4054689
		aggression 	https://doi.org/10.6084/m9.figshare.4267550
		toxicity 	https://doi.org/10.6084/m9.figshare.4563973


Also contains WCC/*.csv where * is a page_id. 1 file per conversation known to contain 1 or more annotated comment in WCC.
	Contains all comments available in WCC and pertaining to the conversation.

	Attributes are: rev_id, comment, cleaned_comment, timestamp, conv_id, conv_name, author_id, author name, bot, admin
	When the author was not logged in, author_id is missing and author name is its ip address.