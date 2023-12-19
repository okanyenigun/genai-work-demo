import asyncio
from django.shortcuts import render, redirect
from django.views import View
from django.contrib import messages
from asgiref.sync import sync_to_async
from django.utils.decorators import classonlymethod
from review.forms.apprecord_form import AppRecordForm
from review.forms.aimodels_form import AiModelForm
from review.controllers.data import DataController
from review.controllers.nlp import NlpController


class MainView(View):

    def get(self, request):
        return render(request, './templates/review/main.html')


class DataMainView(View):

    def get(self, request):
        return render(request, './templates/review/data/main.html')


class DataAppRecord(View):

    def get(self, request):
        form = AppRecordForm(use_required_attribute=False)
        records = DataController.get_apprecord_records()
        context = {"form": form, "records": records}
        return render(request, './templates/review/data/app_record.html', context)

    def post(self, request):
        context = {}
        form = AppRecordForm(request.POST)
        if form.is_valid():
            form = form.cleaned_data
            _, created = DataController.post_create_app_record(form)
            if not created:
                messages.error(
                    request, f"There is already a record for {form['name']}.")
            else:
                messages.success(request, "Record is saved successfully.")
            return redirect("review_data_app_record")
        else:
            messages.error(request, "Invalid form submission.")
        context["form"] = form
        return render(request, './templates/review/data/app_record.html', context)


class DataAppStore(View):

    @classonlymethod
    def as_view(cls, **initkwargs):
        view = super().as_view(**initkwargs)
        view._is_coroutine = asyncio.coroutines._is_coroutine
        return view

    async def get(self, request):
        app_records = await sync_to_async(list)(DataController.get_appstore_data())
        context = {"apps": app_records}
        get_summary_async = sync_to_async(DataController.get_review_summary)
        context["records"] = await get_summary_async()
        return render(request, './templates/review/data/app_store.html', context)

    async def post(self, request):

        counts = await DataController.post_pull_app_store_reviews(request.POST)

        if counts["ok"] > 0:
            messages.success(
                request, f"{counts['ok']} records are successfully saved. {counts['x']} records are skipped.")
        else:
            messages.error(
                request, f"{counts['x']} records are skipped. No insertion at all!")
        return redirect("review_data_app_store")


class DataExport(View):

    def get(self, request):
        context = {}
        context["apps"] = DataController.get_appstore_data()
        return render(request, './templates/review/data/export.html', context)

    def post(self, request):
        response = DataController.post_export_file(request.POST)
        if response:
            return response
        return render(request, './templates/review/data/export.html')


class NlpMainView(View):

    def get(self, request):

        return render(request, './templates/review/nlp/main.html')


class NlpTranslateMain(View):

    def get(self, request):
        context = {
            "models_form": AiModelForm(),
            "models_records": NlpController.get_translate_models(),
            "apps": DataController.get_appstore_data()
        }
        if "text" in request.GET:
            context["tab"] = "text"
            translation_data = NlpController.get_text_translate(request.GET)
            context["text_translated_text"] = translation_data["translated_text"]
            context["text_text"] = request.GET.get("text_text")
            context["text_model"] = str(request.GET.get("text_model"))
        elif "cross" in request.GET:
            context["tab"] = "cross"
            context["cross_translated"] = NlpController.get_cross_translate(
                request.GET)
        return render(request, './templates/review/nlp/translate/main.html', context)

    def post(self, request):
        context = {}
        if "models" in request.POST:
            context["tab"] = "models"
            context["models_form"] = AiModelForm(request.POST)
            context["models_records"] = NlpController.get_translate_models()
            created, form = NlpController.post_create_translate_model_record(
                form=AiModelForm(request.POST))
            if created == False:
                messages.error(
                    request, f"There is already a model for {form['name']}.")
            elif created == True:
                messages.success(request, "Model is saved successfully.")
                return render(request, './templates/review/nlp/translate/main.html', context)
            elif created is None:
                messages.error(request, "Invalid form submission.")
        elif "all" in request.POST:
            context["tab"] = "all"
            context["all_counts"] = NlpController.post_translate_all(
                request.POST)
        elif "export" in request.POST:
            context["tab"] = "export"
            response = NlpController.post_translate_export(request.POST)
            if response:
                return response
        return render(request, './templates/review/nlp/translate/main.html', context)


class NlpSentimentView(View):

    def get(self, request):
        context = {
            "models_form": AiModelForm(),
            "models_records": NlpController.get_sentiment_models(),
            "apps": DataController.get_appstore_data()
        }
        if "text" in request.GET:
            context["tab"] = "text"
            context["text_sentiment_data"] = NlpController.get_text_sentiment(
                request.GET)
            context["text_text"] = request.GET.get("text_text")
            context["text_model"] = str(request.GET.get("text_model"))
        elif "cross" in request.GET:
            context["tab"] = "cross"
            context["cross_sentiment_data"] = NlpController.get_cross_sentiment(
                request.GET)
        return render(request, './templates/review/nlp/sentiment/main.html', context)

    def post(self, request):
        context = {}
        if "models" in request.POST:
            context["tab"] = "models"
            context["models_form"] = AiModelForm(request.POST)
            context["models_records"] = NlpController.get_sentiment_models()
            created, form = NlpController.post_create_sentiment_model_record(
                form=AiModelForm(request.POST))
            if created == False:
                messages.error(
                    request, f"There is already a model for {form['name']}.")
            elif created == True:
                messages.success(request, "Model is saved successfully.")
                return render(request, './templates/review/nlp/translate/main.html', context)
            elif created is None:
                messages.error(request, "Invalid form submission.")
        elif "all" in request.POST:
            context["tab"] = "all"
            context["all_counts"] = NlpController.post_sentiment_all(
                request.POST)
        elif "export" in request.POST:
            context["tab"] = "export"
            response = NlpController.post_sentiment_export(request.POST)
            if response:
                return response
        return render(request, './templates/review/nlp/sentiment/main.html', context)


class NlpZeroView(View):

    def get(self, request):
        context = {
            "models_form": AiModelForm(),
            "models_records": NlpController.get_zero_models(),
            "apps": DataController.get_appstore_data()
        }
        if "text" in request.GET:
            context["tab"] = "text"
            context["text_zero_data"] = NlpController.get_text_zero(
                request.GET)
            context["text_text"] = request.GET.get("text_text")
            context["text_model"] = str(request.GET.get("text_model"))
            context["text_labels"] = str(request.GET.get("text_labels"))
        elif "cross" in request.GET:
            context["tab"] = "cross"
            context["cross_sentiment_data"] = NlpController.get_cross_sentiment(
                request.GET)
        return render(request, './templates/review/nlp/zeroshot/main.html', context)

    def post(self, request):
        context = {}
        if "models" in request.POST:
            context["tab"] = "models"
            context["models_form"] = AiModelForm(request.POST)
            context["models_records"] = NlpController.get_zero_models()
            created, form = NlpController.post_create_zero_model_record(
                form=AiModelForm(request.POST))
            if created == False:
                messages.error(
                    request, f"There is already a model for {form['name']}.")
            elif created == True:
                messages.success(request, "Model is saved successfully.")
                return render(request, './templates/review/nlp/translate/main.html', context)
            elif created is None:
                messages.error(request, "Invalid form submission.")
        elif "all" in request.POST:
            context["tab"] = "all"
            context["all_counts"] = NlpController.post_sentiment_all(
                request.POST)
        elif "export" in request.POST:
            context["tab"] = "export"
            response = NlpController.post_sentiment_export(request.POST)
            if response:
                return response
        return render(request, './templates/review/nlp/zeroshot/main.html', context)
