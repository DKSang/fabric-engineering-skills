#!/usr/bin/env python3
"""Change detection for document-fabric-workspace.

Works out which items and tables of a workspace need (re)documenting, so a
re-run reads only what changed. Read-only against Fabric: the only `fab`
command it runs is `fab ls`.

  plan    compare the live workspace with the state file, print a plan
  commit  after documenting, record what the plan covered in the state file

Run `python workspace_state.py <command> --help` for options.
"""

import argparse
import datetime as dt
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile

SCHEMA_VERSION = 1
DEFAULT_MAX_AGE_DAYS = 30


def now():
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat()


def parse_time(value):
    return dt.datetime.fromisoformat(value.replace("Z", "+00:00"))


# ---------------------------------------------------------------- fab (read-only)


def fab_ls(path, long=True):
    """Run `fab ls` and return its rows. This is the only fab call made."""
    exe = shutil.which("fab")
    if not exe:
        sys.exit("error: `fab` not found on PATH")
    cmd = [exe, "ls", path] + (["-l"] if long else []) + ["--output_format", "json"]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        sys.exit(f"error: fab ls {path!r} failed:\n{proc.stdout}{proc.stderr}")
    try:
        payload = json.loads(proc.stdout)
    except json.JSONDecodeError:
        sys.exit(f"error: fab ls {path!r} did not return JSON:\n{proc.stdout}")
    data = payload.get("result", {}).get("data", [])
    return [row for row in data if isinstance(row, dict)]


def split_name(full_name):
    """'nb_load.Notebook' -> ('nb_load', 'Notebook')."""
    name, _, item_type = full_name.rpartition(".")
    return (name, item_type) if name else (full_name, "")


# ---------------------------------------------------------------- fingerprints


def hash_folder(folder):
    digest = hashlib.sha256()
    for root, dirs, files in os.walk(folder):
        dirs.sort()
        for name in sorted(files):
            path = os.path.join(root, name)
            digest.update(os.path.relpath(path, folder).replace("\\", "/").encode())
            with open(path, "rb") as handle:
                digest.update(handle.read())
    return "files:sha256:" + digest.hexdigest()


def repo_item_folders(items_root):
    """Map (displayName, type) -> folder for Git-format items under items_root."""
    found = {}
    if not items_root:
        return found
    for root, dirs, files in os.walk(items_root):
        dirs[:] = [d for d in dirs if d != ".git"]
        if ".platform" not in files:
            continue
        try:
            with open(os.path.join(root, ".platform"), encoding="utf-8") as handle:
                meta = json.load(handle).get("metadata", {})
        except (OSError, json.JSONDecodeError):
            continue
        key = (meta.get("displayName"), meta.get("type"))
        if all(key):
            found[key] = root
    return found


# ---------------------------------------------------------------- tables


def lakehouse_tables(workspace, lakehouse):
    """Return {'<schema>/<table>' or '<table>': lastModified} for one lakehouse."""
    base = f"{workspace}.Workspace/{lakehouse}.Lakehouse/Tables"
    entries = fab_ls(base)
    if not entries:
        return {}
    # A lakehouse without schemas lists tables directly (each has a _delta_log);
    # a schema-enabled one lists schemas. Probe the first entry to tell which.
    first = fab_ls(f"{base}/{entries[0]['name']}", long=False)
    if any(row.get("name") == "_delta_log" for row in first):
        return {row["name"]: row.get("lastModified") for row in entries}
    tables = {}
    for schema in entries:
        for row in fab_ls(f"{base}/{schema['name']}"):
            tables[f"{schema['name']}/{row['name']}"] = row.get("lastModified")
    return tables


# ---------------------------------------------------------------- state


def load_state(path, workspace):
    if not os.path.exists(path):
        return {
            "schema_version": SCHEMA_VERSION,
            "workspace": {"name": workspace},
            "max_age_days": DEFAULT_MAX_AGE_DAYS,
            "items": {},
            "tables": {},
        }
    with open(path, encoding="utf-8") as handle:
        state = json.load(handle)
    if state.get("schema_version") != SCHEMA_VERSION:
        sys.exit(f"error: {path} has schema_version {state.get('schema_version')}, expected {SCHEMA_VERSION}")
    return state


def write_json(path, data):
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as handle:
        json.dump(data, handle, indent=2, sort_keys=True)
        handle.write("\n")
    os.replace(tmp, path)


def default_plan_path(workspace):
    safe = "".join(c if c.isalnum() or c in "-_" else "_" for c in workspace)
    return os.path.join(tempfile.gettempdir(), f"document-fabric-workspace-{safe}.plan.json")


# ---------------------------------------------------------------- commands


def cmd_plan(args):
    state = load_state(args.state, args.workspace)
    max_age = dt.timedelta(days=args.max_age_days or state.get("max_age_days", DEFAULT_MAX_AGE_DAYS))
    only = {name.strip() for name in args.only.split(",")} if args.only else None
    folders = repo_item_folders(args.items_root)
    known = state["items"]
    live = {}

    for row in fab_ls(f"{args.workspace}.Workspace"):
        if not row.get("id"):
            continue
        name, item_type = split_name(row["name"])
        folder = folders.get((name, item_type))
        live[row["id"]] = {
            "name": name,
            "type": item_type,
            "fingerprint": hash_folder(folder) if folder else None,
            "repo_folder": os.path.relpath(folder) if folder else None,
        }

    plan = {
        "workspace": args.workspace,
        "state": args.state,
        "planned_at": now(),
        "mode": "full" if args.full else ("only" if only else "incremental"),
        "new": [],
        "changed": [],
        "renamed": [],
        "stale": [],
        "removed": [],
        "unchanged": [],
        "tables": {"new": [], "changed": [], "removed": [], "unchanged": 0},
        "live_items": live,
        "live_tables": {},
    }

    for item_id, item in sorted(live.items(), key=lambda kv: (kv[1]["type"], kv[1]["name"])):
        entry = {"id": item_id, "name": item["name"], "type": item["type"]}
        old = known.get(item_id)
        if old is None:
            bucket, reason = "new", "not documented yet"
        elif only is not None:
            bucket, reason = ("changed", "requested") if item["name"] in only else ("unchanged", "")
        elif args.full:
            bucket, reason = "changed", "full refresh"
        elif old.get("name") != item["name"]:
            bucket, reason = "renamed", f"was {old.get('name')}"
        elif item["fingerprint"] and item["fingerprint"] != old.get("fingerprint"):
            bucket, reason = "changed", "repo definition changed"
        elif not item["fingerprint"] and parse_time(old["documented_at"]) < dt.datetime.now(dt.timezone.utc) - max_age:
            bucket, reason = "stale", f"no change signal; documented {old['documented_at'][:10]}"
        else:
            bucket, reason = "unchanged", ""
        if bucket == "unchanged":
            plan["unchanged"].append(entry["name"])
        else:
            entry["reason"] = reason
            plan[bucket].append(entry)

    for item_id, old in sorted(known.items(), key=lambda kv: kv[1].get("name", "")):
        if item_id not in live:
            plan["removed"].append({"id": item_id, "name": old.get("name"), "type": old.get("type")})

    if args.tables:
        old_tables = state.get("tables", {})
        for item_id, item in live.items():
            if item["type"] != "Lakehouse":
                continue
            for table, modified in lakehouse_tables(args.workspace, item["name"]).items():
                key = f"{item['name']}/{table}"
                plan["live_tables"][key] = modified
                old = old_tables.get(key)
                if old is None:
                    plan["tables"]["new"].append(key)
                elif args.full or old.get("lastModified") != modified:
                    plan["tables"]["changed"].append(key)
                else:
                    plan["tables"]["unchanged"] += 1
        plan["tables"]["removed"] = sorted(key for key in old_tables if key not in plan["live_tables"])

    out = args.out or default_plan_path(args.workspace)
    write_json(out, plan)
    summary = {k: plan[k] for k in ("new", "changed", "renamed", "stale", "removed")}
    summary["unchanged"] = len(plan["unchanged"])
    if args.tables:
        summary["tables"] = plan["tables"]
    summary["plan_file"] = out
    print(json.dumps(summary, indent=2))


def cmd_commit(args):
    with open(args.plan, encoding="utf-8") as handle:
        plan = json.load(handle)
    state = load_state(plan["state"], plan["workspace"])
    skip = {s.strip() for s in args.skip.split(",")} if args.skip else set()
    stamp = now()
    done = []

    for bucket in ("new", "changed", "renamed", "stale"):
        for entry in plan[bucket]:
            if entry["id"] in skip or entry["name"] in skip:
                continue
            live = plan["live_items"][entry["id"]]
            state["items"][entry["id"]] = {
                "name": live["name"],
                "type": live["type"],
                "fingerprint": live["fingerprint"],
                "repo_folder": live["repo_folder"],
                "documented_at": stamp,
            }
            done.append(entry["name"])
    for entry in plan["removed"]:
        if entry["id"] not in skip and entry["name"] not in skip:
            state["items"].pop(entry["id"], None)
            done.append(f"-{entry['name']}")

    if plan["live_tables"] or plan["tables"]["removed"]:
        for key in plan["tables"]["new"] + plan["tables"]["changed"]:
            if key not in skip:
                state["tables"][key] = {"lastModified": plan["live_tables"][key], "documented_at": stamp}
        for key in plan["tables"]["removed"]:
            if key not in skip:
                state["tables"].pop(key, None)

    state["workspace"]["name"] = plan["workspace"]
    state["updated_at"] = stamp
    if plan["mode"] == "full":
        state["full_scan_at"] = stamp
    write_json(plan["state"], state)
    os.remove(args.plan)
    print(json.dumps({"recorded": done, "skipped": sorted(skip), "state": plan["state"]}, indent=2))


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("plan", help="work out what needs (re)documenting")
    p.add_argument("--workspace", required=True, help="workspace name, exactly as Fabric shows it")
    p.add_argument("--state", required=True, help="path to reference/workspaces/<ws>.state.json")
    p.add_argument("--items-root", help="repo folder holding this workspace's Git-format items")
    p.add_argument("--tables", action="store_true", help="also check lakehouse tables for changes")
    p.add_argument("--full", action="store_true", help="treat every item and table as changed")
    p.add_argument("--only", help="comma-separated item names to refresh (new items are always included)")
    p.add_argument("--max-age-days", type=int, help="re-document items with no change signal after this many days")
    p.add_argument("--out", help="where to write the plan (default: OS temp dir)")
    p.set_defaults(func=cmd_plan)

    c = sub.add_parser("commit", help="record a finished plan in the state file")
    c.add_argument("--plan", required=True, help="plan file printed by `plan`")
    c.add_argument("--skip", help="comma-separated item names, IDs or table keys that were NOT documented")
    c.set_defaults(func=cmd_commit)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
