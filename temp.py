from app import app
from extensions import db
from models.member import Member, Role, Workshop
from models.tool import Tools
from models.workshop_details import WorkshopDetails
import pandas as pd

df = pd.read_csv('role.csv')
df = df.reset_index()
with app.app_context():
    for index, row in df.iterrows():
        name = row['name']
        description = row['description']

        entry = Role(
            name=name,
            description=description
        )
        db.session.add(entry)

    db.session.commit()
    print('Hoorey! Transfer accomplished successfully!')