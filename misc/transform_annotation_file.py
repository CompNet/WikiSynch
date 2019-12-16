import csv

'''
Extract 1 annotation from annotation files (annotations_abusetype.csv https://doi.org/10.6084/m9.figshare.11299118).
'''

def extract_annotation(abuse_type, annotation):
    with open("annotations_%s.csv" % abuse_type, mode='r') as file:
        reader = csv.DictReader(file)
        with open("annotations_%s_%s.csv" % (abuse_type, annotation), "w") as output:
            outputwriter = csv.writer(output)
            outputwriter.writerow(["rev_id", "annotation"])
            for line in reader:
                outputwriter.writerow([line["rev_id"], line["%s" % annotation]])
        output.close()
    file.close()

if __name__ == "__main__":
    extract_annotation("attack", "attack")
    extract_annotation("aggression", "aggression_score")