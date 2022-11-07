from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
connection_string = 'mysql://root:@127.0.0.1:3306/fast_api'
SessionLocal = sessionmaker(create_engine(connection_string))