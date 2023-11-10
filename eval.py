from argparse import ArgumentParser
from labelcount import LabelCounter
from copy import deepcopy
from collections import namedtuple
from nltk.metrics import ConfusionMatrix

text = "Compare Russian projection to English original"

parser = ArgumentParser(description=text)
parser.add_argument('gold', help='Name of gold file')
parser.add_argument('out', help = 'Name of output file from automatic projection system')

args = parser.parse_args()

# initialize all counters
unlabeled_args = LabelCounter()
unlabeled_predicates = LabelCounter()
labeled_args_correct = 0

# initialize arg counter dict
labeled_arg_dict = {}

def read_file(filename):
    result = []
    for line in open(filename, encoding='utf8'):
        line = line.strip()
        if line and not line.startswith('#'):
            row = line.split()
            result.append(row)
    return result

# read in both files, check length
gold = read_file(args.gold)
out = read_file(args.out)

if len(gold) != len(out):
    raise ValueError(f"Files of different length (gold {len(gold)}, out {len(out)})")


# create lists for confusion matrix
CMInputs = namedtuple('CMInput', 'X, y') # input structure
inputs = CMInputs([], [])
m_inputs = CMInputs([], [])

# get all counts
for i, gold_row in enumerate(gold):
    out_row = out[i]

    gold_fillpred = gold_row[8]
    out_fillpred = out_row[8]

    if len(gold_row) > 10:
        gold_apreds = gold_row[10:]
    else:
        gold_apreds = ['_']
    if len(out_row) > 10:
        out_apreds = out_row[10:]
    else:
        out_apreds = ['_']

    apreds_len_difference = len(gold_apreds) - len(out_apreds)

    # equalize apred lists
    if apreds_len_difference:
        if apreds_len_difference < 0:
            gold_apreds += ['_'] * -apreds_len_difference
        else:
            out_apreds += ['_'] * apreds_len_difference

    # count unlabeled predicates
    if gold_fillpred == 'Y':
        unlabeled_predicates.gold += 1

    if out_fillpred == 'Y':
        unlabeled_predicates.predicted += 1
        if gold_fillpred == out_fillpred:
            unlabeled_predicates.correct += 1

    # count labeled and unlabeled arguments
    for j, gold_apred in enumerate(gold_apreds):
        out_apred = out_apreds[j]
        
        is_gold_apred = gold_apred != '_'
        is_out_apred = out_apred != '_'

        if is_gold_apred:
            unlabeled_args.gold += 1
            if gold_apred not in labeled_arg_dict:
                labeled_arg_dict[gold_apred] = LabelCounter()
            labeled_arg_dict[gold_apred].gold += 1
            
            # confusion matrix data
            m_gold_apred = "ARGM" if gold_apred.startswith("ARGM") else gold_apred
            m_out_apred = "ARGM" if out_apred.startswith("ARGM") else out_apred

            inputs.y.append(gold_apred)
            inputs.X.append(out_apred)

            m_inputs.y.append(m_gold_apred)
            m_inputs.X.append(m_out_apred)


        
        if is_out_apred:
            unlabeled_args.predicted += 1
            if out_apred not in labeled_arg_dict:
                labeled_arg_dict[out_apred] = LabelCounter()
            labeled_arg_dict[out_apred].predicted += 1
            if gold_apred == out_apred:
                labeled_arg_dict[out_apred].correct += 1
                labeled_args_correct += 1
        
        if is_gold_apred and is_out_apred:
            unlabeled_args.correct += 1

# get measurements

labeled_args = deepcopy(unlabeled_args)
labeled_args.correct = labeled_args_correct

arg_measurements = {}
for arg in labeled_arg_dict:
    arg_measurements[arg] = labeled_arg_dict[arg].measurements()

def print_measurements(counter):
    precision, recall, f1 = counter.measurements()
    print(f"Precision: {counter.correct} / {counter.predicted} = {precision}")
    print(f"Recall:    {counter.correct} / {counter.gold} = {recall}")
    print(f"F1:        {f1}")


# print measurements
print("PREDICATES, UNLABELED")
print_measurements(unlabeled_predicates)
print()
print("ARGUMENTS, UNLABELED")
print_measurements(unlabeled_args)
print()
print("ARGUMENTS, LABELED")
print_measurements(labeled_args)
print()
print("INDIVIDUAL ARGUMENTS")
for arg_name, arg_counter in labeled_arg_dict.items():
    print()
    print(arg_name)
    print_measurements(arg_counter)
print()
print("CONFUSION MATRIX")
print(ConfusionMatrix(inputs.y, inputs.X))
print()
print("CONFUSION MATRIX, COMBINED ARGMS")
print(ConfusionMatrix(m_inputs.y, m_inputs.X))