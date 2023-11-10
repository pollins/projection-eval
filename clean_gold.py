from argparse import ArgumentParser

text = "Remove sentences from some CoNLL output file that are not included in some gold file"

parser = ArgumentParser(description=text)
parser.add_argument('gold', help='Name of gold file')
parser.add_argument('out', help='Name of output file')
parser.add_argument('write', help='Name of file to write to')

args = parser.parse_args()

def read_file(filename):
    result = []
    sent_row = []
    sent_str = ""
    for line in open(filename, encoding='utf8'):
        line = line.strip()
        if line:
            row = line.split()
            sent_row.append(row)
            sent_str += row[1] + " "
        else:
            result.append((sent_str[:-1], sent_row))
            sent_row = []
            sent_str = ""
    return result

gold_sents = read_file(args.gold)
out_sents = read_file(args.out)

new_out_rows = []

while out_sents:
    out_sent = out_sents.pop()
    gold_sent = gold_sents[-1]
    if out_sent[0] == gold_sent[0]:
        out_rows = out_sent[1]
        for row in reversed(out_rows):
            new_out_rows.append(row)
        new_out_rows.append([])
        gold_sents.pop()

with open(args.write, 'w', encoding='utf8') as file: 
    for row in reversed(new_out_rows):
        print("\t".join(row), file=file)

print()