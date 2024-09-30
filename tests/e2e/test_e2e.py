import io
import json

import pytest
from unittest.mock import patch

from counter.entrypoints.webapp import create_app


class TestE2E:

    @pytest.fixture
    def client_e2e(self, monkeypatch, mongo_client_mock):
        monkeypatch.setenv('ENV', 'prod')
        app = create_app()
        app.config['TESTING'] = True
        with app.test_client() as client:
            yield client
    
    def test_object_detection_e2e(self, client_e2e, image_path, mock_tfs_object_detector_request) -> None:
        # Load the image from the path resource/boy.jpg
        with open(image_path, 'rb') as f:
            image_data = f.read()
        image = io.BytesIO(image_data)
        
        data = {'threshold': '0.5'}
        data['file'] = (image, 'test.jpg')
        
        # Make a test request to the object_detection endpoint
        res = client_e2e.post('/object-count', data=data,
            content_type='multipart/form-data', buffered=True)

        assert res.status_code == 200
        mock_tfs_object_detector_request.assert_called_once()
        assert json.loads(res.data) == {'current_objects': [{'count': 1, 'object_class': 'person'}], 
                                        'total_objects': [{'count': 1, 'object_class': 'person'}]}

    def test_predictions_list_e2e(self, client_e2e, image_path, mock_tfs_object_detector_request) -> None:
        # Load the image from the path resource/boy.jpg
        with open(image_path, 'rb') as f:
            image_data = f.read()
        image = io.BytesIO(image_data)
        
        data = {'threshold': '0.5'}
        data['file'] = (image, 'test.jpg')

        # Make a test request to the predictions-list endpoint
        response = client_e2e.post('/predictions-list', data=data,
            content_type='multipart/form-data', buffered=True)
        
        assert response.status_code == 200
        mock_tfs_object_detector_request.assert_called_once()
        assert json.loads(response.data) == {'predictions_list': 
                                             [{'box': {'xmax': 0, 'xmin': 0, 'ymax': 0, 'ymin': 0},
                                               'class_name': 'person',
                                               'score': 0.6}]}