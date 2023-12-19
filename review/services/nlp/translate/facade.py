import threading
import time
import random
import translate
# import googletrans
import concurrent.futures
import translators as ts
from transformers import pipeline
from deep_translator import GoogleTranslator
from django.db import transaction
from review.models import AiModels, AppStoreReview, TranslatedReviews


class TranslateFacade:

    def __init__(self, form):
        self.form = form

    def translate(self):
        if self.form["case"] == "text":
            return self._text_translate(self.form["model"], self.form["text"])
        elif self.form["case"] == "cross":
            return self._cross_translate()
        elif self.form["case"] == "all":
            return self._all_translate()

    def _all_translate(self):
        model_record = AiModels.objects.filter(
            use_case="translate").get(id=self.form["model_id"])
        start_count = TranslatedReviews.objects.filter(
            ai_model=model_record).count()
        # reviews_without_translation = AppStoreReview.objects.exclude(
        #     id__in=TranslatedReviews.objects.filter(ai_model=model_record).values('id'))
        reviews_without_translation = AppStoreReview.objects.all()
        tasks = [(model_record, review)
                 for review in reviews_without_translation]
        print("count: ", reviews_without_translation.count())
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
            executor.map(self._process_translation_task, tasks)

        after_count = TranslatedReviews.objects.filter(
            ai_model=model_record).count()

        return {"modelname": model_record.name, "count": after_count-start_count}

    def _process_translation_task(self, task):
        model_record, review = task
        try:
            matching_records = TranslatedReviews.objects.filter(
                review=review.id)
            if matching_records:
                return
            translated_text = self._text_translate(
                model_record.id, review.review)
            # print(
            #     f"Processing review {review.id} in thread: {threading.current_thread().name}")
            with transaction.atomic():
                if translated_text["translated_text"] is None:
                    translated_text["translated_text"] = ""
                _, created = TranslatedReviews.objects.get_or_create(
                    translated_text=translated_text["translated_text"],
                    review=review.id,
                    ai_model=model_record,
                )
        except Exception as e:
            print("Error: ", e, review)

        return translated_text, review

    def _text_translate(self, model_id, text):
        max_retries = 5
        retries = 0

        model_record = AiModels.objects.get(id=model_id)
        while retries < max_retries:
            try:
                if model_record.source == "huggingface":
                    return self._hg_translate(model_record, text)
                elif model_record.source == "library":
                    return self._library_translate(model_record, text)
            except Exception as e:
                time.sleep(random.randint(1, 6))
                retries += 1
                print("retry: ", retries)
                print(e)
        raise Exception("Max retries reached for translation request")

    def _cross_translate(self):
        data = {}
        model_records = AiModels.objects.filter(use_case="translate")
        for model in model_records:
            data[model.name] = self._text_translate(
                model.id, self.form["text"])
        return data

    def _hg_translate(self, model_record, text):
        translator = pipeline(
            "translation", model=model_record.name)
        resp = translator(text, src_lang="tr", tgt_lang="en")
        translated_text = resp[0]['translation_text']
        return {"translated_text": translated_text}

    def _library_translate(self, model_record, text):
        if model_record.name == "googletrans":
            translator = googletrans.Translator()
            translated_text = translator.translate(
                text, src="tr", dest="en").text
        elif model_record.name == "deep_translator":
            translated_text = GoogleTranslator(
                source='tr', target='en').translate(text)
        elif model_record.name == "translate":
            translator = translate.Translator(from_lang="tr", to_lang="en")
            translated_text = translator.translate(text)
        elif model_record.name == "translators":
            translated_text = ts.translate_text(text, translator="bing",
                                                from_language="tr", to_language="en")
        return {"translated_text": translated_text}
