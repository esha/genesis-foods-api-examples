import requests
import configparser
import json
import csv
import os
from logging_config import setup_logging

# Set up logging
logger = setup_logging()

# Read the configuration file
config = configparser.ConfigParser()
config.read('config.ini')

# Retrieve the API settings
endpoint = config.get('api', 'endpoint')
api_key = config.get('api', 'api_key')

# Retrieve the output file path from the configuration
output_file = config.get('files', 'output_file')

# Ensure the file is written to the local directory
file_path = os.path.join(os.getcwd(), output_file)

# Delete the file if it already exists
if os.path.exists(file_path):
    os.remove(file_path)
    logger.info(f"Existing file '{file_path}' has been deleted.")

# Define the headers
headers = {
    "X-API-KEY": api_key,
    "Content-Type": "application/json"
}

# Define the GraphQL query
query = """
query($input: FoodSearchInput!){
    foods{
        search(input: $input) {
            foodSearchResults{
                id
                name
                modified
                created
                versionName
                eshaCode
                foodType
                product
                supplier
                versionHistoryId
            }
            totalCount
            pageInfo{
                cursor
                hasNextPage
                startCursor
                endCursor
            }
        }
    }
}
"""


def run_query(graphql_query, variables):
    """Run a GraphQL query against the Genesis API with variables."""
    response = requests.post(
        endpoint,
        json={'query': graphql_query, 'variables': variables},
        headers=headers
    )
    if response.status_code == 200:
        return response.json()
    else:
        logger.error(f"Request failed with status code {response.status_code}")
        logger.error(response.text)
        return None


def export(graphql_query, food_type):
    first_entry = True
    """Iterate through each character in the corpus and update the searchText."""
    with open(file_path, "a") as file:

        file.write("[\n")  # Write the opening bracket for the JSON array

        variables = {
            "input": {
                "searchText": '',
                "foodTypes": [food_type],
                "itemSourceFilter": "Customer",
                "versionFilter": "All",
                "first": 10000,
                "after": 0
            }
        }

        logger.info(f"Running query...")
        result = run_query(graphql_query, variables)
        if result:
            total_count = result.get("data", {}).get("foods", {}).get("search", {}).get("totalCount", 0)
            logger.info(f"Found {total_count} results")
            if total_count > 0:
                if not first_entry:
                    file.write(",\n")  # Add a comma before each entry - except the first
                json.dump(result, file, indent=4)  # Append the JSON response to the file
                first_entry = False
            else:
                logger.info(f"No results found. Skipping write.")

        file.write("\n]")  # Write the closing bracket for the JSON array


def json_to_csv(json_file, csv_file):
    """Convert a JSON file to CSV format."""

    # Delete the file if it already exists
    if os.path.exists(csv_file):
        os.remove(csv_file)
        logger.info(f"Existing file '{csv_file}' has been deleted.")

    # Extract the nested "foodSearchResults" list from the JSON structure
    with open(json_file) as f:
        json_file = json.load(f)

    food_results = json_file[0]["data"]["foods"]["search"]["foodSearchResults"]

    # Write JSON data to CSV
    with open(csv_file, mode='w', newline='') as file:
        # Use the keys of the first item as the header
        fieldnames = food_results[0].keys()
        writer = csv.DictWriter(file, fieldnames=fieldnames)

        # Write header and rows
        writer.writeheader()
        writer.writerows(food_results)


# Run the playground script
if __name__ == "__main__":
    export(query, 'Ingredient')  # Ingredient or Recipe
    json_to_csv(file_path, file_path.replace('.json', '.csv'))
    logger.info(f"Complete. Exported results to {file_path}")
