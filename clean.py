import os
from data_cleaning import clean_data_products, clean_data_orders
import pandas as pd

def main():
    # Get the list of file names in the tmp folder
    file_names = os.listdir('tmp')

    # Iterate over the file names
    # for file_name in file_names:
    #     # Check if the file is a JSON file
    #     if file_name.endswith('.json'):
    #         # Read the JSON file
    #         file_path = os.path.join('tmp', file_name)

    #         # Clean the data
    #         clean_data_products(file_path)

    for file_name in file_names:
        # Check if the file is a CSV file
        if file_name.endswith('.csv'):
            # Read the CSV file
            file_path = os.path.join('tmp', file_name)
            clean_data_orders(file_path)
            


if __name__ == "__main__":
    main()
