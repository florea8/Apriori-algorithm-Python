import sys
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QTextEdit
import pandas as pd
from itertools import combinations

class AprioriRunner:
    def __init__(self, source_file_path, min_conf, low_min_sup, num_rules, min_itemset_length):
        self.source_file_path = source_file_path
        self.min_conf = min_conf
        self.low_min_sup = low_min_sup
        self.num_rules = num_rules
        self.min_itemset_length = min_itemset_length
        self.itemsets = {}

    def incarca_fisier(self):
        try:
            with open(self.source_file_path, 'r') as file:
                lines = [line.strip().split(',') for line in file]

            lines = [line for line in lines if line]
            return lines
        except Exception as e:
            print(f"Eroare in citirea: {e}")
            return []


    def items_unici(self, transactions):
        return set(item for transaction in transactions for item in transaction)

    def generare_setdate(self, k, unique_items):
        return {tuple(sorted(itemset)) for itemset in combinations(unique_items, k)}
    
    
    def calculare_support(self, itemset, transactions):
        item = sum(1 for transaction in transactions if set(itemset).issubset(set(transaction)))
        return item / len(transactions)

    def filtrare_set(self, itemsets, transactions):
        return {itemset: self.calculare_support(itemset, transactions) for itemset in itemsets if self.calculare_support(itemset, transactions) >= self.low_min_sup}

    def generare_reguli(self, itemsets, transactions, num_rules):
        rules = []
        for itemset in itemsets:
            for i in range(1, len(itemset)):
                for antecedent in combinations(itemset, i):
                    consequent = tuple(set(itemset) - set(antecedent))
                    support = self.calculare_support(itemset, transactions)
                    confidence = support / self.calculare_support(antecedent, transactions)
                    if confidence >= self.min_conf:
                        rules.append((antecedent, consequent, confidence, support))
        return sorted(rules, key=lambda x: x[2], reverse=True)[:num_rules]


    def run_apriori_algorithm(self, transactions):
        unique_items = self.items_unici(transactions)
        self.itemsets = {1: {(item,) for item in unique_items}}
        k = 2
        while self.itemsets[k - 1]:
            candidate_itemsets = self.generare_setdate(k, unique_items) 
            frequent_itemsets = self.filtrare_set(candidate_itemsets, transactions)
            self.itemsets[k] = frequent_itemsets
            k += 1
 
class AprioriGUI(QWidget):
    def __init__(self):
        super().__init__()

        self.source_file_path = "food.csv"
        self.min_conf = 0.5
        self.low_min_sup = 0.1
        self.num_rules = 5
        self.min_itemset_length = 3 

        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        self.conf_label = QLabel("Confidenta minima:")
        self.conf_input = QLineEdit(str(self.min_conf))
        layout.addWidget(self.conf_label)
        layout.addWidget(self.conf_input)

        self.sup_label = QLabel("Low Min Support:")
        self.sup_input = QLineEdit(str(self.low_min_sup))
        layout.addWidget(self.sup_label)
        layout.addWidget(self.sup_input)

        self.rules_label = QLabel("Numarul de reguli:")
        self.rules_input = QLineEdit(str(self.num_rules))
        layout.addWidget(self.rules_label)
        layout.addWidget(self.rules_input)

        self.min_itemset_label = QLabel("Lungime minima itemset:")
        self.min_itemset_input = QLineEdit(str(self.min_itemset_length))
        layout.addWidget(self.min_itemset_label)
        layout.addWidget(self.min_itemset_input)

        self.run_button = QPushButton("Start")
        self.run_button.clicked.connect(self.run_apriori)
        layout.addWidget(self.run_button)

        self.result_text = QTextEdit()
        layout.addWidget(self.result_text)

        self.setLayout(layout)
        self.setWindowTitle('Algoritmul Apriori')
        self.show()

    def run_apriori(self):
        self.min_conf = float(self.conf_input.text())
        self.low_min_sup = float(self.sup_input.text())
        self.num_rules = int(self.rules_input.text())
        self.min_itemset_length = int(self.min_itemset_input.text())

        apriori_runner = AprioriRunner(self.source_file_path, self.min_conf, self.low_min_sup, self.num_rules, self.min_itemset_length)
        transactions = apriori_runner.incarca_fisier()
        
        apriori_runner.run_apriori_algorithm(transactions)
        result_text = f"Numarul de atribute: {len(apriori_runner.items_unici(transactions))}\n"
        result_text += f"Numarul de tranzactii: {len(transactions)}\n"
        result_text += "Apriori Rules:\n"
        result_text += "\nApriori\n=======\n"
        result_text += f"\nSuport minim: {apriori_runner.low_min_sup * 100}% ({len(transactions)} instante)\n"
        result_text += f"Confidenta minima: {apriori_runner.min_conf}\n"

        best_rules = apriori_runner.generare_reguli(apriori_runner.itemsets[self.min_itemset_length], transactions, self.num_rules)
        result_text += "\nCele mai bune reguli de asociere:\n"
        for rule_number, (antecedent, consequent, confidence, support) in enumerate(best_rules, 1):
            result_text += f"\n{rule_number}. {antecedent} ==> {consequent} <conf:({confidence:.2f})> [Suport: {float(support):.2f}]\n"

        self.result_text.setPlainText(result_text)
if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = AprioriGUI()
    sys.exit(app.exec_())