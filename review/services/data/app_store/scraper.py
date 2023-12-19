import asyncio
from review.services.data.app_store.apple_store import AppleReviews
from review.services.data.app_store.google_store import GoogleAllReviews, GoogleSpecificCountReviews


class ScraperFactory:
    def get_scraper(self, source, count=-1):
        if source == 'google':
            return GoogleAllReviews() if count == -1 else GoogleSpecificCountReviews()
        elif source == 'apple':
            return AppleReviews()
        else:
            raise ValueError("Unsupported source")


class AppReviewFetcher:
    def __init__(self, form):
        self.form = form
        self.scraper = ScraperFactory().get_scraper(
            form["store_type"], form["count"])

    async def fetch_reviews(self):
        if self.form["store_type"] == 'google':
            return await self.scraper.fetch_reviews(self.form["google_id"], self.form["count"])
        elif self.form["store_type"] == 'apple':
            return await self.scraper.fetch_reviews(self.form["apple_name"], self.form["apple_id"], self.form["count"])


class AppStoreReviewCollector:
    def __init__(self, form_list):
        self.form_list = form_list
        self.reviews = None

    async def collect_reviews(self):
        tasks = []
        for form in self.form_list:

            fetcher = AppReviewFetcher(form)
            task = asyncio.create_task(
                self._fetch_and_process_reviews(fetcher, form["app_record"], form["store_type"]))
            tasks.append(task)

        await asyncio.gather(*tasks)

    def get_reviews(self):
        return self.reviews

    async def _fetch_and_process_reviews(self, fetcher, app_record, source):
        fetched_reviews = await fetcher.fetch_reviews()
        processed_reviews = self._process_reviews(
            fetched_reviews, source, app_record)
        self.reviews = processed_reviews

    def _process_reviews(self, reviews, source, app_record):
        processed_reviews = []
        for review in reviews:
            if source == 'google':
                processed_review = {
                    "source": source,
                    "app": app_record,
                    "title": "",
                    "review": review.get('content'),
                    "rating": review.get('score'),
                    "username": review.get('userName'),
                    "date": review.get('at')
                }
            elif source == 'apple':
                processed_review = {
                    "source": source,
                    "app": app_record,
                    "title": review.get('title'),
                    "review": review.get('review'),
                    "rating": review.get('rating'),
                    "username": review.get('userName'),
                    "date": review.get('date')
                }
            processed_reviews.append(processed_review)
        return processed_reviews
