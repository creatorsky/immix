# Immix Tracker Suite

This repository provides trackers for processing times in various Canadian immigration and citizenship processes. The graphs are updated weekly with the latest data, so you can rely on the updated version of these images without necessarily running the scripts.

---

## Canadian Citizenship Tracker

This tracker displays the average time for each processing step in the Canadian citizenship process. The graph below is updated weekly with the latest data.

![Canadian Citizenship Tracker](citizenship/citizenship_tracker.png)

### Total Days
The total processing time from "Application Sent" to "Oath Ceremony" is displayed at the top-right corner of the graph.

_Last updated: 2024-12-11 20:31:20_

---

## Canadian PR Trackers

### CEC PR Tracker

This tracker displays the average time for each processing step in the Canadian CEC PR process. The graph below is updated weekly with the latest data.

![CEC PR Tracker](pr/cec/cec_pr_tracker.png)

### Total Days
The total processing time from "AOR" to "CoPR" is displayed at the top-right corner of the graph.

_Last updated: 2024-12-11 20:31:20_

---

### Spousal PR Tracker

This tracker displays the average time for each processing step in the Canadian Spousal PR process. The graph below is updated weekly with the latest data.

![Spousal PR Tracker](pr/spousal/spousal_pr_tracker.png)

### Total Days
The total processing time from "Application Submitted" to "Passport Request" is displayed at the top-right corner of the graph.

_Last updated: 2024-12-11 20:31:20_

---

## Usage

The images are updated weekly automatically. However, if you'd like to manually update all trackers, you can run the root script:

```bash
python immix.py
