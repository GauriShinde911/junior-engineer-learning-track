# demonstrates when to use tuples (immutable records) vs lists (changeable sequences)
def demonstrate_tuples():
    print("=== Tuples Practice (Immutable Records) ===")
    # A GPS coordinate should never accidentally have its latitude modified in place
    location = (37.7749, -122.4194)
    print("Location tuple (lat, lon):", location)
    print(f"Latitude: {location[0]}, Longitude: {location[1]}")
    
    # Attempting to modify a tuple raises TypeError
    try:
        location[0] = 40.7128
    except TypeError as e:
        print("Caught expected TypeError when trying to mutate tuple:", e)
    print()

# demonstrates set operations (unique collections, unions, intersections, differences)
def demonstrate_sets():
    print("=== Sets Practice (Unique Collections & Operations) ===")
    backend_skills = {"Python", "SQL", "Git", "Docker", "FastAPI"}
    data_skills = {"Python", "SQL", "Pandas", "NumPy", "Statistics"}
    
    print("Backend skills:", backend_skills)
    print("Data skills:   ", data_skills)
    
    # 1. Intersection (common skills)
    common = backend_skills & data_skills
    print("\nCommon skills (Intersection &):", common)
    
    # 2. Union (all combined unique skills)
    all_skills = backend_skills | data_skills
    print("All combined skills (Union |):", all_skills)
    
    # 3. Difference (skills only in backend)
    only_backend = backend_skills - data_skills
    print("Only Backend skills (Difference -):", only_backend)

# Rule of Thumb Comments:
# - Choose TUPLE over LIST when: data is a fixed record of values (like x,y coordinates or database rows)
#   that should never change, or when you need an immutable hashable key for a dictionary.
# - Choose SET over LIST when: you need to ensure all elements are unique (deduplication) or need
#   super-fast O(1) membership checks ('if item in my_set') and math set operations (unions/intersections).

if __name__ == "__main__":
    demonstrate_tuples()
    demonstrate_sets()
