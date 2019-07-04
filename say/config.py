from sqlalchemy import create_engine



db_string = 'postgresql://say:pendara@localhost:5432/say'
db = create_engine(db_string)