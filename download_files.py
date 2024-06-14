from google.cloud import storage
import os

def download_blob(blob, destination_file_name: str) -> None:
    """ Descarga el contenido del blob a un archivo en el sistema local."""
    blob.download_to_filename(destination_file_name)
    print(f"Downloaded {blob.name} to {destination_file_name}")

def list_blobs():
    """ Descarga un los names de los blobs en el bucket 2024-1-tarea-3 """
    gcloud_credentials = os.getenv('GCLOUD_CREDENTIALS')

    if gcloud_credentials:
        # Crear un archivo temporal para las credenciales
        with open('gcloud-credentials-temp.json', 'w') as temp_file:
            temp_file.write(gcloud_credentials)
    storage_client = storage.Client.from_service_account_json('./gcloud-credentials-temp.json')
    blobs = storage_client.list_blobs('2024-1-tarea-3')
    return blobs

def download_blobs():
    # Listar archivos en el bucket
    blobs = list_blobs()
    print("Archivos en el bucket:")

    # Descargar y procesar cada archivo
    for blob in blobs:
        print(blob.name)
        local_file = f"./tmp/{blob.name.replace('/', '_')}"
        download_blob(blob, local_file)

if __name__ == '__main__':
    download_blobs()