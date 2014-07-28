from django.http.response import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.clickjacking import xframe_options_exempt

@xframe_options_exempt
@csrf_exempt
def index(request):
    return HttpResponse("Hello world!")
