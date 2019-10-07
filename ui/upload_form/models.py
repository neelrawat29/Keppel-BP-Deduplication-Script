from django.db import models

# Create your models here.


class FileToDedupe(models.Model):
    file_xlsx = models.FileField(upload_to='%Y-%m-%d/')
    date_uploaded = models.DateTimeField(
        auto_now_add=True, db_index=True, editable=False)
    date_processed = models.DateTimeField(
        null=True, db_index=True, editable=False)
    def processed(self):
        return self.date_processed is not None
    # TODO: uploader field?
