from app_store_scraper import AppStore


class AppleReviewStrategy:
    async def fetch_reviews(self, app_name, app_id, count):
        pass


class AppleReviews(AppleReviewStrategy):
    async def fetch_reviews(self, app_name, app_id, count):
        if count == -1:
            count = 100000
        apple = AppStore(country='tr', app_name=app_name, app_id=app_id)
        apple.review(how_many=count)
        return apple.reviews
