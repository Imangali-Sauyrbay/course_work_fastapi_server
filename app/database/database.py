from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
connection_string = 'mysql://y9khjfekb1l1eroi:bdiqg8urn4a7bjaz@ltnya0pnki2ck9w8.chr7pe7iynqr.eu-west-1.rds.amazonaws.com:3306/uhce0hs96jdhq466'
SessionLocal = sessionmaker(create_engine(connection_string))