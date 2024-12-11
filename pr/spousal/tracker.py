import textwrap

import pandas as pd
import json
from tqdm import tqdm
import requests
import matplotlib.pyplot as plt
import os
from datetime import datetime, timedelta

pd.set_option('display.max_columns', None)

# Get the directory of this file
MODULE_DIR = os.path.dirname(os.path.abspath(__file__))

# Paths to JSON files
COLUMNS_FILE = os.path.join(MODULE_DIR, "columns.json")
DATA_FILE = os.path.join(MODULE_DIR, "data.json")
PLOT_FILE = os.path.join(MODULE_DIR, "spousal_pr_tracker.png")


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

    url_0 = "https://myimmitracker.com/ca/trackers/consolidated-spousal-sponsorship-tracker/cases?start=0&filter=%7B%22state%22%3A%5B%22Active%22%5D%7D&sort=%5B%5B%22updated%22%2C%22desc%22%5D%5D"
    total_cases = requests.request("GET", url_0, headers=headers, data=payload).json()["cases_count"]

    print(f"Total cases: {total_cases}")

    for i in tqdm(range(0, total_cases, 100)):
        url = f"https://myimmitracker.com/ca/trackers/consolidated-spousal-sponsorship-tracker/cases?start={i}&filter=%7B%22state%22%3A%5B%22Active%22%5D%7D&sort=%5B%5B%22updated%22%2C%22desc%22%5D%5D"
        response = requests.request("GET", url, headers=headers, data=payload)
        values.extend(response.json()["values"])

    with open(DATA_FILE, "w") as f:
        json.dump(values, f)


def get_field_to_columns():
    # return field to headerName mapping
    with open(COLUMNS_FILE, "r") as f:
        columns = json.load(f)["columns"]
        field_to_header_name = {column["field"]: column["headerName"] for column in columns}

    return field_to_header_name


def read_data():
    with open(DATA_FILE, "r") as f:
        data = json.load(f)
    return data


def get_analytics(df):
    intervals = {
        'Application Submitted to AOR': ['Application Submitted On', 'AOR Date'],
        'AOR to Sponsor Approval': ['AOR Date', 'Sponsor Approval date'],
        'Sponsor Approval to Background Check Start': ['Sponsor Approval date', 'Background Check In Progress'],
        'Background Check Start to Completion': ['Background Check In Progress', 'Background Check Completed'],
        'Medical Request to Passed': ['Medical Request Date', 'Medical Passed Date'],
        'Application Submitted to Passport Request': ['Application Submitted On', 'Passport Request Date']
    }

    one_year_ago = datetime.now() - timedelta(days=365)
    df_filtered = df[pd.to_datetime(df['Application Submitted On'], errors='coerce') >= one_year_ago].copy()

    results = []
    for step, (start_col, end_col) in intervals.items():
        df_filtered[step] = (
                pd.to_datetime(df_filtered[end_col], errors='coerce') -
                pd.to_datetime(df_filtered[start_col], errors='coerce')
        ).dt.days
        data = df_filtered[step].dropna()

        mean = data.mean() if len(data) > 0 else None
        results.append([step, mean])

    return pd.DataFrame(results, columns=['Processing Step', 'Average Time (Days)'])


def plot_analytics(df):
    # Handle cases where "Total Time to Passport Request" might not exist
    total_days = \
    df.loc[df["Processing Step"] == "Application Submitted to Passport Request", "Average Time (Days)"].values[
        0] if "Application Submitted to Passport Request" in df["Processing Step"].values else 0

    # Create the plot
    plt.xkcd(scale=1, length=100, randomness=2)  # Apply xkcd style
    df_plot = df[df["Processing Step"] != "Application Submitted to Passport Request"].copy()

    fig, ax = plt.subplots(figsize=(10, 8))
    df_plot["Processing Step"] = df_plot["Processing Step"].apply(lambda x: "\n".join(textwrap.wrap(x, width=20)))

    bars = ax.barh(df_plot["Processing Step"], df_plot["Average Time (Days)"], color='skyblue')

    # Add text to bars
    for bar in bars:
        width = bar.get_width()
        ax.text(width + 1, bar.get_y() + bar.get_height() / 2, f"{int(width)} days",
                va='center', ha='left', fontsize=17)

    # Add "Total days" text in the top right
    ax.text(max(df_plot["Average Time (Days)"]) + 2, 0,
            f"Total days: {int(total_days)}", fontsize=17, ha='center', color='red',
            bbox=dict(facecolor='white'))

    # Title and labels
    ax.set_title("Canadian Spousal PR Tracker", fontsize=20, loc='center')
    ax.set_xlabel("")
    ax.set_ylabel("")

    # Dynamically set x-axis range (e.g., add 10% buffer)
    max_days = max(df_plot["Average Time (Days)"])
    ax.set_xlim(0, max_days + max_days * 0.3)  # Add a 30% buffer above max_days

    # Properly reverse the y-axis order
    ax.invert_yaxis()

    plt.tight_layout()
    plt.savefig(PLOT_FILE)
    plt.close(fig)


def run():
    # get_and_write_data()
    data = read_data()
    df = pd.DataFrame(data)
    field_to_header_name = get_field_to_columns()
    # if df column name present in field_to_header_name, replace it with headerName
    df.columns = [field_to_header_name.get(col, col) for col in df.columns]
    step_durations_df = get_analytics(df)
    plot_analytics(step_durations_df)


if __name__ == "__main__":
    run()
