import json
import os

# reads records from a json file, renames 'name' to 'full_name', and filters out minors (age < 18)
def transform_records(input_file, output_file):
    with open(input_file, "r", encoding="utf-8") as f:
        records = json.load(f)
        
    transformed = []
    for item in records:
        # filter: keep only adults (age >= 18)
        if item.get("age", 0) >= 18:
            transformed.append({
                "full_name": item.get("name", ""),
                "age": item.get("age"),
                "city": item.get("city", "")
            })
            
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(transformed, f, indent=2)
        
    return transformed

if __name__ == "__main__":
    input_path = "sample_records.json"
    output_path = "transformed.json"
    
    print(f"Transforming records from {input_path} -> {output_path}...")
    results = transform_records(input_path, output_path)
    
    print(f"\nTransformed {len(results)} adult records:")
    for person in results:
        print(f"- {person['full_name']} ({person['age']} yrs) from {person['city']}")
