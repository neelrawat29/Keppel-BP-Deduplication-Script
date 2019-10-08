from django.shortcuts import render
from django.views import generic

from django.http import HttpResponse

from .models import FileToDedupe


def index(request):
    return HttpResponse("Hello World!")

# Create your views here.


class UploadFile(generic.CreateView):
    model = FileToDedupe
    fields = ['file_xlsx']
    template_name = 'upload_form/upload_form.html'

class FileDetails(generic.DetailView):
    model = FileToDedupe
    context_object_name = 'file'
    template_name = 'upload_form/detail.html'