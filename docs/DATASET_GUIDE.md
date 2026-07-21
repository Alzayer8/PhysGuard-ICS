# Preparing a dataset

Create three UTF-8 CSV files with unique, strictly increasing timestamps:

- `train.csv`: normal baseline telemetry.
- `validation.csv`: separate normal baseline telemetry.
- `test.csv`: telemetry to analyze; an optional `attack` column may be included for
  demonstration metrics.

Required columns:

| Column | Meaning | Constraint |
|---|---|---|
| `timestamp` | Sample time | Parseable datetime, increasing and unique |
| `inlet_flow` | Inlet flow | Finite number |
| `outlet_flow` | Outlet flow | Finite number |
| `tank_level` | Level measurement | Finite number |
| `pressure` | Pressure measurement | Finite number |
| `inlet_valve` | Valve state | `0` or `1` |
| `outlet_pump` | Pump state | `0` or `1` |
| `attack` | Optional reference label | `0` or `1` |

Train and validation must contain only normal rows when `attack` is supplied. Adapt the
column meanings, units, thresholds, and topology to your authorized system before drawing
any conclusion. The defaults in `configs/example.yaml` exist only for the artificial toy
dataset.

Current validation checks ordering and uniqueness within each CSV. Users must
also ensure that train ends before validation begins and validation ends before
test begins; cross-split non-overlap is not currently enforced automatically.

Validate without creating an experiment:

```bash
physguard validate --train train.csv --validation validation.csv --test test.csv
```
