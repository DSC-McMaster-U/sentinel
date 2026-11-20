# evaluation/expected-findings/

Labelled expected findings for each fixture, named after the fixture (`<name>.json` for `fixtures/<safe|risky>/<name>.json`). Each file holds `fixture`, `label`, `summary` and a `findings` list of `SecurityFinding` objects (`backend/app/schemas/finding.py`). Safe fixtures expect an empty findings list.

Evidence line numbers refer to the new side of the fixture's diff. See [evaluation/README.md](../README.md#expected-findings-format) for the format and the rules `--check-fixtures` enforces.
