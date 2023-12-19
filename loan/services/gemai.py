import ast
import json
import environ
import google.generativeai as genai

env = environ.Env()
environ.Env.read_env()


class GeminiApi:

    def __init__(self):
        genai.configure(api_key=env("GEMINI_KEY"))

    def decide_intention(self, message, message_en):
        prompt = """
        My app, a loan finder, allows users to request loan proposals, inquire about loan details, proceed with selected loans, or make general inquiries. Users can specify loan amounts and terms to receive proposals from various banks. They can also query these proposals for specific details like minimum interest rates. The app facilitates proceeding with a chosen loan by redirecting users to the bank's website. Additionally, it handles general inquiries related to frequently asked questions. The messages from user will be in Turkish.
        You will understand the intent of the text sent by the customer. The possible intents are: ["Request Loan Proposals", "Inquire Loan Details", "Proceed With Loan","General Inquiry"]". Return your response in a JSON format. For example: response: {'intent': 'Proceed With Loan'}.
        """

        query = f"{prompt} the message from the user is: {message}"

        model = genai.GenerativeModel('gemini-pro')

        response = model.generate_content(query)
        return ast.literal_eval(response.text)["intent"]

    def ner_loan_values(self, message, message_er):
        prompt = """
        apply Named Entity Recognition to given text. In our case, predefined categories are the loan amount and loan term.
        return your response in JSON format.
        For example; for a given text like: 100000 lira için 24 ay geri ödemeli kredi teklifleri istiyorum.
        your return should be like:
        {'loan_amount': 100000,
        'loan_term': 24}
        """
        query = f"{prompt} the message from the user is: {message}"

        model = genai.GenerativeModel('gemini-pro')

        response = model.generate_content(query)
        string = response.text.replace("`", "").strip()
        print("string ner: ", string)
        try:
            js = ast.literal_eval(string)
        except:
            js = json.loads(string)
        return js["loan_amount"], js["loan_term"]

    def data_question_asking(self, message, message_en, data):
        prompt = """
        You are replying customers in a loan finder app in Turkish. Users asks for loan proposals from various banks,
        and our system collects responses from each provider and combines them into a JSON format. What you will do is that
        you will take this JSON data and the query that the users asks and you will find the right answer from the JSON and 
        also generate a promoting text (in TURKISH) and return them in a JSON format. An example of return JSON: {
            "answer": "Halkbank",
            "promoting_text": "Halkbank, en düşük faiz oranı ile sizin için en uygun seçenek olabilir. Halkbank'ın sunduğu bu avantajlı oranı kaçırmayın!"
        }
        """
        query = f"{prompt}. The Response from banks: {data['json']}. And the question is: {message}"
        model = genai.GenerativeModel('gemini-pro')

        response = model.generate_content(query)
        string = response.text.replace("`", "").strip()
        print("string: ", string)
        try:
            js = ast.literal_eval(string)
        except:
            js = json.loads(string)
        print("js: ", js)
        return js

    def ask_to_document(self, message, message_en, text):
        prompt = f"""
        find the appropriate answer based on this text.  return your response in a JSON format, using only one key: 'answer'. Even if you cannot find information about the query inside the text, state that in the JSON format as your answer.
        The text: {text}
        """
        query = f"{prompt}. The question about the text is: {message}"
        model = genai.GenerativeModel('gemini-pro')

        response = model.generate_content(query)
        string = response.text.replace("`", "").strip()
        print("string: ", string)
        try:
            js = ast.literal_eval(string)
        except:
            js = json.loads(string)
        print("js: ", js)
        return js
