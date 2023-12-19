import time
import random
import threading
import concurrent.futures
from transformers import pipeline
from django.db import transaction
from review.models import AiModels, AppStoreReview, SentimentReview, TranslatedReviews


class SentimentFacade:

    def __init__(self, form):
        self.form = form

    def analyze(self):
        if self.form["case"] == "text":
            return self._text_sentiment(self.form["model"], self.form["text"])
        elif self.form["case"] == "cross":
            return self._cross_sentiment()
        elif self.form["case"] == "all":
            return self._all_sentiment()

    def _all_sentiment(self):
        model_record = AiModels.objects.filter(
            use_case="sentiment").get(id=self.form["model_id"])
        start_count = SentimentReview.objects.filter(
            ai_model=model_record).count()
        if self.form["review_type"] == "tr":
            reviews_without_sentiment = AppStoreReview.objects.exclude(
                id__in=SentimentReview.objects.filter(ai_model=model_record).values('review_id'))
        elif self.form["review_type"] == "en":
            # reviews_without_sentiment = TranslatedReviews.objects.exclude(
            #     id__in=SentimentReviews.objects.filter(ai_model=model_record).values('translated_review_id'))
            reviews_without_sentiment = TranslatedReviews.objects.all()
        tasks = [(model_record, review)
                 for review in reviews_without_sentiment]

        with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
            executor.map(self._process_sentiment_task, tasks)

        after_count = SentimentReview.objects.filter(
            ai_model=model_record).count()

        return {"modelname": model_record.name, "count": after_count-start_count}

    def _process_sentiment_task(self, task):
        model_record, translated_review = task
        try:
            print(
                f"Processing translated review {translated_review.id} in thread: {threading.current_thread().name}")
            if self.form["review_type"] == "tr":
                sentiment = self._text_sentiment(
                    model_record.id, review.review)
                with transaction.atomic():
                    _, created = SentimentReviews.objects.get_or_create(
                        review=review,
                        translated_review=None,
                        ai_model=model_record,
                        defaults={
                            'sentiment_color': sentiment['color'],
                            'label': sentiment["label"],
                            'score': sentiment["score"]
                        }
                    )
            elif self.form["review_type"] == "en":
                match_records = SentimentReview.objects.filter(
                    review=translated_review.review).filter(ai_model=model_record)
                if match_records:
                    print("skipped")
                    return
                sentiment = self._text_sentiment(
                    model_record.id, translated_review.translated_text)
                with transaction.atomic():
                    _, created = SentimentReview.objects.get_or_create(
                        review=translated_review.review,
                        translated_review=translated_review.id,
                        ai_model=model_record,
                        defaults={
                            'sentiment_color': sentiment['color'],
                            'label': sentiment["label"],
                            'score': sentiment["score"]
                        }
                    )

        except Exception as e:
            print(e)

        return

    def _cross_sentiment(self):
        data = {}
        model_records = AiModels.objects.filter(use_case="sentiment")
        for model in model_records:
            data[model.name] = self._text_sentiment(
                model.id, self.form["text"])
        return data

    def _text_sentiment(self, model_id, text):
        max_retries = 5
        retries = 0

        model_record = AiModels.objects.get(id=model_id)
        while retries < max_retries:
            try:
                pipe = pipeline("text-classification", model=model_record.name)
                resp = pipe(text)[0]
                resp = self._convert_label(resp)
                return resp
            except Exception as e:
                print(e)
                time.sleep(random.randint(1, 6))
                retries += 1
                print("retry: ", retries)
            raise Exception("Max retries reached for sentiment request")

    def _convert_label(self, result):
        result["label"] = result["label"].lower()
        if result["label"] == "1 star" or result["label"] == "2 stars":
            color = "negative"
        elif result["label"] == "label_0":
            color = "negative"
        elif result["label"] == "label_1":
            color = "neutral"
        elif result["label"] == "label_2":
            color = "positive"
        elif result["label"] == "3 stars":
            color = "neutral"
        elif result["label"] == "4 stars" or result["label"] == "5 stars":
            color = "positive"
        elif result["label"] == "positive":
            color = "positive"
        elif result["label"] == "negative":
            color = "negative"
        elif result["label"] == "neutral":
            color = "neutral"
        result["color"] = color
        return result
