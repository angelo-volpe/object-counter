import os

from counter.adapters.count_repo import CountMongoDBRepo, CountInMemoryRepo, CountPostgreSQLRepo
from counter.adapters.object_detector import TFSObjectDetector, FakeObjectDetector
from counter.domain.actions import CountDetectedObjects, PredictionsListAction
from counter.domain.ports import ObjectDetector, ObjectCountRepo


def get_mongodb_repo() -> ObjectCountRepo:
    mongo_host = os.environ.get('MONGO_HOST', 'localhost')
    mongo_port = os.environ.get('MONGO_PORT', 27017)
    mongo_db = os.environ.get('MONGO_DB', 'prod_counter')
    return CountMongoDBRepo(mongo_host, mongo_port, mongo_db)


def get_postgres_repo() -> ObjectCountRepo:
    pg_host = os.environ.get('POSTGRES_HOST', 'localhost')
    pg_port = os.environ.get('POSTGRES_PORT', '5432')
    pg_database = os.environ.get('POSTGRES_DATABASE', 'prod_counter')
    pg_user = os.environ.get('POSTGRES_USER', 'counter_user')
    pg_password = os.environ.get('POSTGRES_PASSWORD', 'counter_password')
    return CountPostgreSQLRepo(host=pg_host, port=pg_port, database=pg_database, user=pg_user, password=pg_password)


def get_tfs_object_detector() -> ObjectDetector:
    tfs_host = os.environ.get('TFS_HOST', 'localhost')
    tfs_port = os.environ.get('TFS_PORT', 8501)
    return TFSObjectDetector(tfs_host, tfs_port, 'rfcn')


def get_in_memory_repo() -> ObjectCountRepo:
    return CountInMemoryRepo()


def get_fake_detector() -> ObjectDetector:
    return FakeObjectDetector()


def dev_count_action() -> CountDetectedObjects:
    return CountDetectedObjects(get_fake_detector(), get_in_memory_repo())


def dev_postgres_count_action() -> CountDetectedObjects:
    return CountDetectedObjects(get_fake_detector(), get_postgres_repo())


def prod_count_action() -> CountDetectedObjects:
    return CountDetectedObjects(get_tfs_object_detector(), get_mongodb_repo())


def get_count_action() -> CountDetectedObjects:
    env = os.environ.get('ENV', 'dev')
    count_action_fn = f"{env}_count_action"
    return globals()[count_action_fn]()


def dev_predictions_list_action() -> PredictionsListAction:
    return PredictionsListAction(get_fake_detector())


def dev_postgres_predictions_list_action() -> PredictionsListAction:
    return PredictionsListAction(get_fake_detector())


def prod_predictions_list_action() -> PredictionsListAction:
    return PredictionsListAction(get_tfs_object_detector())


def get_predictions_list_action() -> PredictionsListAction:
    env = os.environ.get('ENV', 'dev')
    count_action_fn = f"{env}_predictions_list_action"
    return globals()[count_action_fn]()