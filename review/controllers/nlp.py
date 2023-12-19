from review.models import AiModels
from review.services.nlp.translate.facade import TranslateFacade
from review.services.nlp.translate.export import TranslationExport
from review.services.nlp.sentiment.facade import SentimentFacade
from review.services.nlp.sentiment.export import SentimentExport
from review.services.nlp.zero.facade import ZeroFacade


class NlpController:

    @staticmethod
    def get_translate_models():
        return AiModels.objects.filter(use_case="translate")

    @staticmethod
    def post_create_translate_model_record(form):
        if form.is_valid():
            form = form.cleaned_data
            form["use_case"] = "translate"
            _, created = AiModels.objects.get_or_create(
                name=form["name"].strip(),
                source=form["source"].strip(),
                language_support=form["language_support"].strip(),
                defaults={
                    'use_case': form['use_case'].strip(),
                })
            return created, form
        return None, None

    @staticmethod
    def get_text_translate(req):
        text = req.get("text_text", "")
        model = req.get("text_model")
        T = TranslateFacade(
            {"case": "text", "text": text, "model": int(model)})
        translation_data = T.translate()
        return translation_data

    @staticmethod
    def get_cross_translate(req):
        text = req.get("cross_text", "")
        T = TranslateFacade({"case": "cross", "text": text})
        translation_data = T.translate()
        return translation_data

    @staticmethod
    def post_translate_all(post):
        data_source = post.get("all_data_source")
        app_id = int(post.get("all_app_id"))
        model_id = int(post.get("all_model_id"))
        T = TranslateFacade(
            {"case": "all", "data_source": data_source, "app_id": app_id, "model_id": model_id})
        return T.translate()

    @staticmethod
    def post_translate_export(post):
        app_id = post.get("app_id")
        data_source = post.get("data_source")
        model_id = int(post.get("translation_model"))
        file_format = post.get("file_format")
        T = TranslationExport()
        return T.export(data_source, model_id, app_id, file_format)

    @staticmethod
    def get_sentiment_models():
        return AiModels.objects.filter(use_case="sentiment")

    @staticmethod
    def post_create_sentiment_model_record(form):
        if form.is_valid():
            form = form.cleaned_data
            form["use_case"] = "sentiment"
            _, created = AiModels.objects.get_or_create(
                name=form["name"].strip(),
                source=form["source"].strip(),
                language_support=form["language_support"].strip(),
                defaults={
                    'use_case': form['use_case'].strip(),
                })
            return created, form
        return None, None

    @staticmethod
    def get_text_sentiment(req):
        text = req.get("text_text", "")
        model = req.get("text_model")
        S = SentimentFacade(
            {"case": "text", "text": text, "model": int(model)})
        sentiment_data = S.analyze()
        return sentiment_data

    @staticmethod
    def get_cross_sentiment(req):
        text = req.get("cross_text", "")
        S = SentimentFacade({"case": "cross", "text": text})
        sentiment_data = S.analyze()
        return sentiment_data

    @staticmethod
    def post_sentiment_all(post):
        data_source = post.get("all_data_source")
        app_id = int(post.get("all_app_id"))
        model_id = int(post.get("all_model_id"))
        review_type = post.get("review_type")
        S = SentimentFacade(
            {"case": "all", "data_source": data_source, "app_id": app_id,
             "model_id": model_id, "review_type": review_type})
        return S.analyze()

    @staticmethod
    def post_sentiment_export(post):
        app_id = post.get("app_id")
        data_source = post.get("data_source")
        model_id = int(post.get("sentiment_model"))
        file_format = post.get("file_format")
        S = SentimentExport()
        return S.export(data_source, model_id, app_id, file_format)

    @staticmethod
    def get_zero_models():
        return AiModels.objects.filter(use_case="zero-shot")

    @staticmethod
    def post_create_zero_model_record(form):
        if form.is_valid():
            form = form.cleaned_data
            form["use_case"] = "zero-shot"
            _, created = AiModels.objects.get_or_create(
                name=form["name"].strip(),
                source=form["source"].strip(),
                language_support=form["language_support"].strip(),
                defaults={
                    'use_case': form['use_case'].strip(),
                })
            return created, form
        return None, None

    @staticmethod
    def get_text_zero(req):
        text = req.get("text_text", "")
        model = req.get("text_model")
        labels = req.get("text_labels").split(",")
        labels = [label.strip() for label in labels]
        Z = ZeroFacade(
            {"case": "text", "text": text, "model": int(model), "labels": labels})
        zero_data = Z.analyze()
        return zero_data
