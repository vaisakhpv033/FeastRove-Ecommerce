from django.core.exceptions import ValidationError
import os
import magic

def allow_only_images_validator(value):
    ext = os.path.splitext(value.name)[1]
    print(ext)
    valid_extensions = ['.png', '.jpg', '.jpeg']
    if ext.lower() not in valid_extensions:
        raise ValidationError("Unsupported file extension. Allowed extension: ", +str(valid_extensions))


def validate_file_mimetype(file):
    try:
        file_mime_type = magic.from_buffer(file.read(1024), mime=True)
        file.seek(0)  
    except magic.MagicException:
        print("file can't read")
        raise ValidationError("Error occurred while reading the file.")

    accept = ["image/png", "image/jpeg", "image/jpg"]
    if file_mime_type not in accept:
        print("file type is not supported")
        raise ValidationError(
            "Unsupported file type or corrupted file. Allowed types are: PNG, JPEG, JPG"
        )


def validate_file_size(file):
    max_size_mb = 2 
    max_size = max_size_mb * 1024 * 1024  # Convert MB to bytes

    if file.size > max_size:
        print("file size exceeded")
        raise ValidationError(f"File size should not exceed {max_size_mb} MB.")