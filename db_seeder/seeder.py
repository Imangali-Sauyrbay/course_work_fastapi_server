from pathlib import Path
from sqlalchemyseeder import ResolvingSeeder
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


def seed(models):
    session_maker = sessionmaker(create_engine('mysql://root:@127.0.0.1:3306/fast_api'))

    with session_maker() as session:
        seeder = ResolvingSeeder(session)
        seeder.register_module(models)
        new_entities = seeder.load_entities_from_json_file(Path(__file__).parent / 'seeds.json')
        session.commit()