#!/usr/bin/env sh

# Copyright (C) 2017 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>

set -o errexit
set -o nounset

declare -r SCRIPTPATH=$( cd "$(dirname "$0")" ; pwd -P )
cd "${SCRIPTPATH}/../../"

usage () {
  cat <<EOF
Usage: $(basename ${0})

Fetch the latest upstream/master,
search src/ggrc/settings/default.py for the version number,
create a tag with the name equal to the version number,
push it to upstream.

Prerequisites:
1. Google repo is pointed by "upstream" remote.
2. Git is configured to sign tags
(see https://help.github.com/articles/signing-commits-with-gpg/)
EOF
}

write_visible_message () {
  message=${1:-}
  echo '-----'
  echo ${message}
  echo '-----'
}

main () {
  if [[ "${1:-}" == "--help" ]]; then
    usage
    exit 0
  fi

  git fetch upstream master

  v=$(python -c "BUILD_NUMBER='' ; $(grep 'VERSION =' src/ggrc/settings/default.py) ; print VERSION")
  git tag -s -m "$v" $v FETCH_HEAD

  write_visible_message "$(git rev-parse FETCH_HEAD) is tagged as $v"
  git show $v

  write_visible_message "Pushing $v to upstream:"
  git push upstream $v
}

main "$@"
