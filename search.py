#!/usr/bin/env python3

import urllib.request
import argparse
import json
import math
from datetime import datetime
import subprocess


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("username", help="Twitch username")
    args = parser.parse_args()
    username = args.username
    user_id = get_user_id(username)
    print_monthly_revenue(user_id)


def get_user_id(username):
    # client ID is stolen from: https://www.streamweasels.com/support/convert-twitch-username-to-user-id/
    twitch_url = f"https://api.twitch.tv/kraken/users?login={username}"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:93.0) Gecko/20100101 Firefox/93.0",
        "Accept": "application/vnd.twitchtv.v5+json",
        "Client-ID": "ekj09tcx24qymrl1wl5c6er2qjkpryz",
    }
    request = urllib.request.Request(url=twitch_url, headers=headers)
    with urllib.request.urlopen(request) as response:
        if response.status != 200:
            raise Exception("The Twitch API request failed.")

        data = json.loads(response.read())
        if data["_total"] == 0:
            raise Exception("The username provided is not found.")

        return data["users"][0]["_id"]


def print_monthly_revenue(user_id):
    revenues = None

    run_result = subprocess.run(
        ["rg", "-IN", "--color=never", user_id, "all_revenues"],
        encoding="UTF-8",
        capture_output=True,
    )
    if run_result.returncode == 0:
        revenues = run_result.stdout
    else:
        raise Exception(
            "The user's revenue was not found in the data. This can also happen if the user was banned."
        )

    dates_and_money = []
    rows = revenues.splitlines()
    for row in rows:
        date = row.split(",")[11]
        revenues = get_revenues_from_row(row)
        revenues_float = list(map(float, revenues))
        revenues_sum = sum(revenues_float)
        dates_and_money.append({"date": date, "money": revenues_sum})

    def timestamp(x):
        date = datetime.strptime(x["date"], "%m/%d/%Y")
        timestamp = datetime.timestamp(date)
        return timestamp

    sort_by_date = sorted(dates_and_money, key=timestamp)

    printed = set()
    for x in sort_by_date:
        if x["date"] in printed:
            continue
        print(x["date"], math.floor(x["money"]))
        printed.add(x["date"])


def get_revenues_from_row(row):
    columns = row.split(",")
    if len(columns) == 13:
        a = columns[2:-2]
        a.append(columns[-1])
        return a
    else:
        return columns[2:-1]


if __name__ == "__main__":
    main()
