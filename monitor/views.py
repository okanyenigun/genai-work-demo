import os
import json
import base64
import pandas as pd
from django.conf import settings
from django.shortcuts import render
from django.views import View
from django.http import JsonResponse
from monitor.services.model_train.pipe import ModelGenerator
from monitor.services.chat.controller import Chatter
from django.views.decorators.csrf import csrf_exempt


def two(request):
    return render(request, './templates/monitor/main.html')


class BuildView(View):

    def get(self, request):
        return render(request, './templates/monitor/build.html')

    def post(self, request):
        print("here")
        path = os.path.join(
            settings.STATICFILES_DIRS[0], "files", "monitor", "data.csv")
        df = pd.read_csv(path)
        M = ModelGenerator(df)
        M.train()
        return render(request, './templates/monitor/build.html')


def ajax_message_handler_monitor(request):
    if request.method == 'GET':
        message = request.GET.get('message').strip()
        print("message: ", message)
        C = Chatter()
        chat_response = C.chat(message)

        return JsonResponse(chat_response)


@csrf_exempt  # Use this decorator to exempt this view from CSRF verification, or handle CSRF properly
def save_chart_image(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        image_data = data['imageData']
        filename = data['filename']

        # Remove the header of base64 string and decode
        image_data = base64.b64decode(image_data.split(',')[1])
        file_path = os.path.join(
            settings.STATICFILES_DIRS[0], "files", "monitor", filename)

        # Write the image
        with open(file_path, 'wb') as file:
            file.write(image_data)

        return JsonResponse({'status': 'success'})

    return JsonResponse({'status': 'error'}, status=400)
