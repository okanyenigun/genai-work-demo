from asgiref.sync import sync_to_async
from django.db.models import Count, Max
from review.models import AppRecord, AppStoreReview
from review.services.data.app_store.scraper import AppStoreReviewCollector
from review.services.data.export.app_store import AppStoreExporter


class DataController:

    @staticmethod
    def get_apprecord_records():
        records = AppRecord.objects.all()
        return records

    @staticmethod
    def post_create_app_record(form):
        record, created = AppRecord.objects.get_or_create(
            name=form["name"],
            defaults={
                'google_id': form['google_id'],
                'apple_name': form["apple_name"],
                'apple_id': form["apple_id"]
            }
        )
        return record, created

    @staticmethod
    def get_appstore_data():
        app_records = AppRecord.objects.values('id', 'name')
        return app_records

    @staticmethod
    def get_review_summary():
        summary = AppStoreReview.objects.values('app') \
                                        .annotate(total_reviews=Count('id'),
                                                  last_createdate=Max('createdate')) \
                                        .order_by('app')

        # Convert QuerySet to a list of dictionaries
        summary_list = list(summary)
        for s in summary_list:
            s["name"] = AppRecord.objects.get(id=s["app"]).name
        return summary_list

    @staticmethod
    async def post_pull_app_store_reviews(post):
        # parse form
        form = {
            "app_id": int(post.get("app_id")),
            "store_type": post.get("store_type"),
            "count": -1 if post.get("count") == "" else int(post.get("count"))
        }
        get_app_record = sync_to_async(AppRecord.objects.get)
        app_record = await get_app_record(id=form["app_id"])
        form["google_id"] = app_record.google_id
        form["apple_name"] = app_record.apple_name
        form["apple_id"] = app_record.apple_id
        form["app_record"] = app_record
        # collect reviews
        A = AppStoreReviewCollector([form])
        await A.collect_reviews()
        reviews = A.get_reviews()
        # insert reviews
        counts = {"ok": 0, "x": 0}
        for review in reviews:
            _, created = await sync_to_async(AppStoreReview.objects.get_or_create)(
                review=review["review"], date=review["date"],
                defaults={
                    'app': review['app'],
                    'source': review["source"],
                    'title': review["title"],
                    'username': review["username"],
                    'rating': review["rating"]
                }
            )
            if created:
                counts["ok"] += 1
            else:
                counts["x"] += 1

        return counts

    @staticmethod
    def post_export_file(post):
        form = {
            "app_id": int(post.get("app_id")),
            "data_source": post.get("app_id"),
            "file_format": post.get("file_format")
        }
        if post.get("data_source") == "app_store":
            E = AppStoreExporter(form)
        response = E.export()

        return response
