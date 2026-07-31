#!/usr/bin/env python3
"""Tests for build_topology.py. Stdlib unittest, run with:

    python3 tests/test_build_topology.py
"""

import json
import subprocess
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "scripts" / "build_topology.py"
EXAMPLE = ROOT / "reference" / "examples" / "small-office.json"

MINIMAL = {
    "pages": [{
        "name": "P1",
        "zones": [{"id": "z", "label": "Zone", "nodes": ["a", "b"]}],
    }],
    "nodes": [
        {"id": "a", "icon": "router", "label": "R"},
        {"id": "b", "icon": "switch", "label": "S"},
    ],
    "links": [{"from": "a", "to": "b", "fromPort": "Gi1", "toPort": "Gi2"}],
}


def run(spec: dict):
    """Build a spec, returning (returncode, stdout, stderr, output_text)."""
    with tempfile.TemporaryDirectory() as tmp:
        spec_path = Path(tmp) / "spec.json"
        out_path = Path(tmp) / "out.drawio"
        spec_path.write_text(json.dumps(spec))
        proc = subprocess.run(
            [sys.executable, str(SCRIPT), str(spec_path), "-o", str(out_path)],
            capture_output=True, text=True,
        )
        text = out_path.read_text() if out_path.exists() else ""
        return proc.returncode, proc.stdout, proc.stderr, text


def mutate(**changes) -> dict:
    spec = json.loads(json.dumps(MINIMAL))
    spec.update(changes)
    return spec


class TestValidation(unittest.TestCase):
    """Every one of these must fail loudly rather than emit a wrong diagram."""

    def assert_spec_error(self, spec, fragment):
        code, _, err, _ = run(spec)
        self.assertEqual(code, 2, f"expected exit 2, got {code}\n{err}")
        self.assertIn("spec error", err)
        self.assertIn(fragment, err)

    def test_link_to_unknown_node(self):
        spec = mutate(links=[{"from": "a", "to": "ghost"}])
        self.assert_spec_error(spec, "ghost")

    def test_duplicate_node_id(self):
        spec = mutate(nodes=MINIMAL["nodes"] + [{"id": "a", "icon": "pc", "label": "dup"}])
        self.assert_spec_error(spec, "duplicate node id")

    def test_zone_lists_unknown_node(self):
        spec = json.loads(json.dumps(MINIMAL))
        spec["pages"][0]["zones"][0]["nodes"].append("nope")
        self.assert_spec_error(spec, "nope")

    def test_node_never_placed(self):
        spec = mutate(nodes=MINIMAL["nodes"] + [{"id": "c", "icon": "pc", "label": "C"}])
        self.assert_spec_error(spec, "never placed")

    def test_node_placed_twice(self):
        spec = json.loads(json.dumps(MINIMAL))
        spec["pages"][0]["zones"].append(
            {"id": "z2", "label": "Zone 2", "nodes": ["a"]}
        )
        self.assert_spec_error(spec, "more than one zone")


class TestOutput(unittest.TestCase):

    def test_minimal_spec_is_valid_xml(self):
        code, _, _, text = run(MINIMAL)
        self.assertEqual(code, 0)
        root = ET.fromstring(text)
        self.assertEqual(root.tag, "mxfile")
        self.assertEqual([d.get("name") for d in root.findall("diagram")], ["P1"])

    def test_edge_carries_both_port_labels(self):
        _, _, _, text = run(MINIMAL)
        root = ET.fromstring(text)
        labels = [c.get("value") for c in root.iter("mxCell")
                  if c.get("style", "").startswith("edgeLabel")]
        self.assertIn("Gi1", labels)
        self.assertIn("Gi2", labels)

    def test_icons_are_embedded_not_referenced(self):
        _, _, _, text = run(MINIMAL)
        self.assertIn("image=data:image/png,", text)
        self.assertNotIn("assets/icons/", text)

    def test_unknown_icon_warns_but_still_builds(self):
        spec = mutate(nodes=[
            {"id": "a", "icon": "definitely-not-a-real-device", "label": "R"},
            {"id": "b", "icon": "switch", "label": "S"},
        ])
        code, _, err, text = run(spec)
        self.assertEqual(code, 0, "an unknown icon must not fail the build")
        self.assertIn("definitely-not-a-real-device", err)
        ET.fromstring(text)

    def test_count_and_badges_render(self):
        spec = mutate(nodes=[
            {"id": "a", "icon": "router", "label": "R"},
            {"id": "b", "icon": "laptop", "label": "Laptops",
             "count": 12, "badges": ["VLAN 20"]},
        ])
        _, _, _, text = run(spec)
        # Read the attribute back through the parser: the file itself stores
        # this double-escaped (&amp;#215;) because the label is HTML inside XML.
        values = [c.get("value", "") for c in ET.fromstring(text).iter("mxCell")]
        caption = next(v for v in values if "Laptops" in v)
        self.assertIn("&#215;&#160;12", caption)
        self.assertIn("VLAN 20", caption)

    def test_legend_page_only_when_requested(self):
        _, _, _, text = run(MINIMAL)
        self.assertEqual(len(ET.fromstring(text).findall("diagram")), 1)

        spec = mutate(legend={"title": "Key", "assumptions": ["1 — guessed"]})
        _, _, _, text = run(spec)
        names = [d.get("name") for d in ET.fromstring(text).findall("diagram")]
        self.assertEqual(names, ["P1", "Legend"])

    def test_legend_lists_each_colour_once(self):
        spec = mutate(
            links=[
                {"from": "a", "to": "b", "color": "#DC2626", "meaning": "WAN"},
                {"from": "b", "to": "a", "color": "#DC2626", "meaning": "WAN"},
            ],
            legend={"title": "Key"},
        )
        _, _, _, text = run(spec)
        self.assertEqual(text.count(">WAN<") + text.count('value="WAN"'), 1)


class TestIconResolution(unittest.TestCase):

    def setUp(self):
        sys.path.insert(0, str(ROOT / "scripts"))
        import build_topology
        self.icons = build_topology.IconLibrary()

    def test_exact_slug(self):
        self.assertEqual(self.icons.resolve("firewall"), "firewall")

    def test_alias(self):
        self.assertEqual(self.icons.resolve("l3-switch"), "layer-3-switch")
        self.assertEqual(self.icons.resolve("ap"), "accesspoint")

    def test_spaces_and_case_normalise(self):
        self.assertEqual(self.icons.resolve("Layer 3 Switch"), "layer-3-switch")

    def test_token_fallback(self):
        self.assertEqual(self.icons.resolve("atm switch"), "atm-switch")

    def test_no_match_returns_none(self):
        self.assertIsNone(self.icons.resolve("quantum-flux-capacitor"))


class TestExample(unittest.TestCase):

    def test_shipped_example_builds_clean(self):
        spec = json.loads(EXAMPLE.read_text())
        code, out, err, text = run(spec)
        self.assertEqual(code, 0, err)
        self.assertNotIn("WARNING", err, f"example should resolve every icon:\n{err}")
        names = [d.get("name") for d in ET.fromstring(text).findall("diagram")]
        self.assertEqual(names, ["Office", "Legend"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
