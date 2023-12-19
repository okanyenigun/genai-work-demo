import pickle
import os
import pandas as pd
from imblearn.over_sampling import RandomOverSampler
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from django.conf import settings
from monitor.services.model_train.logreg import LogRegModel
from monitor.services.model_train.rf import RfModel


class ModelGenerator:

    def __init__(self, df, encoders=None, count=None):
        self.df = df
        self._encoders = {} if encoders == None else encoders
        self._models = {}
        self._evaluations = {}
        self._count = 0 if count == None else count

    def train(self):
        self._fillna()

        X_df, y_df = self._get_x_y()

        X_resampled, y_resampled = self._oversample(X_df, y_df)

        df_X_train, df_X_test, df_Y_train, df_Y_test = train_test_split(
            X_resampled, y_resampled, test_size=0.2, random_state=42, shuffle=True)

        df_X_train_scaled = self._transform_features(df_X_train, fit=True)
        df_X_test_scaled = self._transform_features(df_X_test, fit=False)

        X_train, X_test, y_train, y_test = self._get_x_y_for_model(
            df_X_train_scaled, df_X_test_scaled, df_Y_train, df_Y_test)

        X_real = self._transform_features(X_resampled, fit=True)

        L = LogRegModel(X_train, y_train, X_test, y_test, X_real, y_resampled)
        self._models["logreg"], self._evaluations["logreg"] = L.get_real_model()
        print("end of log reg")
        R = RfModel(X_train, y_train, X_test, y_test, X_real, y_resampled)
        self._models["rf"], self._evaluations["rf"] = R.get_real_model()
        print("end of rf")
        self._save_models()

        return self._models, self._evaluations, self._encoders

    def _fillna(self):
        self.df['person_emp_length'] = self.df['person_emp_length'].fillna(
            self.df['person_emp_length'].median())
        self.df['loan_int_rate'] = self.df['loan_int_rate'].fillna(
            self.df['loan_int_rate'].median())
        return

    def _get_x_y(self):
        X = self.df.drop('loan_status', axis=1)  # Features
        y = self.df['loan_status']  # Target
        return X, y

    def _oversample(self, X_df, y_df):
        ros = RandomOverSampler(random_state=42)
        X_resampled, y_resampled = ros.fit_resample(X_df, y_df)
        return X_resampled, y_resampled

    def _transform_features(self, X, fit=False):
        feature_df_list = []
        for col in X.columns:
            col_type = X[col].dtypes
            if col_type == "int64" or col_type == "float64":
                if fit:
                    scaler = StandardScaler()
                    scaler.fit(X[col].values.reshape(-1, 1))
                    self._encoders[col] = scaler

                scaler = self._encoders[col]
                scaled_values = list(scaler.transform(
                    X[col].values.reshape(-1, 1)))

                temp = pd.DataFrame(data=scaled_values, columns=[col])
                feature_df_list.append(temp)
            elif col_type == "object":
                if fit:
                    encoder = OneHotEncoder(
                        handle_unknown="infrequent_if_exist")
                    encoder.fit(X[col].values.reshape(-1, 1))
                    self._encoders[col] = encoder

                encoder = self._encoders[col]
                encoded_values = encoder.transform(
                    X[col].values.reshape(-1, 1)).toarray()
                encoded_col_list = list(encoder.get_feature_names_out())
                encoded_col_list = [col + "_" +
                                    x.split("_")[1] for x in encoded_col_list]

                temp = pd.DataFrame(data=encoded_values,
                                    columns=encoded_col_list)
                feature_df_list.append(temp)
        X_scaled = pd.concat(feature_df_list, axis=1)
        return X_scaled

    def _get_x_y_for_model(self, X_train, X_test, y_train, y_test):
        X_train = X_train.values
        X_test = X_test.values
        y_train = y_train.values.reshape(-1, 1)
        y_test = y_test.values.reshape(-1, 1)
        return X_train, X_test, y_train, y_test

    def _save_models(self):
        path = os.path.join(settings.STATICFILES_DIRS[0], "files", "monitor")
        pickle.dump(self._models["logreg"], open(os.path.join(
            path, f'logreg_model_{self._count}.pkl'), 'wb'))
        pickle.dump(self._models["rf"], open(os.path.join(
            path, f'rf_model_{self._count}.pkl'), 'wb'))
        pickle.dump(self._encoders, open(os.path.join(
            path, f"encoders_{self._count}.pkl"), "wb"))
        pickle.dump(self._evaluations, open(os.path.join(
            path, f"evaluations_{self._count}.pkl"), "wb"))
        return

    def predict(self, encoders, X, model):
        X = X.drop('loan_status', axis=1)
        self._encoders = encoders
        X_scaled = self._transform_features(X, fit=False)
        y_pred = model.predict(X_scaled)
        return y_pred
