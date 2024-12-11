from pr.cec.tracker import run as cec_run
from pr.spousal.tracker import run as spousal_run


def run():
    print("\nRunning CEC Tracker...")
    cec_run()
    print("\nRunning Spousal Tracker...")
    spousal_run()


if __name__ == "__main__":
    run()
