import csv
import random

'''
Randomly generate train/dev/test files for the 3 datasets.
'''

train_percent = 0.6
dev_percent = 0.2


for abuse_type in ["attack", "aggression", "toxicity"]:
    rev_ids = []
    with open("GeneratedData/annotated_%s.csv" % abuse_type, "r") as f:
        reader = csv.DictReader(f)
        for message in reader:
            rev_ids.append(message["rev_id"])
    random.shuffle(rev_ids)

    limit_train = int(train_percent * len(rev_ids))
    limit_dev = int((train_percent+dev_percent) * len(rev_ids))

    with open("%s_train.csv" % abuse_type, "w") as output:
        writer = csv.writer(output)
        writer.writerow(["rev_id"])
        for rev_id in rev_ids[:limit_train]:
            writer.writerow([rev_id])
    output.close()

    with open("%s_dev.csv" % abuse_type, "w") as output:
        writer = csv.writer(output)
        writer.writerow(["rev_id"])
        for rev_id in rev_ids[limit_train:limit_dev]:
            writer.writerow([rev_id])
    output.close()

    with open("%s_test.csv" % abuse_type, "w") as output:
        writer = csv.writer(output)
        writer.writerow(["rev_id"])
        for rev_id in rev_ids[limit_dev:]:
            writer.writerow([rev_id])
    output.close()
    f.close()