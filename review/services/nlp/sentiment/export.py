import os
import pandas as pd
from django.conf import settings
from review.models import TranslatedReviews, AiModels, AppRecord, AppStoreReview, SentimentReview
from utility.files import FileHandler


class SentimentExport:

    def __init__(self):
        self.df = pd.DataFrame(columns=["id", "app", "source", "title", "review",
                                        "rating", "user", "date", "createdate"])

    def export(self, data_source, model_id, app_id, file_format):
        app_name = AppRecord.objects.get(id=app_id).name
        modelname = AiModels.objects.get(id=model_id).name
        if data_source == "app_store":
            sentiment_records = SentimentReview.objects.filter(
                ai_model_id=model_id)
            color_values = []
            label_values = []
            score_values = []
            translated_values = []
            for sentiment_record in sentiment_records:
                record = AppStoreReview.objects.get(
                    id=sentiment_record.review_id)

                row = [record.id,
                       app_name,
                       record.source,
                       record.title,
                       record.review,
                       record.rating,
                       record.username,
                       record.date,
                       record.createdate,
                       ]
                if sentiment_record.translated_review_id:
                    translated_values.append(TranslatedReviews.objects.get(
                        id=sentiment_record.translated_review_id).translated_text)
                else:
                    translated_values.append("")
                color_values.append(sentiment_record.sentiment_color)
                label_values.append(sentiment_record.label)
                score_values.append(sentiment_record.score)
                self.df.loc[len(self.df)-1, :] = row
            self.df[f"{modelname}_color"] = color_values
            self.df[f"{modelname}_label"] = label_values
            self.df[f"{modelname}_score"] = score_values
            self.df[f"translation"] = translated_values
            folder_path = os.path.join(
                settings.STATICFILES_DIRS[0], "files", "temp")
            if file_format == "csv":
                path = os.path.join(
                    folder_path, f"{app_name}_appstore_reviews.csv")
                self.df.to_csv(path, index=False)
            elif file_format == "excel":
                self.df['date'] = self.df['date'].apply(
                    lambda a: pd.to_datetime(a).date())
                self.df['createdate'] = self.df['createdate'].apply(
                    lambda a: pd.to_datetime(a).date())
                path = os.path.join(
                    folder_path, f"{app_name}_appstore_reviews.xlsx")
                self.df.to_excel(path, index=False)
            response = FileHandler.download_static_file(path)
            return response
