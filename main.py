import os
import schedule
import time
import threading
from sqlalchemy.orm import sessionmaker
from db import engine, Product, Category, Order, Customer, Seller
from data_cleaning import clean_data_products, clean_data_orders
from dashboard import update_graph
from download_files import download_blobs
from dashboard import app

# Crear una sesión de SQLAlchemy
Session = sessionmaker(bind=engine)
session = Session()

def job():
    # Eliminar archivos en tmp y download_files
    print("Eliminando archivos en tmp y download_files")
    os.system("rm -rf ./tmp/*")

    # Eliminar todas las tuplas de las tablas
    print("Eliminando tuplas de las tablas")
    session.query(Order).delete()
    session.commit()

    session.query(Product).delete()
    session.query(Category).delete()
    session.query(Customer).delete()
    session.query(Seller).delete()
    session.commit()

    # # Descargar los archivos
    print("Descargando archivos")
    download_blobs()

    print("Limpiando archivos")
    file_names = os.listdir('tmp')

    # Iterate over the file names
    for file_name in file_names:
        # Check if the file is a JSON file
        if file_name.endswith('.json'):
            # Read the JSON file
            file_path = os.path.join('tmp', file_name)

            # Clean the data
            clean_data_products(file_path)

    for file_name in file_names:
        # Check if the file is a CSV file
        if file_name.endswith('.csv'):
            # Read the CSV file
            file_path = os.path.join('tmp', file_name)
            clean_data_orders(file_path)

    # Ejecutar dashboard
    print("Actualizando dashboard")

def run_schedule():
    while True:
        schedule.run_pending()
        time.sleep(1)

# Programar el trabajo para que se ejecute cada 2 minutos
schedule.every(24).hours.do(job)

# Iniciar el hilo de `schedule`
schedule_thread = threading.Thread(target=run_schedule)
schedule_thread.start()

# Iniciar el servidor Dash
if __name__ == '__main__':
    app.run_server(debug=True)
