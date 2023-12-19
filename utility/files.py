import os
import mimetypes
from wsgiref.util import FileWrapper
from django.core.files.storage import FileSystemStorage
from django.http import HttpResponse


class FileHandler:

    @staticmethod
    def save_file_into_directory(path, file):
        """save any file in the static folders"""
        fs = FileSystemStorage(location=path)
        filename = fs.save(file.name, file)
        path += "\\"+filename
        return path

    @staticmethod
    def download_static_file(path):
        wrapper = FileWrapper(open(path, 'rb'))
        file_mimetype = mimetypes.guess_type(path)
        response = HttpResponse(wrapper, content_type=file_mimetype)
        response['X-Sendfile'] = path
        response['Content-Length'] = os.stat(path).st_size
        response['Content-Disposition'] = 'attachment; filename=' + \
            os.path.basename(path)
        return response
