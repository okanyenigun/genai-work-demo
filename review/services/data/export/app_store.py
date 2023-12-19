import os
import pandas as pd
from django.conf import settings
from review.models import AppStoreReview, AppRecord
from utility.files import FileHandler


class AppStoreExporter:

    def __init__(self, form):
        self.form = form

    def export(self):
        folder_path = os.path.join(
            settings.STATICFILES_DIRS[0], "files", "temp")
        df = pd.DataFrame(columns=["id", "app", "source", "title", "review",
                                   "rating", "user", "date", "createdate"])
        records = AppStoreReview.objects.filter(app_id=self.form["app_id"])
        app_name = AppRecord.objects.get(id=self.form["app_id"]).name
        for record in records:
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
            df.loc[len(df)-1, :] = row
        if self.form["file_format"] == "csv":
            path = os.path.join(
                folder_path, f"{app_name}_appstore_reviews.csv")
            df.to_csv(path, index=False)
        elif self.form["file_format"] == "excel":
            df['date'] = df['date'].apply(lambda a: pd.to_datetime(a).date())
            df['createdate'] = df['createdate'].apply(
                lambda a: pd.to_datetime(a).date())
            path = os.path.join(
                folder_path, f"{app_name}_appstore_reviews.xlsx")
            df.to_excel(path, index=False)
        response = FileHandler.download_static_file(path)
        return response
