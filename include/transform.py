import polars as pl
import os
from dotenv import load_dotenv

load_dotenv()

storage_options = {
    'account_name': 'urbancitystorage',
    'account_key': os.getenv('ACCOUNT_KEY')
}

def transform():
    source_uri = 'az://bronze/311_urban_service_requests.csv'
    target_uri = 'az://silver/311_urban_service_requests.parquet'

    df = pl.scan_csv(source_uri, storage_options=storage_options)

    column_mapping = {
        "Created Date": "created_date",
        "Closed Date": "closed_date",
        "Problem (formerly Complaint Type)": "problem",
        "Problem Detail (formerly Descriptor)": "problem_detail",
        "Location Type": "location_type",
        "Incident Address": "incident_address",
        "City": "city",
        "Borough": "borough",
        "Latitude": "latitude",
        "Longitude": "longitude"
    }

    df_refined = df.select(
        [pl.col(old).alias(new) for old, new in column_mapping.items()]
    )

    df_refined.sink_parquet(
        target_uri,
        storage_options=storage_options,
        compression="snappy"
    )

    print(f"data loaded to {target_uri}")

    return None
