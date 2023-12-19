from datetime import datetime
from django.shortcuts import render
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from loan.controller import Controller


class MainView(View):

    def get(self, request):
        context = {"time": datetime.now()}
        if "calculate" in request.GET:
            C = Controller()
            context["loan_amount"] = int(request.GET.get("loan_amount"))
            context["loan_term"] = int(request.GET.get("loan_term"))
            context["bank_response"] = C.collect_bank_responses(
                context["loan_amount"], context["loan_term"])["dicto"]

        return render(request, './templates/loan/main.html', context)


@csrf_exempt
def ajax_message_handler(request):
    if request.method == 'POST':
        message = request.POST.get('message').strip()
        selected_model = request.POST.get('selected_model').strip()
        print("message: ", message)
        print("selected_model: ", selected_model)
        C = Controller()
        chat_response = C.chat(message, selected_model)
        print()
        print("response: ")
        print()
        print(chat_response)
        return JsonResponse(chat_response)


def loading_view(request):
    return render(request, './templates/loan/loading.html')
