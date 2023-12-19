import random
import json
import pandas as pd


class BankApi:

    def __init__(self, loan_amount, loan_term):
        self.bank_list = ["ziraat bankasi", "vakifbank", "is bankasi", "halkbank", "garanti bankasi",
                          "yapi kredi", "akbank", "qnb finansbank", "denizbank", "teb", "ing"]
        self.loan_amount = loan_amount
        self.loan_term = loan_term

    def fetch_response(self):
        response_dict = self.generate_proposal_for_each_bank()
        data = self.convert_types_of_data(response_dict)
        return data

    def convert_types_of_data(self, data):
        out = {
            "dicto": data,
            "json": json.dumps(data, indent=4, ensure_ascii=False),
        }
        df = pd.DataFrame.from_dict(data, orient='index')
        df.reset_index(inplace=True)
        df.rename(columns={'index': 'Bank', "interest_rate": "Interest Rate",
                  "monthly_payment": "Monthly Payment", "total_payment": "Total Payment"}, inplace=True)
        df['Interest Rate'] = df['Interest Rate'].apply(
            lambda x: f'{x:.2f}')
        df = df.astype(str)
        out["df"] = df
        return out

    def generate_proposal_for_each_bank(self):
        data = {}
        for bank in self.bank_list:
            data[bank] = self.calculate_compound_loan_payments()
        return data

    def calculate_compound_loan_payments(self):
        monthly_interest_rate = random.uniform(2.0, 3.0) / 100
        compound_amount = self.loan_amount * \
            (1 + monthly_interest_rate) ** self.loan_term
        monthly_payment = compound_amount / self.loan_term
        return {
            "interest_rate": round(monthly_interest_rate * 100, 2),
            "monthly_payment": int(monthly_payment),
            "total_payment": int(compound_amount)
        }
