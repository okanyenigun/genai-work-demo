from google_play_scraper import Sort, reviews, reviews_all


class GoogleReviewStrategy:
    async def fetch_reviews(self, app_id, count):
        pass


class GoogleAllReviews(GoogleReviewStrategy):
    async def fetch_reviews(self, app_id, count=None):
        return reviews_all(app_id, sleep_milliseconds=0, lang="tr", country="tr", sort=Sort.NEWEST)


class GoogleSpecificCountReviews(GoogleReviewStrategy):
    async def fetch_reviews(self, app_id, count):
        result, _ = reviews(app_id, lang='tr', country='tr',
                            sort=Sort.NEWEST, count=count)
        return result
