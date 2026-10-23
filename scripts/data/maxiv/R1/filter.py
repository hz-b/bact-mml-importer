import json

# Load the original file
with open("ao_R1_with_lattice_index.json", "r") as f:
    data = json.load(f)

# Allowed family types
keep_families = {"SQFI", "HCM", "VCM"}

# Filter the dictionary
filtered = {
    name: info
    for name, info in data.items()
    if info.get("FamilyName") in keep_families
}

# Save the filtered result
with open("ao_R1_filtered.json", "w") as f:
    json.dump(filtered, f, indent=2)

print("Filtered file written to ao_R1_filtered.json")
