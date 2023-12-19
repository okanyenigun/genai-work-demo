import os
import pickle
import json
import pandas as pd
import numpy as np
from sklearn.metrics import accuracy_score, precision_score, recall_score
from django.conf import settings
from django.core.cache import cache
from monitor.services.stream.data import DataGenerator
from monitor.services.model_train.pipe import ModelGenerator


class StreamFacade:

    def __init__(self):
        self.folder_path = os.path.join(
            settings.STATICFILES_DIRS[0], "files", "monitor")
        self.df = pd.read_csv(os.path.join(self.folder_path, "data.csv"))
        self._fillna()
        self.storage = {
            "model_trained": 0,
            "data_drift_counts": [0] * 11,
            "concept_drift_values": [],
            "predictions": {
                "logreg": [],
                "rf": [],
            },
            "ground_truth": {
                "logreg": [],
                "rf": []
            },
            "new_rows": [],
            "last_model_trained_row": 0,
        }
        print("initialization ended")

    async def stream(self, tour, data_type):
        #  load
        encoders, logreg_model, rf_model, evaluations = self._load()
        # get data
        new_row, row_string = self.generate_data(data_type)
        self.storage[tour] = new_row
        # predict
        logreg_pred = self.upcoming_prediction(
            new_row, encoders, logreg_model, "logreg")
        rf_pred = self.upcoming_prediction(new_row, encoders, rf_model, "rf")
        #  model parameters table
        model_parameters = self.get_model_parameters_table(evaluations)
        #  model evaluations table
        model_evaluations, logreg_accuracy, rf_accuracy = self.get_model_evaluations_table(
            evaluations)
        # data drift
        data_drift_existed_counts, data_drift_new_points = self.drift_data(
            new_row)
        # concept drift
        concept_drift_existed_values, concept_drift_new_points = self.drift_concept(
            new_row)

        # if necessary retrain
        self.check_model_performance(logreg_accuracy, rf_accuracy, tour)

        return json.dumps(
            {
                "logreg_pred": logreg_pred,
                "rf_pred": rf_pred,
                "inputs": row_string,
                "model_parameters": model_parameters,
                "model_evaluations": model_evaluations,
                "data_drift_existed_counts": data_drift_existed_counts,
                "data_drift_new_points": data_drift_new_points,
                "concept_drift_existed_values": concept_drift_existed_values,
                "concept_drift_new_points": concept_drift_new_points
            })

    def _load(self):

        with open(os.path.join(self.folder_path, f"encoders_{self.storage['model_trained']}.pkl"), 'rb') as file:
            encoders = pickle.load(file)
        with open(os.path.join(self.folder_path, f"logreg_model_{self.storage['model_trained']}.pkl"), 'rb') as file:
            logreg_model = pickle.load(file)
        with open(os.path.join(self.folder_path, f"rf_model_{self.storage['model_trained']}.pkl"), 'rb') as file:
            rf_model = pickle.load(file)
        with open(os.path.join(self.folder_path, f"evaluations_{self.storage['model_trained']}.pkl"), 'rb') as file:
            evaluations = pickle.load(file)

        return encoders, logreg_model, rf_model, evaluations

    def _fillna(self):
        self.df['person_emp_length'] = self.df['person_emp_length'].fillna(
            self.df['person_emp_length'].median())
        self.df['loan_int_rate'] = self.df['loan_int_rate'].fillna(
            self.df['loan_int_rate'].median())
        return

    def generate_data(self, data_type):
        D = DataGenerator(self.df)
        new_row = D.generate(data_type)
        formatted_string = ', '.join(
            f"{col}: {val}" for col, val in new_row.items())
        self.storage["new_rows"].append(new_row)
        return new_row, formatted_string

    def upcoming_prediction(self, new_row, encoders, model, modelname):
        M = ModelGenerator(self.df)
        pred = int(M.predict(encoders, new_row, model)[0])
        new_row.reset_index(inplace=True, drop=True)
        if modelname == "logreg":
            self.storage["predictions"]["logreg"].append(pred)
            self.storage["ground_truth"]["logreg"].append(
                new_row.loc[0, "loan_status"])
        elif modelname == "rf":
            self.storage["predictions"]["rf"].append(pred)
            self.storage["ground_truth"]["rf"].append(
                new_row.loc[0, "loan_status"])
        return pred

    def get_model_parameters_table(self, evaluations):
        if self.storage['model_trained'] > 0:
            with open(os.path.join(self.folder_path, f"evaluations_{self.storage['model_trained']-1}.pkl"), 'rb') as file:
                previous_evaluations = pickle.load(file)
        else:
            previous_evaluations = evaluations
        logreg_params = previous_evaluations["logreg"]["best_params"]
        new_logreg_params = evaluations["logreg"]["best_params"]
        rf_params = previous_evaluations["rf"]["best_params"]
        new_rf_params = evaluations["rf"]["best_params"]
        data = []
        for key, value in logreg_params.items():
            if key == "C":
                row = ["Logistic Regression", key, round(
                    value, 2), round(new_logreg_params[key], 2)]
            else:
                row = ["Logistic Regression", key,
                       value, new_logreg_params[key]]
            data.append(row)
        for key, value in rf_params.items():
            row = ["Random Forest", key, value, new_rf_params[key]]
            data.append(row)

        df = pd.DataFrame(
            data, columns=['Model Name', 'Parameter Name', 'Previous Model Value', "New Model Value"])

        data_dict = df.to_dict(orient="records")
        # Convert the dictionary to JSON
        data_json = json.dumps(data_dict)
        cache.set('model_hyperparameters', data_json,
                  timeout=3000)  # 300 seconds timeout
        return data_json

    def calculate_performance_metrics(self, modelname):
        accuracy = accuracy_score(
            self.storage["ground_truth"][modelname], self.storage["predictions"][modelname])
        precision = precision_score(
            self.storage["ground_truth"][modelname], self.storage["predictions"][modelname])
        recall = recall_score(
            self.storage["ground_truth"][modelname], self.storage["predictions"][modelname])
        return round(accuracy, 2), round(precision, 2), round(recall, 2)

    def get_model_evaluations_table(self, evaluations):
        if self.storage['model_trained'] > 0:
            with open(os.path.join(self.folder_path, f"evaluations_{self.storage['model_trained']-1}.pkl"), 'rb') as file:
                previous_evaluations = pickle.load(file)
        else:
            previous_evaluations = evaluations
        logreg_params = previous_evaluations["logreg"]
        new_logreg_params = evaluations["logreg"]
        rf_params = previous_evaluations["rf"]
        new_rf_params = evaluations["rf"]

        logreg_accuracy, logreg_precision, logreg_recall = self.calculate_performance_metrics(
            "logreg")
        rf_accuracy, rf_precision, rf_recall = self.calculate_performance_metrics(
            "rf")

        data = []
        keys = ["Accuracy", "Precision", "Recall"]
        for key in keys:
            if key == "Accuracy":
                row = ["Logistic Regression", key,
                       logreg_params[key], new_logreg_params[key], logreg_accuracy]
            elif key == "Precision":
                row = ["Logistic Regression", key,
                       logreg_params[key], new_logreg_params[key], logreg_precision]
            elif key == "Recall":
                row = ["Logistic Regression", key,
                       logreg_params[key], new_logreg_params[key], logreg_recall]
            data.append(row)
        for key in keys:
            if key == "Accuracy":
                row = ["Random Forest", key, rf_params[key],
                       new_rf_params[key], rf_accuracy]
            elif key == "Precision":
                row = ["Random Forest", key, rf_params[key],
                       new_rf_params[key], rf_precision]
            elif key == "Recall":
                row = ["Random Forest", key, rf_params[key],
                       new_rf_params[key], rf_recall]
            data.append(row)

        df = pd.DataFrame(
            data, columns=['Model Name', 'Metric Name', 'Previous Model Score', "New Model Score", "Performance"])

        df["Previous Model Score"] = df["Previous Model Score"].round(2)
        df["New Model Score"] = df["New Model Score"].round(2)

        data_dict = df.to_dict(orient="records")
        # Convert the dictionary to JSON
        data_json = json.dumps(data_dict)
        cache.set('model_parameters', data_json,
                  timeout=3000)  # 300 seconds timeout
        return data_json, logreg_accuracy, rf_accuracy

    def drift_data(self, new_row):
        existed = self.df['loan_percent_income'].tolist()
        # bin
        bins = np.arange(0, 1.1, 0.1)
        histogram, _ = np.histogram(existed, bins)
        histogram = [int(x/100) for x in list(histogram)]
        new_row.reset_index(inplace=True, drop=True)
        new_point = new_row.loc[0, "loan_percent_income"]
        self.storage["data_drift_counts"][int(round(new_point, 1) / 0.1)] += 1
        return histogram, self.storage["data_drift_counts"]

    def drift_concept(self, new_row):
        x = self.df['loan_percent_income'].tolist()
        x = [float(val) for val in x]
        y = self.df['loan_status'].tolist()
        y = [int(val) for val in y]
        existed_data = [{"x": xi, "y": yi} for xi, yi in zip(x, y)][:100]

        new_row.reset_index(inplace=True, drop=True)
        new_points = {
            "x": float(new_row.loc[0, "loan_percent_income"]), "y": int(new_row.loc[0, "loan_status"])}
        self.storage["concept_drift_values"].append(new_points)
        return existed_data, self.storage["concept_drift_values"]

    def check_model_performance(self, logreg_acc, rf_acc, tour):
        if logreg_acc < 0.65 and rf_acc < 0.65 and tour - self.storage["last_model_trained_row"] > 200:
            print("logreg_acc: ", logreg_acc)
            print("rf_acc: ", rf_acc)
            new_df = self.df.copy()
            for row in self.storage["new_rows"]:
                new_df = pd.concat([new_df, row], axis=0)
            M = ModelGenerator(new_df, count=self.storage["model_trained"]+1)
            M.train()
            self.storage["model_trained"] += 1
            self.storage["last_model_trained_row"] = tour
