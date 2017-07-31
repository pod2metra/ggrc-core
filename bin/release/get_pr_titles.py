#!/usr/bin/env python

# Copyright (C) 2017 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>

"""Utility script to get a list of pull requests merged since some tag.

Usage:
  get_pr_titles.py TAG_NAME

Tries to guess ticket ids from pull request titles.
"""


from __future__ import print_function

import argparse
import collections
import getpass
import re
import subprocess
import sys

import requests


class PrGetter(object):  # pylint: disable=too-few-public-methods
  """Github REST client to fetch PR data."""
  URL_PATTERN = "https://api.github.com/repos/google/ggrc-core/pulls/{id}"

  def __init__(self, auth):
    self.session = requests.Session()
    self.auth = auth

  @classmethod
  def _make_pr_url(cls, pr_id):
    return cls.URL_PATTERN.format(id=pr_id)

  def get_pr(self, pr_id):
    """Fetch JSON description for PR by its id"""
    response = self.session.get(self._make_pr_url(pr_id),
                                auth=self.auth)
    if response.status_code != 200:
      raise ValueError(u"Expected HTTP200 response, found "
                       u"status_code={status_code}, body={body}"
                       .format(status_code=response.status_code,
                               body=response.body))
    return response.json()


def parse_argv(argv):
  """Get argv and return a parsed arguments object.

  Supported arguments:
    previous_release_tag (str)
    --upstream (str, default "upstream")
    --branch (str, default "release/0.10-Raspberry")
  """
  parser = argparse.ArgumentParser(
      description="Get PR titles from current release",
  )
  parser.add_argument("previous_release_tag", type=str,
                      help="The name of the previous release tag")
  parser.add_argument("--upstream", type=str, default="upstream",
                      help="The name of the main git remote, "
                           "default 'upstream'")
  parser.add_argument("--branch", type=str, default="release/0.10-Raspberry")

  return parser.parse_args(argv)


def git_diff(upstream, branch, tag):
  """Get git diff --oneline between tag and latest upstream/branch."""
  subprocess.check_call(["git", "fetch", upstream, branch])

  log_target = "{tag}..{upstream}/{branch}".format(
      tag=tag,
      upstream=upstream,
      branch=branch,
  )
  return subprocess.check_output(["git", "log", "--oneline", log_target])


def get_pr_ids(message_list):
  """Get PR ids from git log --oneline output (skip non-merge lines)."""
  merge_commit_pattern = r"Merge pull request #(?P<id>\d+)"
  for line in message_list:
    match = re.search(merge_commit_pattern, line)
    if match:
      yield match.group("id")


def try_parse_ticket_ids(title):
  """Get ticket id from PR title.

  Assumptions:
    - ticket id or special prefix before PR title
    - no whitespace before ticket id
    - whitespace between ticket id and PR title

  Transformations (for the worst case):
    "ggrc-1234/1235: Do something" -> ["GGRC-1234", "GGRC-1235"]

  Special prefixes:
    "QUICK-FIX", "DOCS"

  Returns:
    a list of string ticket ids.
  """
  ticket = title.split()[0]
  ticket = ticket.upper()
  ticket = ticket.rstrip(":")

  if ticket in ("QUICK-FIX", "DOCS"):
    return [ticket]

  ticket = ticket.replace("/", ",")
  tickets = []
  for ticket in ticket.split(","):
    if not ticket.startswith("GGRC-"):
      ticket = "GGRC-" + ticket
    tickets.append(ticket)

  return tickets


def print_pr_details(pr_details):
  """Print PR list summary in table format.

  For each PR, try to guess ticket id(s) and print a table with columns:
    - PR id
    - ticket id(s) comma-separated
    - assignee username or "None"
    - milestone name or "None"
    - PR title

  Also print a Jira-friendly list of ticket ids guessed from the PRs.
  """
  assumed_tickets = set()

  row_tuple = collections.namedtuple(
      "Row",
      ["id", "ticket", "assignee", "milestone", "title"],
  )
  header = row_tuple(*row_tuple._fields)
  rows = [header]

  for id_, details in pr_details.iteritems():
    tickets = try_parse_ticket_ids(details.get("title"))
    assumed_tickets.update(tickets)
    rows.append(row_tuple(
        id=str(id_),
        ticket=", ".join(tickets),
        assignee=(details.get("assignee") or {}).get("login"),
        milestone=(details.get("milestone") or {}).get("title"),
        title=details.get("title"),
    ))

  max_widths = [max(len(unicode(v)) for v in column)
                for column in zip(*rows)]

  print(u" | ".join(u"{0:{width}}".format(field, width=width)
                    for field, width in zip(header, max_widths)))
  print(u"-|-".join(u"-" * width for width in max_widths))

  for row in rows[1:]:
    print(u" | ".join(u"{0:{width}}".format(field, width=width)
                      for field, width in zip(row, max_widths)))

  print("")
  print("Assumed ticket ids")
  print(", ".join(assumed_tickets))


def main():
  """Get and print the details of pull requests merged since some tag."""
  args = parse_argv(sys.argv[1:])

  git_output = git_diff(upstream=args.upstream,
                        branch=args.branch,
                        tag=args.previous_release_tag)

  pull_request_ids = get_pr_ids(git_output.split("\n"))

  username = raw_input("Username: ")
  password = getpass.getpass("Password: ")

  pr_getter = PrGetter(auth=requests.auth.HTTPBasicAuth(username, password))

  pull_request_details = {}
  for pull_request_id in pull_request_ids:
    pull_request_details[pull_request_id] = pr_getter.get_pr(pull_request_id)

  print_pr_details(pull_request_details)


if __name__ == "__main__":
  exit(main())
