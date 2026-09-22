from pathlib import Path
from datetime import datetime
import json
import shutil

# CG ASSET PIPELINE AUTOMATION TOOL
BASE_DIR = Path("assets")

DEPARTMENTS = [
        "model",
        "texture",
        "rig",
        "animation",
        "render"
]

# UTILITY FUNCTIONS
def get_asset_path(asset_name):
    """Return path"""
    return BASE_DIR / asset_name

def get_metadata_path(asset_name): 
    """Return the metadata JSON path"""
    return get_asset_path(asset_name) / "metadata.json"

def load_metadata(asset_name):
    """Load asset metadata from JSON."""
    metadata_path = get_metadata_path(asset_name)


    if not metadata_path.exists():
        return {
            "asset_name": asset_name,
            "created": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "versions": []
        }


    try:
        with open(metadata_path, "r", encoding="utf-8") as file:
            return json.load(file)

    except json.JSONDecodeError:
        print("Warning: Metadata file is corrupted.")
        return {
            "asset_name": asset_name,
            "created": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "versions": []
        }

def save_metadata(asset_name, metadata):
    """Save asset metadata to JSON."""

    metadata_path = get_metadata_path(asset_name)

    with open(metadata_path, "w", encoding="utf-8") as file:
        json.dump(metadata, file, indent=4)

#CREATE ASSET


def create_asset(asset_name):
    """Create the standard CG asset folder structure."""

    asset_name = asset_name.strip()


    if not asset_name:
        print("\nAsset name cannot be empty.")
        return
    
# Prevent invalid path characters    
    invalid_characters = '<>:"/\\|?*'

    
    if any(char in asset_name for char in invalid_characters):
        print("\nInvalid asset name.")
        print("Please avoid characters such as: < > : \" / \\ | ? *")
        return


    asset_path = get_asset_path(asset_name)
 
    if asset_path.exists():
        print(f"\nAsset '{asset_name}' already exists.")
        return


# Create department folders    
    for department in DEPARTMENTS:
          
        work_folder = asset_path / department / "work"
        final_folder = asset_path / department / "final"
        publish_folder = asset_path / department / "publish"


        work_folder.mkdir(parents=True, exist_ok=True)
        final_folder.mkdir(parents=True, exist_ok=True)
        publish_folder.mkdir(parents=True, exist_ok=True)


# Create metadata    
    metadata = {
        "asset_name": asset_name,
        "created": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "versions": []
    }


    save_metadata(asset_name, metadata)
    print("\n")
    print("Asset created successfully!")
    print("-------------------------")
    print(f"Asset:    {asset_name}")
    print(f"Location: {asset_path}")
    print("\n")




# VALIDATE ASSET
def validate_asset(asset_name):
    """Check whether the asset has the required folder structure."""


    asset_path = get_asset_path(asset_name)


    if not asset_path.exists():
        print(f"\nAsset '{asset_name}' does not exist.")
        return False


    print("\n")
    print(f"Validating asset: {asset_name}")
    print("----------------------------------------")


    all_valid = True


    for department in DEPARTMENTS:
          
        required_folders = [
            asset_path / department / "work",
            asset_path / department / "final",
            asset_path / department / "publish"
        ]


        for folder in required_folders:
            if folder.exists():
                print(f"[OK]      {folder.relative_to(asset_path)}")

            else:
                print(f"[MISSING] {folder.relative_to(asset_path)}")
                all_valid = False



    print("----------------------------------------")

    if all_valid:
        print("VALIDATION SUCCESSFUL")

    else:

        print("VALIDATION FAILED")


    return all_valid

# CREATE VERSION

def create_version(asset_name, department):
    """Create the next version of an asset department."""


    department = department.lower().strip()


    if department not in DEPARTMENTS:
        print("\nInvalid department.")
        print("Available departments:")
        print(", ".join(DEPARTMENTS))
        return


    department_path = get_asset_path(asset_name) / department

    if not department_path.exists():
        print(f"\nDepartment '{department}' does not exist.")
        return


    versions = []



# Look for existing v001, v002 etc.    
    for item in department_path.iterdir():

        if item.is_dir() and item.name.startswith("v"):

            try:
                number = int(item.name[1:])
                versions.append(number)
            except ValueError:
                pass


    if versions:
        next_number = max(versions) + 1
    else:
        next_number = 1


    version_name = f"v{next_number:03d}"

    version_path = department_path / version_name

    version_path.mkdir(parents=True)

# Update metadata    
    metadata = load_metadata(asset_name)

    version_info = {
        "department": department,
        "version": version_name,
        "status": "Work",
        "created": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }


    metadata["versions"].append(version_info)

    save_metadata(asset_name, metadata)


    print("\n----------------------------------------")
    print("Version created successfully!")
    print("----------------------------------------")
    print(f"Asset:  {asset_name}")
    print(f"Department:{department}")
    print(f"Version:   {version_name}")
    print(f"Location:  {version_path}")
    print("----------------------------------------")



# PUBLISH ASSET
def publish_asset(asset_name, department, version):
    """Publish a version of an asset."""

    department = department.lower().strip()
    version = version.lower().strip()


    if department not in DEPARTMENTS:
        print("\nInvalid department.")
        return


    source_path = (
        get_asset_path(asset_name)
        / department
        / version
        )


    publish_path = (
        get_asset_path(asset_name)
        / department
        / "publish"
        / version
        )


    if not source_path.exists():    
        print(f"\nVersion '{version}' does not exist.") 
        return


    if publish_path.exists():
        print(f"\nVersion '{version}' is already published.")
        return


# Validate before publishing    
    print("\nValidating asset before publishing...")


    if not validate_asset(asset_name):
        print("\nPublishing cancelled because validation failed.")
        return


    publish_path.parent.mkdir(parents=True, exist_ok=True)

    shutil.copytree(source_path, publish_path)


# Update metadata    
    metadata = load_metadata(asset_name)



    for version_info in metadata["versions"]:

        if (
            version_info["department"] == department
            and version_info["version"] == version
            ):
                version_info["status"] = "Published"
                version_info["published"] = (
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                )

    save_metadata(asset_name, metadata)

    print("\n----------------------------------------")
    print("ASSET PUBLISHED")
    print("----------------------------------------")
    print(f"Asset:     {asset_name}")
    print(f"Department:{department}")
    print(f"Version:   {version}")
    print(f"Location:  {publish_path}")
    print("----------------------------------------")

# SEARCH ASSETS
def search_asset(search_term):
    """Search for assets by name."""

    if not BASE_DIR.exists():
        print("\nNo assets found.")
        return


    search_term = search_term.lower().strip()

    results = []


    for asset_folder in BASE_DIR.iterdir():

        if asset_folder.is_dir():

            if search_term in asset_folder.name.lower():
                results.append(asset_folder.name)


    print("\n----------------------------------------")
    print("SEARCH RESULTS")
    print("----------------------------------------")


    if not results:
        print("No matching assets found.")
        return


    for asset in results:
        print(f"[FOUND] {asset}")



    print("----------------------------------------")

# SHOW ASSET INFORMATION

def show_asset_info(asset_name):
    """Display metadata for an asset."""


    asset_path = get_asset_path(asset_name)

    if not asset_path.exists():
        print(f"\nAsset '{asset_name}' does not exist.")
        return


    metadata = load_metadata(asset_name)


    print("\n========================================")
    print("ASSET INFORMATION")
    print("========================================")


    print(f"Asset:   {metadata['asset_name']}")
    print(f"Created: {metadata['created']}")


    print("\nVersions:")
    print("----------------------------------------")


    if not metadata["versions"]:
        print("No versions created yet.")
    else:

        for version in metadata["versions"]:
            print(
                    f"{version['department']:12} "
                    f"{version['version']:6} "
                    f"{version['status']}"
                )

            print(f"  Created: {version['created']}")

            if "published" in version:
                print(f"  Published: {version['published']}")

    print("========================================")

# PIPELINE REPORT
def generate_report():
    """Generate a summary of the entire CG pipeline."""

    if not BASE_DIR.exists():
        print("\nNo assets available.")
        return


    total_assets = 0
    total_versions = 0
    published_versions = 0
    work_versions = 0

    print("\n========================================")
    print("       CG PIPELINE REPORT")
    print("========================================")


    for asset_folder in BASE_DIR.iterdir():

        if not asset_folder.is_dir():
            continue

        total_assets += 1

    metadata = load_metadata(asset_folder.name)


    for version in metadata["versions"]:

        total_versions += 1

        if version["status"] == "Published":
            published_versions += 1

        elif version["status"] == "Work":
            work_versions += 1

    print(f"Total Assets:       {total_assets}")
    print(f"Total Versions:     {total_versions}")
    print(f"Work Versions:      {work_versions}")
    print(f"Published Versions: {published_versions}")

    print("========================================")

# MAIN MENU

def main():

    BASE_DIR.mkdir(exist_ok=True)

    while True:

        print("\n")
        print("CG ASSET PIPELINE MANAGER")
        print("\n")
        print("1. Create Asset")
        print("2. Validate Asset")
        print("3. Create Version")
        print("4. Publish Asset")
        print("5. Search Asset")
        print("6. Show Asset Information")
        print("7. Generate Pipeline Report")
        print("8. Exit")
        

        choice = input("Enter your choice: ").strip()

# CREATE ASSET        
        if choice == "1":

            asset_name = input(
                "Enter asset name: "
            ).strip()


            create_asset(asset_name)
# VALIDATE ASSET

        elif choice == "2":

            asset_name = input(
                "Enter asset name to validate: "
            ).strip()

            validate_asset(asset_name)

# CREATE VERSION        

        elif choice == "3":

            asset_name = input(
                "Enter asset name: "
            ).strip()

            department = input(
                "Enter department "
                "(model/texture/rig/animation/render): "
            ).strip()

            create_version(asset_name, department)
# PUBLISH ASSET

        elif choice == "4":

            asset_name = input(
                "Enter asset name: "
                ).strip()
            department = input(
                    "Enter department: "
                ).strip()
            version = input(
                "Enter version (example: v001): "
                ).strip()
            publish_asset(
                asset_name,
                department,
                version
                )
 # SEARCH

        elif choice == "5":

            search_term = input(
                "Enter asset name to search: "
                ).strip()

            search_asset(search_term)

# ASSET INFORMATION        
    
        elif choice == "6":

            asset_name = input(
                "Enter asset name: "
                ).strip()

            show_asset_info(asset_name)

# REPORT
        elif choice == "7":

            generate_report()

# EXIT

        elif choice == "8":

            print("\nExiting CG Asset Pipeline...")
            break

        else:
            print("\nInvalid choice.")
            print("Please select a number from 1 to 8.")

#PROGRAM START
if __name__ == "__main__":
        main()