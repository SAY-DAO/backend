from sqlalchemy import create_engine



db_string = 'postgresql://postgres:root@localhost:5432/say'
db = create_engine(db_string)