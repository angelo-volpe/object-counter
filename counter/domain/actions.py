from PIL import Image

from counter.debug import draw
from counter.domain.models import CountResponse, PredictionsListResponse
from counter.domain.ports import ObjectDetector, ObjectCountRepo
from counter.domain.predictions import over_threshold, count


class BaseObjectDetectorAction:
    def __init__(self, object_detector: ObjectDetector):
        self.__object_detector = object_detector
    
    def _find_valid_predictions(self, image, threshold):
        predictions = self.__object_detector.predict(image)
        self.__debug_image(image, predictions, "all_predictions.jpg")
        valid_predictions = list(over_threshold(predictions, threshold=threshold))
        self.__debug_image(image, valid_predictions, f"valid_predictions_with_threshold_{threshold}.jpg")
        return valid_predictions

    @staticmethod
    def __debug_image(image, predictions, image_name):
        if __debug__ and image is not None:
            image = Image.open(image)
            draw(predictions, image, image_name)


class CountDetectedObjects(BaseObjectDetectorAction):
    def __init__(self, object_detector: ObjectDetector, object_count_repo: ObjectCountRepo):
        super().__init__(object_detector)
        self.__object_count_repo = object_count_repo

    def execute(self, image, threshold) -> CountResponse:
        predictions = self._find_valid_predictions(image, threshold)
        object_counts = count(predictions)
        self.__object_count_repo.update_values(object_counts)
        total_objects = self.__object_count_repo.read_values()
        return CountResponse(current_objects=object_counts, total_objects=total_objects)


class PredictionsListAction(BaseObjectDetectorAction):
    def __init__(self, object_detector: ObjectDetector):
        super().__init__(object_detector)

    def execute(self, image, threshold) -> PredictionsListResponse:
        predictions = self._find_valid_predictions(image, threshold)
        return PredictionsListResponse(predictions_list=predictions)
