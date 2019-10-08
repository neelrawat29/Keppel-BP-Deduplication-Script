from django.shortcuts import render, get_object_or_404
from django.views import generic
import os
from django.conf import settings

from django.http import HttpResponse, FileResponse

from .models import UploadedFile


def index(request):
    return HttpResponse("Hello World!")

# Create your views here.


class UploadFile(generic.CreateView):
    model = UploadedFile
    fields = ['file_xlsx']
    template_name = 'upload_form/upload_form.html'

class FileDetails(generic.DetailView):
    model = UploadedFile
    context_object_name = 'file'
    template_name = 'upload_form/detail.html'

def download(request, pk):
    file = get_object_or_404(UploadedFile, pk=pk)
    print(settings.MEDIA_ROOT)
    file_path = os.path.join(settings.MEDIA_ROOT, file.file_xlsx.name)
    file = open(file_path, 'rb')
    response = FileResponse(file, as_attachment=True)
    return response