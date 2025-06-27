import requests
import configparser
import json
import csv
import os
from datetime import datetime
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
output_csv = config.get('files', 'output_csv')

# Retrieve options
food_type = config.get('options', 'food_type')
output_limit = int(config.get('options', 'limit', fallback=10000))

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

analysis_query = """
query($input : GetAnalysisInput!){
    analysis{
        getAnalysis(input: $input){
            analysis{
                analysisType
                nutrientInfos{
                    nutrient{
                        id
                        name
                    }
                    value
                }
                amountAnalyzed{
                    quantity{
                        value
                    }
                    unit{
                        name
                    }
                }
                weight{
                   quantity{
                        value
                    }
                    unit{
                        name
                    }
                }
            }
        }
    }
}
"""

statements_query = """
query($input: GetFoodInput!){
    foods{
        get(input: $input){
            food{
                ... on Recipe{
                    id
                    name
                    unitedStates2016AllergenStatement {
                        englishStatements {
                            statement
                        }
                    }
                    unitedStates2016IngredientStatement {
                        englishStatement {
                            generatedStatement
                        }
                    }
                    canada2016AllergenStatement {
                        englishStatements {
                            statement
                        }
                    }
                    canada2016IngredientStatement { 
                        englishStatement {
                            generatedStatement
                        }
                    }
                }
                ... on Ingredient{
                    id
                    name
                    unitedStates2016AllergenStatement {
                        englishStatements {
                            statement
                        }
                    }
                    canada2016AllergenStatement {
                        englishStatements {
                            statement
                        }
                    }
                }
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
        logger.error(f"Endpoint: {endpoint}")
        logger.error(f"Query: {graphql_query} \r\n Variables: {variables}")
        return None


def get_analysis(graphql_query, food_id):
    nutrients = {}

    variables = {
        "input": {
            "foodId": food_id,
            "analysisInput": {
                "analysisType": "Net",
                "amount": {
                    "quantity": "100",
                    "unitId": "a7df0af5-0008-0000-7484-751e8eaf05c6"
                }
            }
        }
    }

    result = run_query(graphql_query, variables)
    if result:
        nutrients = result.get("data", {}).get("analysis", {}).get("getAnalysis", {}).get("analysis", {}).get("nutrientInfos", [])
        if len(nutrients) == 0:
            logger.warning(f"Unable to get nutrient information for {food_id}")

    return nutrients


def search(graphql_query, food_type):
    result_items = []
    variables = {
        "input": {
            "searchText": '',
            "foodTypes": [food_type],
            "itemSourceFilter": "Customer",
            "archiveFilter": "Unarchived",
            "versionFilter": "Latest",
            "first": output_limit,
            "after": 0
        }
    }

    logger.info(f"Running query...")
    result = run_query(graphql_query, variables)
    if result:
        total_count = result.get("data", {}).get("foods", {}).get("search", {}).get("totalCount", 0)
        logger.info(f"Found {total_count} results.")

    return result


def get_statements(graphql_query, food_id):
    statements = {}
    variables = {
        "input": {
            "id": food_id
        }
    }

    result = run_query(graphql_query, variables)
    if result:
        try:
            statements['allergen_statement'] = result.get("data", {}).get("foods", {}).get("get", {}).get("food", {}).get("unitedStates2016AllergenStatement", {}).get("englishStatements", []).get("statement", "")
        except:
            statements['allergen_statement'] = ""
        try:
            statements['ingredient_statement'] = result.get("data", {}).get("foods", {}).get("get", {}).get("food", {}).get("unitedStates2016IngredientStatement", {}).get("englishStatement", []).get("generatedStatement", "")
        except:
            statements['ingredient_statement'] = ""
    else:
        statements['allergen_statement'] = ""
        statements['ingredient_statement'] = ""
        logger.warning(f"Unable to get statements for {food_id}")

    return statements
        


def export_to_json(result):
    first_entry = True
    returned_items = []

    """Iterate through each character and update the searchText."""
    with open(file_path, "a") as file:

        file.write("[\n")  # Write the opening bracket for the JSON array
        if not first_entry:
            file.write(",\n")  # Add a comma before each entry - except first

        json.dump(result, file, indent=4)  # Append the JSON to the file
        first_entry = False

        file.write("\n]")  # Write the closing bracket for the JSON array


def json_to_csv(food_results, csv_file):
    """ Convert a JSON array to CSV format.
        Expectation that this will be the foodSearchResult element of the array
    """

    # Delete the file if it already exists
    if os.path.exists(csv_file):
        os.remove(csv_file)
        logger.info(f"Existing file '{csv_file}' has been deleted.")

    # Different results may have different fields; handle
    fieldnames = []
    for r in food_results:
        for key in r.keys():
            if key not in fieldnames:
                fieldnames.append(key)

    # Write JSON data to CSV
    with open(csv_file, mode='w', newline='') as file:
        # Use the keys of the first item as the header
        # fieldnames = food_results[0].keys()
        writer = csv.DictWriter(file, fieldnames=fieldnames)

        # Write header and rows
        writer.writeheader()
        writer.writerows(food_results)


# Run the playground script
if __name__ == "__main__":
    start_time = datetime.now()
    logger.info(f"Starting export process...")
    
    search_result = search(query, food_type)  # Food type from config
    if search_result is None:
        logger.error(f"No results found. Exiting.")
        exit(0)

    export_to_json(search_result)

    result_items = search_result.get("data", {}).get("foods", {}).get("search", {}).get("foodSearchResults", [])
    for f in result_items:
        nutrients = get_analysis(analysis_query, f['id'])
        # Add the nutrients to the food object
        for n in nutrients:
            f[n['nutrient']['name']] = n['value']
        statements = get_statements(statements_query, f['id'])
        # Add the statements to the food object
        if statements['allergen_statement']:    
            f['allergen_statement'] = statements['allergen_statement']
        if statements['ingredient_statement']:
            f['ingredient_statement'] = statements['ingredient_statement']

    json_to_csv(result_items, output_csv)
    
    end_time = datetime.now()
    elapsed_time = end_time - start_time
    logger.info(f"Complete. Exported results to {output_csv}")
    logger.info(f"Total elapsed time: {elapsed_time}")
