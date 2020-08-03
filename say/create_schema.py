from say.config import config
from say.orm import create_engine, setup_schema


def create_schema():
    engine = create_engine(config['dbUrl'])
    setup_schema(engine)
