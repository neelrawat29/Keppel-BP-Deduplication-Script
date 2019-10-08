from django.db import models
from django.urls import reverse

# Create your models here.


class FileToDedupe(models.Model):
    file_xlsx = models.FileField(upload_to='%Y-%m-%d/')
    date_uploaded = models.DateTimeField(
        auto_now_add=True, db_index=True, editable=False)
    date_processed = models.DateTimeField(
        null=True, db_index=True, editable=False)

    def processed(self):
        return self.date_processed is not None

    def get_absolute_url(self):
        return reverse('detail', kwargs={'pk': self.pk})

    class Meta:
        verbose_name_plural='files to deduplicate'

    # TODO: uploader field
