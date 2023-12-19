import os
import torch
import joblib
import pickle
import numpy as np
from transformers import DistilBertForSequenceClassification, DistilBertTokenizer, BertForTokenClassification, BertTokenizerFast, AutoModelForTableQuestionAnswering, AutoTokenizer, pipeline
from django.conf import settings
from loan.services.translatee import Translatee


class OpenSourceApi:

    def __init__(self):
        pass

    def decide_intention(self, message, message_en):
        # load
        model, tokenizer, device = self._load_intent_model()
        # predict
        intent = self._predict_intent(message_en, model, tokenizer, device)
        return intent.strip()

    def ner_loan_values(self, message, message_en):

        label_list_path = os.path.join(
            settings.STATICFILES_DIRS[0], "files", "models", "ner_label_list.pkl")
        with open(label_list_path, 'rb') as file:
            label_list = pickle.load(file)

        model, tokenizer = self._load_ner_model()
        inputs = tokenizer(message_en, return_tensors="pt")
        with torch.no_grad():
            outputs = model(**inputs)
        logits = outputs.logits
        predictions = torch.argmax(logits, dim=2)
        predicted_label_ids = predictions[0].tolist()
        predicted_labels = [label_list[label_id]
                            for label_id in predicted_label_ids]

        tokens = message_en.split(" ")
        loan_amount, loan_term = self._extract_ner(predicted_labels, tokens)
        return loan_amount, loan_term

    def data_question_asking(self, message, message_en, data):
        questioner = self._load_question_model()
        result = questioner(
            {'table': data["df"].astype(str), 'query': message_en})
        answer = result['cells'][0].strip()
        return {
            "answer": answer,
            "promoting_text": "",
        }

    def ask_to_document(self, message, message_en, text):
        text_path = os.path.join(
            settings.STATICFILES_DIRS[0], "files", "models", "texts_en.pkl")
        with open(text_path, 'rb') as file:
            translated = pickle.load(file)
        qa_pipeline = pipeline(
            "question-answering", model="salti/bert-base-multilingual-cased-finetuned-squad")
        answer = qa_pipeline(question=message_en, context=translated)
        tr_answer = Translatee.translate_to_tr(answer["answer"])
        return {
            "answer": tr_answer
        }

    def _load_question_model(self):
        model = AutoModelForTableQuestionAnswering.from_pretrained(
            "google/tapas-large-finetuned-wtq")
        tokenizer = AutoTokenizer.from_pretrained(
            "google/tapas-large-finetuned-wtq")
        questioner = pipeline('table-question-answering',
                              model=model, tokenizer=tokenizer)
        return questioner

    def _extract_ner(self, predicted_labels, tokens):
        amount_idx = predicted_labels.index("B-AMOUNT")
        loan_amount = tokens[amount_idx]
        try:
            loan_amount = int(loan_amount)
        except:
            try:
                loan_amount = int(tokens[amount_idx+1])
            except:
                loan_amount = 0

        term_idx = predicted_labels.index("B-TERM")
        loan_term = tokens[term_idx]
        try:
            loan_term = int(loan_term)
        except:
            try:
                loan_term = int(tokens[term_idx+1])
            except:
                loan_amount = 0
        return loan_amount, loan_term

    def _load_ner_model(self):
        model_path = os.path.join(
            settings.STATICFILES_DIRS[0], "files", "models", "ner_trained_model")
        model = BertForTokenClassification.from_pretrained(model_path)
        tokenizer = BertTokenizerFast.from_pretrained(model_path)
        return model, tokenizer

    def _load_intent_model(self):
        model_path = os.path.join(
            settings.STATICFILES_DIRS[0], "files", "models", "trained_model_intent")
        model = DistilBertForSequenceClassification.from_pretrained(model_path)
        tokenizer = DistilBertTokenizer.from_pretrained(model_path)

        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        return model, tokenizer, device

    def _predict_intent(self, text, model, tokenizer, device):
        # Encode the text using the same tokenizer used during training
        inputs = tokenizer.encode_plus(
            text,
            None,
            add_special_tokens=True,
            max_length=512,
            pad_to_max_length=True,
            return_attention_mask=True,
            return_tensors='pt',
        )

        # Move the inputs to the GPU if available
        inputs = {key: value.to(device) for key, value in inputs.items()}

        with torch.no_grad():
            # Forward pass, calculate logit predictions
            outputs = model(**inputs)
            logits = outputs.logits

        # Move logits to CPU
        logits = logits.detach().cpu().numpy()
        # Use softmax to calculate probabilities
        probabilities = torch.nn.functional.softmax(
            torch.tensor(logits), dim=1).numpy()
        # Find the highest probability as the predicted class
        predicted_class_idx = np.argmax(probabilities, axis=1).flatten()
        encoder_path = os.path.join(
            settings.STATICFILES_DIRS[0], "files", "models", "label_encoder_intent.joblib")
        label_encoder = joblib.load(encoder_path)
        # Convert predicted class index to label
        predicted_class = label_encoder.inverse_transform(predicted_class_idx)[
            0]
        return predicted_class
