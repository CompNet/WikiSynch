import json
import glob
import csv
from sklearn.metrics import f1_score
from sklearn.metrics import precision_score
from sklearn.metrics import recall_score

'''
Compute the precision, recall and F1 score of the Google perspective API scores provided in WikiConv.
Human annotations from WCC are used as true labels.
'''


def retrieve_annotations(abuse_type):
    #list all rev_ids to use in the test split
    test = []
    with open("%s_test.csv" % abuse_type, mode='r') as f:
        reader = csv.DictReader(f)
        for message in reader:
            test.append(message['rev_id'])
    test = test[:300]

    #General annotation from WCC indexed by rev_id
    annotations = {}
    with open("GeneratedData/annotated_%s.csv" % abuse_type, "r") as f:
        reader = csv.DictReader(f)
        for message in reader:
            if message["rev_id"] in test:
                annotations[message["rev_id"]] = message["%s" % abuse_type]
    f.close()

    #Retrieve the toxicity and severe toxicity scores for each annotated message
    perspective_toxicity = {}
    perspective_severe_toxicity = {}
    for rev_id in test:
        file = "conversations/%s_conversation.txt" % rev_id
        for line in open(file, 'r'):
            message = json.loads(line)
            if message['rev_id'] == rev_id:
                perspective_toxicity[message['rev_id']] = message["toxicity"]
                perspective_severe_toxicity[message['rev_id']] = message["sever_toxicity"]
                break

    #true label from WCC
    wcc = []
    #Creates binary labels from scores using the threshold provided by WikiConv authors
    perspect_toxicity = []
    perspect_severe_toxicity = []
    for revid in perspective_toxicity:
        if perspective_toxicity[revid] > 0.64:
            perspect_toxicity.append(1)
        else: 
            perspect_toxicity.append(0)
        if perspective_severe_toxicity[revid] > 0.92:
            perspect_severe_toxicity.append(1)
        else: 
            perspect_severe_toxicity.append(0)
        wcc.append(int(annotations[revid]))

    return wcc, perspect_toxicity, perspect_severe_toxicity


def compute_results(true_labels, pred_toxicity, pred_severe_toxicity):
    #compute and print results
    print ("=====================Toxicity============================")
    print ("Binary accuracy: %s" % precision_score(true_labels, pred_toxicity, average='binary', pos_label=1))
    print ("Macro accuracy: %s" % precision_score(true_labels, pred_toxicity, average='macro'))
    print ("Micro accuracy: %s" % precision_score(true_labels, pred_toxicity, average='micro'))
    print ("Weighted accuracy: %s" % precision_score(true_labels, pred_toxicity, average='weighted'))

    print ("Binary recall: %s" % recall_score(true_labels, pred_toxicity, average='binary', pos_label=1))
    print ("Macro recall: %s" % recall_score(true_labels, pred_toxicity, average='macro'))
    print ("Micro recall: %s" % recall_score(true_labels, pred_toxicity, average='micro'))
    print ("Weighted recall: %s" % recall_score(true_labels, pred_toxicity, average='weighted'))

    print ("Binary F1 score (perspective toxicity vs detox): %s" % f1_score(true_labels, pred_toxicity, average='binary', pos_label=1))
    print ("Macro F1 score (perspective toxicity vs detox): %s" % f1_score(true_labels, pred_toxicity, average='macro'))
    print ("Micro F1 score (perspective toxicity vs detox): %s" % f1_score(true_labels, pred_toxicity, average='micro'))
    print ("Weighted F1 score (perspective toxicity vs detox): %s" % f1_score(true_labels, pred_toxicity, average='weighted'))
        
    print ("=====================Severe toxicity============================")

    print ("Binary accuracy: %s" % precision_score(true_labels, pred_severe_toxicity, average='binary', pos_label=1))
    print ("Macro accuracy: %s" % precision_score(true_labels, pred_severe_toxicity, average='macro'))
    print ("Micro accuracy: %s" % precision_score(true_labels, pred_severe_toxicity, average='micro'))
    print ("Weighted accuracy: %s" % precision_score(true_labels, pred_severe_toxicity, average='weighted'))

    print ("Binary recall: %s" % recall_score(true_labels, pred_severe_toxicity, average='binary', pos_label=1))
    print ("Macro recall: %s" % recall_score(true_labels, pred_severe_toxicity, average='macro'))
    print ("Micro recall: %s" % recall_score(true_labels, pred_severe_toxicity, average='micro'))
    print ("Weighted recall: %s" % recall_score(true_labels, pred_severe_toxicity, average='weighted'))

    print ("Binary F1 score (perspective toxicity vs detox): %s" % f1_score(true_labels, pred_severe_toxicity, average='binary', pos_label=1))
    print ("Macro F1 score (perspective toxicity vs detox): %s" % f1_score(true_labels, pred_severe_toxicity, average='macro'))
    print ("Micro F1 score (perspective toxicity vs detox): %s" % f1_score(true_labels, pred_severe_toxicity, average='micro'))
    print ("Weighted F1 score (perspective toxicity vs detox): %s" % f1_score(true_labels, pred_severe_toxicity, average='weighted'))



if __name__ == "__main__": 

    for abuse_type in ["attack", "aggression", "toxicity"]:
        true_labels, pred_toxicity, pred_severe_toxicity = retrieve_annotations(abuse_type)
        print ("-----------------%s-------------------" % abuse_type)
        compute_results(true_labels, pred_toxicity, pred_severe_toxicity)