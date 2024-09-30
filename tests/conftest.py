import pytest
import mongomock
from unittest.mock import patch, Mock
from pytest_postgresql import factories

from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import sessionmaker, scoped_session, declarative_base
from pathlib import Path

from counter.entrypoints.webapp import create_app


@pytest.fixture
def client():
    app = create_app()
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

@pytest.fixture
def image_path():
    ref_dir = Path(__file__)
    return ref_dir.parent.parent / "resources" / "images" / "boy.jpg"

@pytest.fixture
def mock_tfs_object_detector_request():
    with patch('counter.adapters.object_detector.requests.post') as mock_post:
        mock_response = Mock()
        mock_response.json.return_value = {"predictions": 
                                        [{'num_detections': 2,
                                            'detection_boxes': [[0,0,0,0], [0,0,0,0]],
                                            'detection_scores': [0.6, 0.4],
                                            'detection_classes': [1, 1]}]}
        mock_response.status_code = 200
        mock_post.return_value = mock_response
        yield mock_post

@pytest.fixture
def mongo_client_mock():
    with patch('counter.adapters.count_repo.MongoClient', new=mongomock.MongoClient) as mongo_client_mock:
        yield

Base = declarative_base()

class Counter(Base):
    __tablename__ = 'counter'
    object_class = Column(String, primary_key=True)
    count = Column(Integer)

def load_database(**kwargs):
    connection = f"postgresql+psycopg2://{kwargs['user']}:@{kwargs['host']}:{kwargs['port']}/{kwargs['dbname']}"
    engine = create_engine(connection)
    Base.metadata.create_all(engine)
    session = scoped_session(sessionmaker(bind=engine))
    session.commit()

postgresql_proc = factories.postgresql_proc(load=[load_database])

@pytest.fixture
def postgres_engine(postgresql):
    connection = f'postgresql+psycopg2://{postgresql.info.user}:@{postgresql.info.host}:{postgresql.info.port}/{postgresql.info.dbname}'
    engine = create_engine(connection)
    return engine

@pytest.fixture
def mock_create_engine(postgres_engine):
    with patch('counter.adapters.count_repo.create_engine', return_value=postgres_engine) as mock_postgres:
        yield