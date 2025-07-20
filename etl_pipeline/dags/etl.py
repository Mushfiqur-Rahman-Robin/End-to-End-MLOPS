from airflow import DAG
from airflow.decorators import task
from airflow.providers.http.hooks.http import HttpHook
from airflow.providers.postgres.hooks.postgres import PostgresHook
from datetime import datetime, timedelta

# Define the DAG with a daily schedule and no backfilling
with DAG(
    "nasa_apod_postgres", 
    start_date=datetime.combine(datetime.today() - timedelta(days=1), datetime.min.time()),
    schedule="@daily", 
    catchup=False
) as dag:

    # Step 1: Create the Postgres table if it doesn't exist
    @task
    def create_table():
        postgres_hook = PostgresHook(postgres_conn_id="my_postgres_connection")
        create_table_query = """
            CREATE TABLE IF NOT EXISTS nasa_apod (
                id SERIAL PRIMARY KEY,
                title VARCHAR(512),
                url VARCHAR(1024),
                explanation TEXT,
                date DATE,
                media_type VARCHAR(100)
            );
        """
        postgres_hook.run(create_table_query)

    # Step 2: Extract NASA APOD data using HttpHook
    @task
    def extract_apod():
        http = HttpHook(method="GET", http_conn_id="nasa_api")
        api_key = http.get_connection("nasa_api").extra_dejson["api_key"]
        response = http.run(endpoint="planetary/apod", data={"api_key": api_key})
        return response.json()

    # Step 3: Transform the data to match table structure
    @task
    def transform_apod_data(response):
        apod_data = {
            "title": response["title"],
            "url": response["url"],
            "explanation": response["explanation"],
            "date": response["date"],
            "media_type": response["media_type"]
        }
        return apod_data

    # Step 4: Load the transformed data into Postgres
    @task
    def load_data_to_postgres(apod_data):
        postgres_hook = PostgresHook(postgres_conn_id="my_postgres_connection")
        insert_query = """
            INSERT INTO nasa_apod (title, url, explanation, date, media_type)
            VALUES (%s, %s, %s, %s, %s);
        """
        postgres_hook.run(insert_query, parameters=(
            apod_data["title"],
            apod_data["url"],
            apod_data["explanation"],
            apod_data["date"],
            apod_data["media_type"]
        ))

    # step 5: define task dependencies


    # step 6: define task dependencies
    ct = create_table()
    ea = extract_apod()
    tr = transform_apod_data(ea)
    ld = load_data_to_postgres(tr)

    ct >> ea >> tr >> ld  # ensure table is created before data is extracted
