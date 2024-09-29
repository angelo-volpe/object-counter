from io import BytesIO

from flask import Flask, request, jsonify
from marshmallow import ValidationError

from counter import config
from counter.entrypoints.schemas import ImageWithTresholdSchema

def create_app():
    
    app = Flask(__name__)
    
    count_action = config.get_count_action()
    predictions_list_action = config.get_predictions_list_action()
    
    @app.route('/object-count', methods=['POST'])
    def object_detection():
        schema = ImageWithTresholdSchema()
        data = {
            'threshold': request.form.get('threshold', "0.5"),
            'file': request.files.get('file')
        }
        try:
            validated_data = schema.load(data)
        except ValidationError as err:
            return jsonify({"errors": err.messages}), 400
        threshold = float(validated_data['threshold'])
        uploaded_file = validated_data['file']
        image = BytesIO()
        uploaded_file.save(image)
        count_response = count_action.execute(image, threshold)
        return jsonify(count_response)
    
    @app.route('/predictions-list', methods=['POST'])
    def predictions_list():
        schema = ImageWithTresholdSchema()
        data = {
            'threshold': request.form.get('threshold', "0.5"),
            'file': request.files.get('file')
        }
        try:
            validated_data = schema.load(data)
        except ValidationError as err:
            return jsonify({"errors": err.messages}), 400
        threshold = float(validated_data['threshold'])
        uploaded_file = validated_data['file']
        image = BytesIO()
        uploaded_file.save(image)
        predictions_list_response = predictions_list_action.execute(image, threshold)
        return jsonify(predictions_list_response)
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run('0.0.0.0', debug=True)
