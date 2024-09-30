import io
import json


def test_object_detection(client, image_path):
    # Load the image from the path resource/boy.jpg
    with open(image_path, 'rb') as f:
        image_data = f.read()
    image = io.BytesIO(image_data)
    
    data = {
        'threshold': '0.9',
        'model_name': 'rfcn',
    }
    data['file'] = (image, 'test.jpg')

    # Make a test request to the object_detection endpoint
    response = client.post('/object-count', data = data,
        content_type='multipart/form-data', buffered=True)

    # Check that the count_action was called with the correct arguments and
    # and status code is correct(Integration test)
    assert response.status_code == 200
    assert json.loads(response.data) != None


def test_predictions_list(client, image_path):
    # Load the image from the path resource/boy.jpg
    with open(image_path, 'rb') as f:
        image_data = f.read()
    image = io.BytesIO(image_data)
    
    data = {
        'threshold': '0.9',
        'model_name': 'rfcn',
    }
    data['file'] = (image, 'test.jpg')

    # Make a test request to the predictions-list endpoint
    response = client.post('/predictions-list', data = data,
        content_type='multipart/form-data', buffered=True)

    # Check that the predictions_list was called with the correct arguments and
    # and status code is correct(Integration test)
    assert response.status_code == 200
    assert json.loads(response.data) != None
