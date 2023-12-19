from django.db import models


class AppRecord(models.Model):
    name = models.CharField(max_length=250, blank=False, null=False)
    google_id = models.CharField(max_length=250, blank=True, null=True)
    apple_name = models.CharField(max_length=250, blank=True, null=True)
    apple_id = models.CharField(max_length=250, blank=True, null=True)
    createdate = models.DateTimeField(auto_now_add=True, blank=True)


class AppStoreReview(models.Model):
    app = models.ForeignKey(AppRecord, on_delete=models.PROTECT)
    source = models.CharField(max_length=50, blank=False, null=False)
    title = models.CharField(max_length=250, blank=True, null=True)
    review = models.TextField()
    username = models.CharField(max_length=250)
    rating = models.IntegerField()
    date = models.DateField()
    createdate = models.DateTimeField(auto_now_add=True, blank=True)


class AiModels(models.Model):
    SOURCE_CHOICES = (
        ('huggingface', 'Hugging Face'),
        ('library', 'Library')
    )
    LANGUAGE_CHOICES = (
        ('all', 'All'),
        ('tr', 'Turkish'),
        ('en', 'English')
    )

    name = models.CharField(max_length=300, blank=False, null=False)
    source = models.CharField(
        max_length=250, blank=False, null=False, choices=SOURCE_CHOICES)
    use_case = models.CharField(max_length=250, blank=False, null=False)
    language_support = models.CharField(
        max_length=250, blank=True, null=True, default="all", choices=LANGUAGE_CHOICES)
    createdate = models.DateTimeField(auto_now_add=True, blank=True)


class TranslatedReviews(models.Model):
    translated_text = models.TextField()
    review = models.IntegerField()
    ai_model = models.ForeignKey(AiModels, on_delete=models.PROTECT)
    createdate = models.DateTimeField(auto_now_add=True, blank=True)


class SentimentReview(models.Model):
    sentiment_color = models.CharField(max_length=20, null=False, blank=False)
    label = models.CharField(max_length=50, null=False, blank=False)
    score = models.FloatField(null=False, blank=False)
    review = models.IntegerField()
    translated_review = models.IntegerField(default=-1)
    ai_model = models.ForeignKey(AiModels, on_delete=models.PROTECT)
    createdate = models.DateTimeField(auto_now_add=True, blank=True)
