from app import Jobs, db
from app import app
with app.app_context():
    jobs_to_delete = Jobs.query.filter((Jobs.status == 'Waiting in a queue') | 
                                    (Jobs.status == 'Running') |
                                    (Jobs.status == 'Finished') |
                                    (Jobs.status == 'Preprocessing')).all()

    for record in jobs_to_delete:
        db.session.delete(record)

    db.session.commit()
