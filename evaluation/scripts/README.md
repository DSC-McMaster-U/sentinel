# evaluation/scripts/

The evaluation harness. `run_evaluation.py` runs Sentinel against the fixtures (or reads saved outputs), compares the results with `expected-findings/`, and reports precision, recall, false-positive rate and related metrics.

```bash
python evaluation/scripts/run_evaluation.py --help
```

See [evaluation/README.md](../README.md) for the matching rule and metric definitions. Tests: `backend/tests/unit/test_evaluation_harness.py`.
