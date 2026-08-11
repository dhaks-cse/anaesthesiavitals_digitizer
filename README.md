# Smart Anaesthesia Vitals Digitizer Phase 1

This repository contains the Phase 1 implementation of a camera-based system to digitize vitals from an anaesthesia monitor screen.

## Structure

- `src/avd/` - main package modules
- `profiles/` - monitor profile JSON files
- `tests/` - unit tests and synthetic monitor generator

## Usage

Run calibration:

```bash
git clone <repo>
cd anest_visualdigi
python -m avd.cli calibrate --source video --path input.mp4 --out profiles/example_monitor.json
```

Run the pipeline:

```bash
python -m avd.cli run --source cam --profile profiles/example_monitor.json
```
