import time
import random
from transformers import pipeline
from review.models import AiModels


class ZeroFacade:

    def __init__(self, form):
        self.form = form

    def analyze(self):
        if self.form["case"] == "text":
            return self._text_zero(self.form["model"], self.form["text"], self.form["labels"])

    def _text_zero(self, model_id, text, labels):
        max_retries = 5
        retries = 0

        model_record = AiModels.objects.get(id=model_id)
        while retries < max_retries:
            try:
                pipe = pipeline("zero-shot-classification",
                                model=model_record.name)
                resp = pipe(text, labels, multi_label=True)
                resp = self._convert_label(resp)
                return resp
            except Exception as e:
                print(e)
                time.sleep(random.randint(1, 6))
                retries += 1
                print("retry: ", retries)
            raise Exception("Max retries reached for zero-shot request")

    def _convert_label(self, resp):
        data = {}
        for i in range(len(resp["labels"])):
            data[resp["labels"][i]] = resp["scores"][i]
        return data
