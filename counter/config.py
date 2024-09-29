import os

from counter.adapters.count_repo import CountMongoDBRepo, CountInMemoryRepo, CountPostgreSQLRepo
from counter.adapters.object_detector import TFSObjectDetector, FakeObjectDetector
from counter.domain.actions import CountDetectedObjects, PredictionsListAction


def init_tfs():
    tfs_host = os.environ.get('TFS_HOST', 'localhost')
    tfs_port = os.environ.get('TFS_PORT', 8501)
    return tfs_host, tfs_port


def get_mongodb_repo():
    mongo_host = os.environ.get('MONGO_HOST', 'localhost')
    mongo_port = os.environ.get('MONGO_PORT', 27017)
    mongo_db = os.environ.get('MONGO_DB', 'prod_counter')
    return CountMongoDBRepo(mongo_host, mongo_port, mongo_db)


def get_postgres_repo():
    pg_host = os.environ.get('POSTGRES_HOST', 'localhost')
    pg_port = os.environ.get('POSTGRES_PORT', '5432')
    pg_database = os.environ.get('POSTGRES_DATABASE', 'prod_counter')
    pg_user = os.environ.get('POSTGRES_USER', 'counter_user')
    pg_password = os.environ.get('POSTGRES_PASSWORD', 'counter_password')
    return CountPostgreSQLRepo(host=pg_host, port=pg_port, database=pg_database, user=pg_user, password=pg_password)


def get_in_memory_repo():
    return CountInMemoryRepo()


def get_repo():
    repo = os.environ.get('REPO', 'in_memory')
    get_repo_fn = f"get_{repo}_repo"
    return globals()[get_repo_fn]()


def dev_count_action() -> CountDetectedObjects:
    return CountDetectedObjects(FakeObjectDetector(), get_repo())


def prod_count_action() -> CountDetectedObjects:
    tfs_host, tfs_port = init_tfs()
    return CountDetectedObjects(TFSObjectDetector(tfs_host, tfs_port, 'rfcn'), get_repo())


def get_count_action() -> CountDetectedObjects:
    env = os.environ.get('ENV', 'dev')
    count_action_fn = f"{env}_count_action"
    return globals()[count_action_fn]()


def dev_predictions_list_action() -> PredictionsListAction:
    return PredictionsListAction(FakeObjectDetector())


def prod_predictions_list_action() -> PredictionsListAction:
    tfs_host, tfs_port = init_tfs()
    return PredictionsListAction(TFSObjectDetector(tfs_host, tfs_port, 'rfcn'))


def get_predictions_list_action() -> PredictionsListAction:
    env = os.environ.get('ENV', 'dev')
    predictions_list_action_fn = f"{env}_predictions_list_action"
    return globals()[predictions_list_action_fn]()