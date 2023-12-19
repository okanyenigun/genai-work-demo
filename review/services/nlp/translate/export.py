import os
import pandas as pd
from django.conf import settings
from review.models import TranslatedReviews, AiModels, AppRecord, AppStoreReview
from utility.files import FileHandler


class TranslationExport:

    def __init__(self):
        self.df = pd.DataFrame(columns=["id", "app", "source", "title", "review",
                                        "rating", "user", "date", "createdate"])

    def export(self, data_source, model_id, app_id, file_format):
        app_name = AppRecord.objects.get(id=app_id).name
        modelname = AiModels.objects.get(id=model_id).name
        if data_source == "app_store":
            translation_records = TranslatedReviews.objects.filter(
                ai_model_id=model_id)
            values = []
            for translated_record in translation_records:
                record = AppStoreReview.objects.get(
                    id=translated_record.review)

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
                values.append(translated_record.translated_text)
                self.df.loc[len(self.df)-1, :] = row
            self.df[modelname] = values
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
