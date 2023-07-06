from django.core.exceptions import ValidationError
import os

# Custom Raised errors for the image extension 
def allow_only_images(value):
    ext = os.path.splitext(value.name)[1]
    valid_extensions = ['.png', '.jpg', '.jpeg']
    if not ext.lower() in valid_extensions:
        raise ValidationError('Unsupported File Extension, Allowed Extensions:'+ str(valid_extensions))