"""Tests for skills/brain/document-fabric-workspace/scripts/workspace_state.py.

A fake `fab` on PATH answers `fab ls` from a JSON fixture and logs every call,
so the tests also prove the script never runs anything but `fab ls`.
"""

import json
import os
import subprocess
import sys
import tempfile
import textwrap
import unittest

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPT = os.path.join(REPO, "skills", "brain", "document-fabric-workspace", "scripts", "workspace_state.py")

FAKE_FAB = textwrap.dedent(
    """\
    #!/usr/bin/env python3
    import json, os, sys
    with open(os.environ["FAKE_FAB_LOG"], "a") as log:
        log.write(json.dumps(sys.argv[1:]) + "\\n")
    if sys.argv[1] != "ls":
        print("fake fab: only ls is simulated"); sys.exit(1)
    path = sys.argv[2]
    fixture = json.load(open(os.environ["FAKE_FAB_FIXTURE"]))
    if path not in fixture:
        print(f"x ls: [NotFound] {path}"); sys.exit(1)
    print(json.dumps({"status": "Success", "result": {"data": fixture[path]}}))
    """
)

WS = "Sales-DEV"
LAKEHOUSE_ID = "11111111-0000-0000-0000-000000000001"
NOTEBOOK_ID = "11111111-0000-0000-0000-000000000002"
PIPELINE_ID = "11111111-0000-0000-0000-000000000003"


def base_fixture():
    return {
        f"{WS}.Workspace": [
            {"name": "lh_bronze.Lakehouse", "id": LAKEHOUSE_ID},
            {"name": "nb_load_bronze.Notebook", "id": NOTEBOOK_ID},
            {"name": "pl_ingest_bronze_webshop.DataPipeline", "id": PIPELINE_ID},
        ],
        f"{WS}.Workspace/lh_bronze.Lakehouse/Tables": [{"name": "webshop", "lastModified": "t0"}],
        f"{WS}.Workspace/lh_bronze.Lakehouse/Tables/webshop": [
            {"name": "orders", "lastModified": "t1"},
            {"name": "customers", "lastModified": "t1"},
        ],
    }


class WorkspaceStateTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        bin_dir = os.path.join(self.tmp, "bin")
        os.makedirs(bin_dir)
        fab = os.path.join(bin_dir, "fab")
        with open(fab, "w") as handle:
            handle.write(FAKE_FAB)
        os.chmod(fab, 0o755)
        self.fixture_path = os.path.join(self.tmp, "fixture.json")
        self.log = os.path.join(self.tmp, "fab.log")
        self.state = os.path.join(self.tmp, "reference", "workspaces", f"{WS}.state.json")
        self.plan_file = os.path.join(self.tmp, "plan.json")
        self.env = dict(os.environ, PATH=bin_dir + os.pathsep + os.environ["PATH"],
                        FAKE_FAB_FIXTURE=self.fixture_path, FAKE_FAB_LOG=self.log)
        self.write_fixture(base_fixture())

    def write_fixture(self, fixture):
        with open(self.fixture_path, "w") as handle:
            json.dump(fixture, handle)

    def run_script(self, *args):
        proc = subprocess.run([sys.executable, SCRIPT, *args], capture_output=True, text=True, env=self.env)
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        return json.loads(proc.stdout)

    def plan(self, *extra):
        return self.run_script("plan", "--workspace", WS, "--state", self.state, "--out", self.plan_file, *extra)

    def commit(self, *extra):
        return self.run_script("commit", "--plan", self.plan_file, *extra)

    def names(self, entries):
        return sorted(entry["name"] for entry in entries)

    def test_first_run_documents_everything_then_nothing(self):
        first = self.plan("--tables")
        self.assertEqual(self.names(first["new"]), ["lh_bronze", "nb_load_bronze", "pl_ingest_bronze_webshop"])
        self.assertEqual(sorted(first["tables"]["new"]), ["lh_bronze/webshop/customers", "lh_bronze/webshop/orders"])
        self.commit()
        self.assertFalse(os.path.exists(self.plan_file))

        second = self.plan("--tables")
        for bucket in ("new", "changed", "renamed", "stale", "removed"):
            self.assertEqual(second[bucket], [], bucket)
        self.assertEqual(second["unchanged"], 3)
        self.assertEqual(second["tables"]["unchanged"], 2)

    def test_rename_is_detected_by_id(self):
        self.plan(); self.commit()
        fixture = base_fixture()
        fixture[f"{WS}.Workspace"][1]["name"] = "nb_load_bronze_v2.Notebook"
        self.write_fixture(fixture)
        result = self.plan()
        self.assertEqual(self.names(result["renamed"]), ["nb_load_bronze_v2"])
        self.assertEqual(result["renamed"][0]["reason"], "was nb_load_bronze")
        self.assertEqual(result["new"], [])

    def test_removed_item(self):
        self.plan(); self.commit()
        fixture = base_fixture()
        fixture[f"{WS}.Workspace"].pop(2)
        self.write_fixture(fixture)
        result = self.plan()
        self.assertEqual(self.names(result["removed"]), ["pl_ingest_bronze_webshop"])
        self.commit()
        with open(self.state) as handle:
            self.assertNotIn(PIPELINE_ID, json.load(handle)["items"])

    def test_repo_definition_change_is_detected(self):
        items = os.path.join(self.tmp, "fabric")
        nb = os.path.join(items, "nb_load_bronze.Notebook")
        os.makedirs(nb)
        with open(os.path.join(nb, ".platform"), "w") as handle:
            json.dump({"metadata": {"type": "Notebook", "displayName": "nb_load_bronze"}}, handle)
        with open(os.path.join(nb, "notebook-content.py"), "w") as handle:
            handle.write("print(1)\n")
        self.plan("--items-root", items); self.commit()
        self.assertEqual(self.plan("--items-root", items)["changed"], [])

        with open(os.path.join(nb, "notebook-content.py"), "w") as handle:
            handle.write("print(2)\n")
        result = self.plan("--items-root", items)
        self.assertEqual(self.names(result["changed"]), ["nb_load_bronze"])
        self.assertEqual(result["changed"][0]["reason"], "repo definition changed")

    def test_items_without_change_signal_go_stale(self):
        self.plan(); self.commit()
        with open(self.state) as handle:
            state = json.load(handle)
        state["items"][LAKEHOUSE_ID]["documented_at"] = "2020-01-01T00:00:00+00:00"
        with open(self.state, "w") as handle:
            json.dump(state, handle)
        result = self.plan()
        self.assertEqual(self.names(result["stale"]), ["lh_bronze"])

    def test_only_refreshes_named_items(self):
        self.plan(); self.commit()
        result = self.plan("--only", "nb_load_bronze")
        self.assertEqual(self.names(result["changed"]), ["nb_load_bronze"])
        self.assertEqual(result["unchanged"], 2)

    def test_skip_leaves_item_pending(self):
        self.plan()
        self.commit("--skip", "pl_ingest_bronze_webshop")
        result = self.plan()
        self.assertEqual(self.names(result["new"]), ["pl_ingest_bronze_webshop"])

    def test_table_changes(self):
        self.plan("--tables"); self.commit()
        fixture = base_fixture()
        fixture[f"{WS}.Workspace/lh_bronze.Lakehouse/Tables/webshop"] = [
            {"name": "orders", "lastModified": "t2"},
            {"name": "returns", "lastModified": "t2"},
        ]
        self.write_fixture(fixture)
        result = self.plan("--tables")["tables"]
        self.assertEqual(result["changed"], ["lh_bronze/webshop/orders"])
        self.assertEqual(result["new"], ["lh_bronze/webshop/returns"])
        self.assertEqual(result["removed"], ["lh_bronze/webshop/customers"])

    def test_lakehouse_without_schemas(self):
        fixture = base_fixture()
        fixture[f"{WS}.Workspace/lh_bronze.Lakehouse/Tables"] = [
            {"name": "orders", "lastModified": "t1"},
        ]
        fixture[f"{WS}.Workspace/lh_bronze.Lakehouse/Tables/orders"] = [{"name": "_delta_log"}]
        del fixture[f"{WS}.Workspace/lh_bronze.Lakehouse/Tables/webshop"]
        self.write_fixture(fixture)
        self.assertEqual(self.plan("--tables")["tables"]["new"], ["lh_bronze/orders"])

    def test_only_fab_ls_is_ever_called(self):
        self.plan("--tables"); self.commit(); self.plan("--tables", "--full")
        with open(self.log) as handle:
            calls = [json.loads(line) for line in handle]
        self.assertTrue(calls)
        self.assertTrue(all(call[0] == "ls" for call in calls), calls)


if __name__ == "__main__":
    unittest.main()
