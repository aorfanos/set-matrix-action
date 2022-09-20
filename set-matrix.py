from ntpath import join
import os
import re
import json

HEAD_BRANCH = os.getenv('HEAD_BRANCH', default="main")
WATCH_CHANGES_FILES = re.compile(
    rf'{os.getenv("WATCH_CHANGES_FILES",default=".*yaml$|.*hcl$")}'
)

git_files_diff = []
git_fetch_changes_cmd = f"git diff --name-only HEAD origin/{HEAD_BRANCH}"

matrix_dict = {"include": []}

walkback_dict = {}


def walk_reverse(item):
    for iter, change in enumerate(item):
        path = change.split('/')
        matrix_dict["include"].append({f"{change}": []})
        for i in range(len(path)):
            matrix_dict['include'][int(
                iter)][f"{change}"][f"walkback_{i}"] = f"{'/'.join(path[:i+1])}"


with os.popen(git_fetch_changes_cmd) as f:
    for file in f.readlines():
        if WATCH_CHANGES_FILES.findall(file):
            git_files_diff.append(re.sub('\n', '', file))

walk_reverse(git_files_diff)
print(json.dumps(matrix_dict))

print(f"::set-output name=matrix::{json.dumps(matrix_dict)}")
