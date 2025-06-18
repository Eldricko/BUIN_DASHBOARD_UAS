from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
import pandas as pd
import os

dag_path = os.path.dirname(__file__)

# --------------------
# 1. EXTRACT
# --------------------
def extract():
    input_path = os.path.join(dag_path, 'data.csv') 
    df = pd.read_csv(input_path)

    # Konversi tanggal
    df['Order Date'] = pd.to_datetime(df['Order Date'], errors='coerce')
    df.dropna(subset=['Order Date'], inplace=True)

    df.to_csv('/tmp/extracted_data.csv', index=False)
    print(f"✅ Extract selesai: {len(df)} baris")

# --------------------
# 2. TRANSFORM
# --------------------
def transform():
    df = pd.read_csv('/tmp/extracted_data.csv')

    # Tambahkan kolom waktu
    df['Year'] = pd.to_datetime(df['Order Date']).dt.year
    df['Month'] = pd.to_datetime(df['Order Date']).dt.month

    # Bersihkan data wajib
    df.dropna(subset=['Amount', 'Profit', 'Quantity', 'City', 'Category'], inplace=True)

    df.to_csv('/tmp/transformed_data.csv', index=False)
    print(f"✅ Transform selesai: {len(df)} baris")

# --------------------
# 3. LOAD
# --------------------
def load():
    df = pd.read_csv('/tmp/transformed_data.csv')
    output_path = os.path.join(dag_path, 'buin_gabungan.csv')
    df.to_csv(output_path, index=False)
    print(f"✅ Load selesai: {output_path}")

# --------------------
# DAG DEFINITION
# --------------------
with DAG(
    dag_id='etl_example',
    start_date=datetime(2023, 1, 1),
    schedule='@daily',
    catchup=False,
    tags=['etl', 'star_schema']
) as dag:

    t1 = PythonOperator(task_id='extract', python_callable=extract)
    t2 = PythonOperator(task_id='transform', python_callable=transform)
    t3 = PythonOperator(task_id='load', python_callable=load)

    t1 >> t2 >> t3
