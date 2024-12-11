from datetime import datetime

from pr.tracker import run as pr_run
from citizenship.tracker import run as citizenship_run


def update_readme_last_updated(readme_path="README.md"):
    """
    Updates the 'Last updated' timestamp in the README file with the current datetime.

    Args:
        readme_path (str): Path to the README file to be updated.
    """
    try:
        # Get the current date and time in the desired format
        current_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Read the contents of the README file
        with open(readme_path, "r") as file:
            readme_content = file.readlines()

        # Update the 'Last updated' lines
        updated_content = []
        for line in readme_content:
            if "Last updated:" in line:
                updated_line = f"{line.split('Last updated:')[0]}Last updated: {current_datetime}_\n"
                updated_content.append(updated_line)
            else:
                updated_content.append(line)

        # Write the updated content back to the README file
        with open(readme_path, "w") as file:
            file.writelines(updated_content)

        print(f"README.md successfully updated with 'Last updated' timestamp: {current_datetime}")
    except Exception as e:
        print(f"Failed to update README.md: {e}")


def main():
    print("\nRunning PR Tracker...")
    pr_run()

    print("\nRunning Citizenship Tracker...")
    citizenship_run()

    print("\nUpdating README.md...")
    update_readme_last_updated()


if __name__ == "__main__":
    main()
