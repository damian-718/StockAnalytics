from app import create_app
from app.extensions import db
from sqlalchemy import text

app = create_app()

with app.app_context():
    db.session.execute(text("""
        CREATE TABLE IF NOT EXISTS spark_job_offsets (
            job_name TEXT PRIMARY KEY,
            last_processed_ts TIMESTAMPTZ NOT NULL
        );
    """))

    db.session.execute(text("""
        INSERT INTO spark_job_offsets (job_name, last_processed_ts)
        VALUES ('process_candles', '1970-01-01')
        ON CONFLICT DO NOTHING;
    """))

    db.session.commit()
    print("Spark offset table ready")