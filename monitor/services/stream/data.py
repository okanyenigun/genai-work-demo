import numpy as np


class DataGenerator:

    def __init__(self, df):
        self.df = df

    def generate(self, data_type):
        if data_type == "normal":
            return self.df.sample(1)
        elif data_type == "data_drift":
            row = self.df.sample(1)
            # Generating a right-skewed value between 0.7 and 1
            row['loan_percent_income'] = 0.7 + np.random.beta(5, 2) * 0.3
            return row
        elif data_type == "concept_drift":
            row = self.df.sample(1)
            if row['loan_percent_income'].iloc[0] < 0.1:
                row['loan_status'] = 0
            else:
                row['loan_status'] = 1
            return row
