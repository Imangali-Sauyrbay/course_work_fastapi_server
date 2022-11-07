from pathlib import Path
from sqlalchemyseeder import ResolvingSeeder
from sqlalchemy.orm import sessionmaker, Session


def seed(models, SessionLocal: sessionmaker[Session]):
    with SessionLocal() as session:
        seeder = ResolvingSeeder(session)
        seeder.register_module(models)
        new_entities = seeder.load_entities_from_json_file(Path(__file__).parent / 'seeds.json')
        session.commit()