#!/usr/bin/env python3

import urllib.request
import argparse
import json
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
    'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:93.0) Gecko/20100101 Firefox/93.0',
    'Accept': 'application/vnd.twitchtv.v5+json',
    'Client-ID': 'ekj09tcx24qymrl1wl5c6er2qjkpryz'
  }
  request = urllib.request.Request(url=twitch_url, headers=headers)
  with urllib.request.urlopen(request) as response:
    data = json.loads(response.read())
    return data['users'][0]['_id']


def print_monthly_revenue(user_id):
  revenues = subprocess.check_output([
    "rg",
    "-IN",
    "--color=never",
    user_id,
    "all_revenues"
  ], encoding="UTF-8")

  date_and_money = []
  rows = revenues.splitlines()
  for row in rows:
    date = row.split(",")[11]
    revenues = get_revenues_from_row(row)
    revenues_float = list(map(float, revenues))
    revenues_sum = sum(revenues_float)
    date_and_money.append({
      'date': date,
      'money': revenues_sum
    })

  def sort_key(x):
    date = datetime.strptime(x['date'], '%m/%d/%Y')
    timestamp = datetime.timestamp(date)
    return timestamp
  sort_by_date = sorted(date_and_money, key=sort_key)

  for x in sort_by_date:
    print(x['date'], x['money']);


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
