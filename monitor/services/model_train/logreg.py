import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import RandomizedSearchCV
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix, roc_auc_score, roc_curve


class LogRegModel:

    def __init__(self, X_train, y_train, X_test, y_test, X_real, y_real):
        self.fit_params = {
            'random_state': 10,
            "n_jobs": -1,
        }
        self.param_dist = {
            'C': np.logspace(-4, 4, 20),
            'penalty': ['l1', 'l2'],
            'solver': ['liblinear']
        }
        self.X_train = X_train
        self.y_train = y_train
        self.X_test = X_test
        self.y_test = y_test
        self.X_real = X_real
        self.y_real = y_real
        self._evaluations = {}
        self._real_model = None

    def get_real_model(self):
        best_params, best_model = self._search_hyperparameter()
        self._eval_training(best_model, best_params)
        self._real_model = self._train_real_model(best_params)
        return self._real_model, self._evaluations

    def _search_hyperparameter(self):
        log_reg = LogisticRegression(**self.fit_params)
        random_search = RandomizedSearchCV(
            log_reg, param_distributions=self.param_dist, n_iter=3, cv=5, verbose=1, n_jobs=-1)
        random_search.fit(self.X_train, self.y_train)
        return random_search.best_params_, random_search.best_estimator_

    def _eval_training(self, best_model, best_params):
        y_pred = best_model.predict(self.X_test)
        y_pred_proba = best_model.predict_proba(self.X_test)[:, 1]

        # Calculate metrics
        self._evaluations = {
            "Accuracy": accuracy_score(self.y_test, y_pred),
            "Precision": precision_score(self.y_test, y_pred),
            "Recall": recall_score(self.y_test, y_pred),
            "F1 Score": f1_score(self.y_test, y_pred),
            "Confusion Matrix": confusion_matrix(self.y_test, y_pred),
            "ROC-AUC Score": roc_auc_score(self.y_test, y_pred_proba),
            "best_params": best_params
        }

        fpr, tpr, thresholds = roc_curve(self.y_test, y_pred_proba)
        self._evaluations["roc_curve_data"] = (fpr, tpr, thresholds)
        return

    def _train_real_model(self, best_params):
        log_reg = LogisticRegression(**self.fit_params, **best_params)
        log_reg.fit(self.X_real, self.y_real)
        return log_reg
