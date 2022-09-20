from nis import match
from ntpath import join
import os
import re
import json

HEAD_BRANCH = os.getenv('HEAD_BRANCH', default="main")
WATCH_CHANGES_FILES = re.compile(
    rf'{os.getenv("WATCH_CHANGES_FILES",default=".*yaml$|.*hcl$")}'
)
WATCH_DIRS = re.compile(
    rf'{os.getenv("WATCH_DIRS",default=".*")}'
)
MERGE_COMMON_LABELS = os.getenv('MERGE_COMMON_LABELS', default=0)

git_files_diff = []
git_fetch_changes_cmd = f"git diff --name-only HEAD origin/{HEAD_BRANCH}"

matrix_dict = {"include": []}

walkback_dict = {}


def walk_reverse(item):
    for iter, change in enumerate(item):
        path = change.split('/')
        matrix_dict["include"].append({f"{change}": "null"})
        for i in range(len(path)):
            matrix_dict['include'][int(
                iter)][f"walkback_{i}"] = f"{'/'.join(path[:i+1])}"


with os.popen(git_fetch_changes_cmd) as f:
    for file in f.readlines():
        if WATCH_CHANGES_FILES.findall(file) and WATCH_DIRS.findall(file):
            git_files_diff.append(re.sub('\n', '', file))

walk_reverse(git_files_diff)

if MERGE_COMMON_LABELS:
    # create a single dict with all unique fields
    merged_changes = {}
    for item in matrix_dict['include']:
        merged_changes.update(item)

    # reset dict and populate with merged changes
    matrix_dict['include'] = []
    matrix_dict['include'].append(merged_changes)

print(json.dumps(matrix_dict))

print(f"::set-output name=matrix::{json.dumps(matrix_dict)}")
