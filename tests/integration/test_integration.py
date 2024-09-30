import io

from counter.domain.actions import CountDetectedObjects, PredictionsListAction
from counter.adapters.object_detector import TFSObjectDetector, FakeObjectDetector
from counter.domain.models import ObjectCount, Box, Prediction, CountResponse
from counter.adapters.count_repo import CountInMemoryRepo, CountMongoDBRepo, CountPostgreSQLRepo

class TestIntegrations:

    def test_count_detected_objects_action_with_tfs_model(self, image_path, mock_tfs_object_detector_request) -> None:
        with open(image_path, 'rb') as f:
            image_data = f.read()
        image = io.BytesIO(image_data)
        object_detector = TFSObjectDetector(host='test', port=1111, model='test')
        count_repo = CountInMemoryRepo()
        response = CountDetectedObjects(object_detector, count_repo).execute(image, 0.5)
        mock_tfs_object_detector_request.assert_called_once()
        assert sorted(response.current_objects, key=lambda x: x.object_class) == [ObjectCount('person', 1)]

    def test_count_detected_objects_action_with_mongodb(self, mongo_client_mock) -> None:
        object_detector = FakeObjectDetector()
        count_repo = CountMongoDBRepo('test', 1111, 'counter')
        response = CountDetectedObjects(object_detector, count_repo).execute(None, 0.5)
        assert response == CountResponse(current_objects=[ObjectCount('cat', 1)], total_objects=[ObjectCount('cat', 1)])
        
        response = CountDetectedObjects(object_detector, count_repo).execute(None, 0.5)
        assert response == CountResponse(current_objects=[ObjectCount('cat', 1)], total_objects=[ObjectCount('cat', 2)])
    
    def test_count_detected_objects_action_with_postgres(self, mock_create_engine) -> None:
        object_detector = FakeObjectDetector()
        count_repo = CountPostgreSQLRepo("test", 1111, 'test_db', 'test_user', 'test_password')
        response = CountDetectedObjects(object_detector, count_repo).execute(None, 0.5)
        assert response == CountResponse(current_objects=[ObjectCount('cat', 1)], total_objects=[ObjectCount('cat', 1)])
        
        response = CountDetectedObjects(object_detector, count_repo).execute(None, 0.5)
        assert response == CountResponse(current_objects=[ObjectCount('cat', 1)], total_objects=[ObjectCount('cat', 2)])

    def test_predictions_list_action_with_tfs_object_detector(self, image_path, mock_tfs_object_detector_request) -> None:
        with open(image_path, 'rb') as f:
            image_data = f.read()
        image = io.BytesIO(image_data)
        object_detector = TFSObjectDetector(host='test', port=1111, model='test')
        response = PredictionsListAction(object_detector).execute(image, 0.5)
        mock_tfs_object_detector_request.assert_called_once()
        assert response.predictions_list == [Prediction('person', score=0.6, box=Box(0, 0, 0, 0))]