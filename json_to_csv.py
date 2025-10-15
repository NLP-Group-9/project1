import csv
import json

def json_to_csv(json_data, csv_filename):
    """
    Convert JSON data to CSV file
    
    Args:
        json_data: List of dictionaries or JSON string
        csv_filename: Output CSV filename
    """
    # If json_data is a string, parse it
    if isinstance(json_data, str):
        json_data = json.loads(json_data)
    
    # Handle empty data
    if not json_data:
        print("No data to convert")
        return
    
    # Get headers from the first dictionary
    headers = json_data[0].keys()
    
    # Write to CSV file
    with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=headers)
        writer.writeheader()
        writer.writerows(json_data)
    
    print(f"CSV file '{csv_filename}' created successfully")


# Example usage:
data = [
    {'name': 'John Doe', 'age': 30, 'city': 'New York'},
    {'name': 'Jane Smith', 'age': 25, 'city': 'Los Angeles'},
    {'name': 'Bob Johnson', 'age': 35, 'city': 'Chicago'}
]

# Or from a JSON file:
def json_file_to_csv(json_filename, csv_filename):
    """Convert JSON file to CSV file"""
    with open(json_filename, 'r', encoding='utf-8') as jsonfile:
        data = json.load(jsonfile)
    json_to_csv(data, csv_filename)

json_file_to_csv(rf"C:\Users\haika\Desktop\NU Sem 1\CS337, NLP\project1\gg2013.json", rf'C:\Users\haika\Desktop\NU Sem 1\CS337, NLP\project1\gg_test_output.csv')