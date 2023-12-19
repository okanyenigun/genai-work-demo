import ast
import json
import os
import environ
import PIL.Image
import google.generativeai as genai
from django.conf import settings
from django.core.cache import cache
from loan.services.translatee import Translatee


env = environ.Env()
environ.Env.read_env()


class Chatter:

    def __init__(self):
        genai.configure(api_key=env("GEMINI_KEY"))

    def chat(self, message):
        # translate if necessary
        message_en = self._translate(message)
        print("message_en: ", message_en)
        #  decide intention
        intent = self.decide_intention(message, message_en)
        print("intent: ", intent)
        if intent == "Data Drift":
            return self.answer_data_drift(message, message_en)
        elif intent == "Concept Drift":
            return self.answer_concept_drift(message, message_en)
        elif intent == "Model Performance":
            return self.answer_model_performance(message, message_en)
        elif intent == "Model Hyperparameters":
            return self.answer_model_hyperparameters(message, message_en)
        else:
            return self.answer_irrelevant()
        #  data drift image

        # concept drift image

        # model performance

        # model parameters
        return

    def _translate(self, message):
        model = Translatee()
        lang = model._detect_language(message)
        message_en = model._translate_to_en(message)
        return message_en

    def decide_intention(self, message, message_en):
        prompt = """
        You are a chatbot in a credit risk score machine learning model monitoring tool. User can ask questions about specific topics. Candidate topics are: ["Data Drift", "Concept Drift", "Model Performance", "Model Hyperparameters", "Irrelevant"]. When a question is asked, you should understand the intent and label the questions topic in one of them. Meanings of topics: 

        Data Drift: There is a live chart in the app which displays the data drift condition. It shows the distribution of a feature named loan_income_percent, its existing distribution in the training phase and the its distribution in production.

        Concept Drift: There is another live chart in the app, this chart displays the concept drift condition. It displays the scatter plot of loan_income_percent feature vs target feature, loan_status. Again, it displays existing status vs production status.

        Model Performance: It is a table that displays the for each model the metrics, accuracy, precision, and recall for previous trained model and the current model. (Models can be retrained alive.)

        Model Hyperparameters: There is another table, it displays the hyperparameter values used in model training. It displays the current model's values and previous model's values.

        Irrelevant: Any questions which is not about any of these four topics can be labelled as irrelevant. It is too important that we never answer these type of questions. We just remind the user to ask anything related with other 4 topics.
        
        
        The messages from user will be in Turkish.
        
        You will understand the intent of the text sent by the customer. 
        Return your response in a JSON format. For example: response: {'intent': 'Concept Drift'}.
        """

        query = f"{prompt} the message from the user is: {message}"

        model = genai.GenerativeModel('gemini-pro')

        response = model.generate_content(query)
        string = response.text.replace("`", "").strip()
        try:
            return ast.literal_eval(string)["intent"]
        except:
            return json.loads(string)["intent"]

    def answer_data_drift(self, message, message_en):
        path = os.path.join(
            settings.STATICFILES_DIRS[0], "files", "monitor", "data_drift.png")
        img = PIL.Image.open(path)
        model = genai.GenerativeModel('gemini-pro-vision')
        response = model.generate_content(img)
        definition = response.text
        response = model.generate_content(
            [f"Based on this graph, which is presumed to be from a banking credit scoring model (just a feature of it named loan_income_percent), analyze the condition of data drift. How do you evaluate the drift here? It is dangerous or not? What are your suggestion based on this conditions? What should we do?, Additionally, also focus on the question of the user: {message_en}", img])
        explanation = response.text
        return {
            "intent": "Data Drift",
            "definition": definition,
            "explanation": explanation
        }

    def answer_concept_drift(self, message, message_en):
        path = os.path.join(
            settings.STATICFILES_DIRS[0], "files", "monitor", "concept_drift.png")
        img = PIL.Image.open(path)
        model = genai.GenerativeModel('gemini-pro-vision')
        response = model.generate_content(img)
        definition = response.text
        response = model.generate_content(
            [f"Based on this graph, which is presumed to be from a banking credit scoring model, it is a scatter of a feature loan_income_percent vs target feature loan_status, analyze the condition of concept drift. How do you evaluate the drift here? It is dangerous or not? What are your suggestion based on this conditions? What should we do?, Additionally, also focus on the question of the user: {message_en}", img])
        explanation = response.text
        return {
            "intent": "Concept Drift",
            "definition": definition,
            "explanation": explanation
        }

    def answer_model_performance(self, message, message_en):
        data_json = cache.get('model_parameters')
        prompt = """Here, you will be sent a json data which is converted from a pandas dataframe. This table includes some models and their performance metric values. There are two states of the models. Previously trained model's scores and current model version's scores. You will answer the asked question only based on this data. Analyze each metrics and models and use your knowledge about these models and metrics in general to answer the question.
        """
        query = f"{prompt}. The provided JSON data is: {data_json} the question from the user is: {message_en}"

        model = genai.GenerativeModel('gemini-pro')

        response = model.generate_content(query)
        return {"definition": "", "explanation": response.text}

    def answer_model_hyperparameters(self, message, message_en):

        data_json = cache.get('model_hyperparameters')
        prompt = """Here, you will be sent a json data which is converted from a pandas dataframe. This table includes some models and their hyperparameters values used in training. There are two states of the models. Previously trained model's values and current model version's values. You will answer the asked question only based on this data. Analyze each hyperparameter and models and use your knowledge about these models and hyperparameters in general to answer the question.
        """
        query = f"{prompt}. The provided JSON data is: {data_json} the question from the user is: {message_en}"

        model = genai.GenerativeModel('gemini-pro')

        response = model.generate_content(query)
        print(response.text)
        print()
        return {"definition": " ", "explanation": response.text}

    def answer_irrelevant(self):
        query = """This question was irrelevant. You are only anwering questions about these topics:"Data Drift", "Concept Drift", "Model Performance", "Model Hyperparameters". Warn and inform the user about this. 
        """
        model = genai.GenerativeModel('gemini-pro')

        response = model.generate_content(query)

        return {"definition": "", "explanation": response.text}
