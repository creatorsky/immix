import pandas as pd
import json
from tqdm import tqdm
import requests
import matplotlib.pyplot as plt
import os

# Get the directory of this file
MODULE_DIR = os.path.dirname(os.path.abspath(__file__))

# Paths to JSON files
COLUMNS_FILE = os.path.join(MODULE_DIR, "columns.json")
DATA_FILE = os.path.join(MODULE_DIR, "data.json")
PLOT_FILE = os.path.join(MODULE_DIR, "citizenship_tracker.png")


def get_and_write_data():
    values = []

    payload = {}
    headers = {
        'accept': 'application/json;charset=UTF-8',
        'accept-language': 'en-CA,en-GB;q=0.9,en-US;q=0.8,en;q=0.7',
        'cache-control': 'no-cache',
        'dnt': '1',
        'pragma': 'no-cache',
        'priority': 'u=1, i',
        'referer': 'https://myimmitracker.com/en/ca/trackers/canadian-citizenship-processing-tracker',
        'sec-ch-ua': '"Google Chrome";v="129", "Not=A?Brand";v="8", "Chromium";v="129"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"macOS"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36',
        'x-requested-with': 'XMLHttpRequest',
        'Cookie': '_honshu_session=ZFdyU2hhcHdaWGVUQllKNWlCTGF4QWhLbU0yZzlrbFRrTUpubTF0T1RGZTh3bU9wYWltQ3BodE80Qk1Qd0FvWkNLM3hLVUVyQlQvWVVYSmJJNW9IN2pwMytnQVNtT24zZ1ZvR1V3V2tTSU9hLzZzbDBVNG5ra1J3djZqSUpnV2FaVTlqK2cwNUpVM0xoaWl4UEhnV0s2WER5MVhUM1hVWmFiVThUR2M4UVpWcHo1dnV1S3lNTFU5TzZpdXArWDJZL2ZCOUJNMFJUOUFtcTRvUzZlaG9IL3F0UGZnMmZVczAvNldaN0Z6N0QzZWdtWnoyVlBzNUx1QkFSL0htdjhHa2pxK2tzelVYNFZDNm5ZWUVTcUllZUNNUWo3eG1PakZDZU0xQkRSWFlHeTlUcVhNZFVFaEl4OHc4MmdMUm9iWi9WRmRjRDQ4V0VZNGdpSWQ0aUdJWWpRPT0tLXorZWxWRjVDRG5zOHBpMjN4UkpKQ2c9PQ%3D%3D--3b6fd62562c482855ac079a1e94547274ea699a7; l=en'
    }

    url_0 = "https://myimmitracker.com/ca/trackers/canadian-citizenship-processing-tracker/cases?start=0&filter=%7B%22state%22%3A%5B%22Active%22%5D%7D&sort=%5B%5B%22updated%22%2C%22desc%22%5D%5D"
    total_cases = requests.request("GET", url_0, headers=headers, data=payload).json()["cases_count"]

    print(f"Total cases: {total_cases}")

    for i in tqdm(range(0, total_cases, 100)):
        url = f"https://myimmitracker.com/ca/trackers/canadian-citizenship-processing-tracker/cases?start={i}&filter=%7B%22state%22%3A%5B%22Active%22%5D%7D&sort=%5B%5B%22updated%22%2C%22desc%22%5D%5D"
        response = requests.request("GET", url, headers=headers, data=payload)
        values.extend(response.json()["values"])

    with open(DATA_FILE, "w") as f:
        json.dump(values, f)


def get_field_to_columns():
    """
    columns.json
    {
    "columns": [
      {
        "headerName": "Current status",
        "field": "xekim-tabom-koguk-liven-mepis-fegyc-fufyt-kanac-foxex",
        "type": "select",
        "width": null,
        "headerTooltip": "your current status",
        "filterValues": [
          "Sent",
          "Delivered",
          "AOR",
          "In-process",
          "Test letter received",
          "Test scheduled",
          "Decision Made",
          "Oath Letter received",
          "Oath completed"
        ]
      },
      {
        "headerName": "Online/Paper Application",
        "field": "xelam-segit-henid-vimem-surad-selit-repaf-bykyd-hixex",
        "type": "select",
        "width": null,
        "headerTooltip": "Online or Paper Application",
        "filterValues": [
          "Paper",
          "Online"
        ]
      },
      ...
      ]
    }
    """

    # return field to headerName mapping
    with open(COLUMNS_FILE, "r") as f:
        columns = json.load(f)["columns"]
        field_to_header_name = {column["field"]: column["headerName"] for column in columns}

    return field_to_header_name


def read_data():
    with open(DATA_FILE, "r") as f:
        data = json.load(f)
    return data


def get_analyrics(df):
    # List of columns relevant to the process
    validated_columns_with_aor = [
        'Application Sent Date',
        'AOR Date',
        'In-Process (ECAS) date',
        'Test Invite letter received date',
        'Test date',
        'Oath Letter date',
        'Oath Ceremony date'
    ]

    # Convert relevant columns to datetime
    for col in validated_columns_with_aor:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors='coerce')

    # Filter for valid rows with non-null values in all relevant columns
    valid_data = df.dropna(subset=validated_columns_with_aor)

    # Calculate average time between steps
    step_durations = {}
    for i in range(len(validated_columns_with_aor) - 1):
        step_name = f"{validated_columns_with_aor[i]} to {validated_columns_with_aor[i + 1]}"
        time_diff = (valid_data[validated_columns_with_aor[i + 1]] - valid_data[validated_columns_with_aor[i]]).dt.days
        step_durations[step_name] = time_diff.mean()

    # Create a DataFrame to store and format the results
    step_durations_df = pd.DataFrame.from_dict(
        step_durations, orient='index', columns=['Average Time (Days)']
    ).round(0).reset_index()

    step_durations_df.columns = ['Processing Step', 'Average Time (Days)']

    return step_durations_df


def plot_analytics(df):
    # Remove the word "date" (case-insensitive) from all y-axis labels
    df["Processing Step"] = df["Processing Step"].str.replace(" date", "", regex=False)
    df["Processing Step"] = df["Processing Step"].str.replace(" Date", "", regex=False)

    # Calculate total days
    total_days = df["Average Time (Days)"].sum()

    # Create the plot again
    plt.xkcd(scale=1, length=100, randomness=2)  # Apply xkcd style

    fig, ax = plt.subplots(figsize=(13, 6))
    bars = ax.barh(df["Processing Step"], df["Average Time (Days)"], color='skyblue')

    # Add text to bars
    for bar in bars:
        width = bar.get_width()
        ax.text(width + 1, bar.get_y() + bar.get_height() / 2, f"{int(width)} days",
                va='center', ha='left', fontsize=10)

    # Add "Total days" text in the top right
    ax.text(max(df["Average Time (Days)"]) + 30, -0.5,
            f"Total days: {int(total_days)}", fontsize=14, ha='center', color='red',
            bbox=dict(facecolor='white', alpha=0.8))

    # Title and labels
    ax.set_title("Canadian Citizenship Tracker", fontsize=16, loc='center')
    ax.set_xlabel("")
    ax.set_ylabel("")
    ax.set_xlim(0, max(df["Average Time (Days)"]) + 50)

    # Properly reverse the y-axis order
    ax.invert_yaxis()

    plt.tight_layout()
    plt.savefig(PLOT_FILE)
    plt.close(fig)


def main():
    # get_and_write_data()
    data = read_data()
    df = pd.DataFrame(data)
    field_to_header_name = get_field_to_columns()
    # if df column name present in field_to_header_name, replace it with headerName
    df.columns = [field_to_header_name.get(col, col) for col in df.columns]

    step_durations_df = get_analyrics(df)
    plot_analytics(step_durations_df)


if __name__ == "__main__":
    main()
