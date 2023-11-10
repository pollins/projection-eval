class LabelCounter:

    def __init__(self):
        self.correct = 0
        self.gold = 0
        self.predicted = 0
    
    def f1(self, precision, recall):
        denom = recall + precision
        if denom == 0:
            return float("nan")
        else:
            return (2 * recall * precision) / denom

    def measurements(self):
        if self.predicted == 0:
            precision = float("nan")
        else:
            precision = self.correct / self.predicted
        if self.gold == 0:
            recall = float("nan")
        else:
            recall = self.correct / self.gold
        f1_ = self.f1(precision, recall)
        return precision, recall, f1_
