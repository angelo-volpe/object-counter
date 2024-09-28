import os

from counter.adapters.count_repo import CountMongoDBRepo, CountInMemoryRepo
from counter.adapters.object_detector import TFSObjectDetector, FakeObjectDetector
from counter.domain.actions import CountDetectedObjects, PredictionsListAction


def dev_count_action() -> CountDetectedObjects:
    return CountDetectedObjects(FakeObjectDetector(), CountInMemoryRepo())


def prod_count_action() -> CountDetectedObjects:
    tfs_host = os.environ.get('TFS_HOST', 'localhost')
    tfs_port = os.environ.get('TFS_PORT', 8501)
    mongo_host = os.environ.get('MONGO_HOST', 'localhost')
    mongo_port = os.environ.get('MONGO_PORT', 27017)
    mongo_db = os.environ.get('MONGO_DB', 'prod_counter')
    return CountDetectedObjects(TFSObjectDetector(tfs_host, tfs_port, 'rfcn'),
                                CountMongoDBRepo(host=mongo_host, port=mongo_port, database=mongo_db))


def get_count_action() -> CountDetectedObjects:
    env = os.environ.get('ENV', 'dev')
    count_action_fn = f"{env}_count_action"
    return globals()[count_action_fn]()


def dev_predictions_list_action() -> PredictionsListAction:
    return PredictionsListAction(FakeObjectDetector(), CountInMemoryRepo())


def prod_predictions_list_action() -> PredictionsListAction:
    tfs_host = os.environ.get('TFS_HOST', 'localhost')
    tfs_port = os.environ.get('TFS_PORT', 8501)
    return PredictionsListAction(TFSObjectDetector(tfs_host, tfs_port, 'rfcn'))


def get_predictions_list_action() -> PredictionsListAction:
    env = os.environ.get('ENV', 'dev')
    predictions_list_action_fn = f"{env}_count_action"
    return globals()[predictions_list_action_fn]()