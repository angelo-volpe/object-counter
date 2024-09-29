from marshmallow import Schema, fields, validates, ValidationError
from werkzeug.datastructures import FileStorage


class ImageWithTresholdSchema(Schema):
    file = fields.Raw(required=True, type=FileStorage)
    threshold = fields.String(required=True)

    @validates('file')
    def validate_file_field(self, file: FileStorage):
        if not file:
            raise ValidationError("No image provided.")
        if not file.content_type.startswith('image/'):
            raise ValidationError("File must be an image.")
        
    @validates('threshold')
    def validate_threshold_field(slef, threshold: str):
        try:
            threshold = float(threshold)
        except ValueError:
            raise ValidationError("threshold is not a number")
        
        if not (0 <= threshold <= 1):
            raise ValidationError("threshold is out of range")
    