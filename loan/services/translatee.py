import environ
import detectlanguage
from deep_translator import GoogleTranslator

env = environ.Env()
environ.Env.read_env()


class Translatee:

    def __init__(self):
        detectlanguage.configuration.api_key = env("DETECT_LANGUAGE_KEY")

    def _detect_language(self, message):
        try:
            response = detectlanguage.detect(message)
            return response[0]["language"]
        except:
            return "tr"

    def _translate_to_en(self, message):
        translated = GoogleTranslator(
            source='tr', target='en').translate(message)
        return translated

    @staticmethod
    def translate_batches(batches, source_lang='tr', target_lang='en'):
        translator = GoogleTranslator(source=source_lang, target=target_lang)
        translated_batches = [translator.translate(batch) for batch in batches]
        translated_text = ' '.join(translated_batches)
        return translated_text

    @staticmethod
    def translate_to_tr(text):
        translated = GoogleTranslator(
            source='en', target='tr').translate(text)
        return translated
