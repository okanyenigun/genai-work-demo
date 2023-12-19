import os
import pickle
from django.conf import settings
from django.core.cache import cache
from loan.services.bank import BankApi
from loan.services.oai import OpenApi
from loan.services.translatee import Translatee
from loan.services.open_source import OpenSourceApi
from loan.services.gemai import GeminiApi


class Controller:

    def __init__(self):
        self._models = {
            "opensource": OpenSourceApi,
            "openai": OpenApi,
            "gemini": GeminiApi,
            "translate": Translatee()
        }
        self.cache_bank_response_key = 'bank_responses'

    def collect_bank_responses(self, loan_amount, loan_term):
        B = BankApi(loan_amount, loan_term)
        bank_responses = B.fetch_response()
        cache.set(self.cache_bank_response_key, bank_responses, 3600)
        return bank_responses

    def chat(self, message, selected_model):
        # get model
        if selected_model == "btnradio1":
            model_obj = self._models["opensource"]()
        elif selected_model == "btnradio2":
            model_obj = self._models["openai"]()
        elif selected_model == "btnradio3":
            model_obj = self._models["gemini"]()
        # detect language
        lang = self._models["translate"]._detect_language(message)
        print("lang: ", lang)
        # translate if necessary
        message_en = self._models["translate"]._translate_to_en(message)
        print("message_en: ", message_en)
        # decide topic
        intention = model_obj.decide_intention(message, message_en)
        intention = intention.replace("_", " ")
        print("intention: ", intention)
        try:
            if intention == "Request Loan Proposals":
                return self.request_loan_proposals(model_obj, message, message_en)
            elif intention == "Inquire Loan Details":
                return self.inquire_loan_details(model_obj, message, message_en)
            elif intention == "Proceed With Loan":
                return self.proceed_with_loan()
            elif intention == "General Inquiry":
                return self.general_inquiry(model_obj, message, message_en)
        except:
            return {
                "error": "Bir şeyler yanlış gitti."
            }
        return

    def request_loan_proposals(self, model, message, message_en):
        loan_amount, loan_term = model.ner_loan_values(message, message_en)
        bank_responses = self.collect_bank_responses(loan_amount, loan_term)
        return {
            "intent": "Request Loan Proposals",
            "bank_responses": bank_responses["json"],
            "loan_amount": loan_amount,
            "loan_term": loan_term
        }

    def inquire_loan_details(self, model, message, message_en):
        bank_responses = cache.get(self.cache_bank_response_key)
        response = model.data_question_asking(
            message, message_en, bank_responses)
        return {
            "intent": "Inquire Loan Details",
            "answer": response["answer"],
            "promoting_text": response["promoting_text"],
        }

    def proceed_with_loan(self):
        return {
            "intent": "Proceed With Loan"
        }

    def general_inquiry(self, model, message, message_en):
        text_path = os.path.join(
            settings.STATICFILES_DIRS[0], "files", "models", "texts.pkl")
        with open(text_path, 'rb') as file:
            text = pickle.load(file)
        response = model.ask_to_document(message, message_en, text)
        return {
            "intent": "General Inquiry",
            "answer": response["answer"],
        }
