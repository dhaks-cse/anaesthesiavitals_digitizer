![Uploading image.png…]()
Anaesthesia Vitals Digitizer

A retrofit, camera-based system that reads vital signs from an existing anaesthesia monitor screen and generates a complete, timestamped digital anaesthesia record — without any cable into the monitor, any vendor SDK, or any change to theatre workflow.

Most operating theatres in India still maintain the anaesthesia chart on paper. At roughly five-minute intervals the anaesthetist reads the monitor and transcribes heart rate, blood pressure, oxygen saturation and end-tidal CO2 by hand, while simultaneously managing the airway and the patient. Documentation therefore competes with clinical care, and it is the documentation that is deferred during induction, intubation or an episode of hypotension — precisely when the record carries the most weight. Commercial digitisation depends on proprietary monitor interfaces and typically costs Rs. 3–10 lakh per theatre, which is not viable for a hospital running a mixed fleet of monitors. This project reads what the monitor already displays, using a clip-on camera and an edge compute device, and is designed to be affordable for small and medium hospitals.

The device is a documentation aid. It does not diagnose, does not raise alarms, and does not influence therapy. The monitor remains the sole source of truth for clinical alerts, and the anaesthetist reviews and signs every generated chart before it becomes the record.

Status

Phase 1 — implemented. Frame capture, screen rectification, monitor profile format, interactive calibration, digit recognition interface, plausibility filtering, and encrypted local storage.

Phase 2 — in progress. Case lifecycle detection, event annotation, PDF chart rendering, CSV/FHIR export, access control and audit logging, trained recognition model, replay regression harness.

How it works
Camera → Rectify (homography) → ROI crop (from brand profile) → Digit CNN (INT8)
       → Colour-channel tagging → Plausibility filter + Kalman smoothing
       → Encrypted local store → PDF chart / CSV / FHIR

Two design decisions carry most of the weight:

Profile-driven layout. Each monitor model is described by a JSON profile giving the canonical screen size and, for every parameter, its region of interest, expected colour, plausible range and digit count. Supporting a new brand is a sixty-second calibration that produces a configuration file — not a new engineering effort, and not a new model.

Confidence gating. A reading is rejected if it falls outside the profile's bounds, if the region's dominant colour does not match the expected channel, or if the rate of change from the last accepted value is implausible. Rejected intervals are stored and rendered as unverified and referred for manual entry. The system never substitutes an estimated value.

Installation

Requires Python 3.11+.

bash
git clone https://github.com/dhaks-cse/anaesthesiavitals_digitizer.git
cd anaesthesiavitals_digitizer

python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

pip install -e ".[dev]"

Set the database encryption key before first run:

bash
export AVD_DB_KEY="your-key-here"
Usage

Calibrate a monitor — capture a frame, draw a region for each parameter, and write a reusable brand profile:

bash
avd calibrate --source 0 --out profiles/my_monitor.json
avd calibrate --source footage/theatre_2.mp4 --out profiles/bpl_ultima.json

Run the pipeline — reads at 1 Hz and prints a live table, flagging anything unverified:

bash
avd run --source 0 --profile profiles/my_monitor.json
avd run --source footage/case_017.mp4 --profile profiles/bpl_ultima.json

Annotate an event during a case:

bash
avd event add --case 12 --category drug --label "Propofol 120 mg"

Export the record:

bash
avd export --case 12 --format pdf   --out charts/case_012.pdf
avd export --case 12 --format csv   --out exports/case_012.csv
avd export --case 12 --format fhir  --out exports/case_012.json

Replay against ground truth — the regression gate; accuracy must not drop between commits:

bash
avd replay --video footage/bench_01.mp4 \
           --profile profiles/bpl_ultima.json \
           --truth footage/bench_01_truth.csv
Project layout
src/avd/
  capture/      frame sources: webcam, video file, image directory
  calibrate/    interactive ROI selection and profile creation
  vision/       rectify · roi_extract · digit_recognize · colour_tag
  filter/       plausibility checks and Kalman smoothing
  store/        SQLAlchemy models and encrypted local database
  cli.py        Typer entrypoints
profiles/       per-monitor JSON layout profiles
tests/          unit tests and synthetic monitor generator
Monitor profile format
json
{
  "name": "example_anaesthesia_monitor",
  "canonical_width": 1280,
  "canonical_height": 720,
  "parameters": [
    {
      "name": "HR",
      "unit": "bpm",
      "roi": [920, 120, 220, 120],
      "expected_colour": "green",
      "min": 30,
      "max": 180,
      "digits": 3,
      "max_delta_per_sec": 20
    }
  ]
}
Data handling

All inference runs locally on the edge device. No frames are retained, no data leaves the hospital, and the system has no network dependency at runtime. The database is encrypted at rest, access is role-based, and every read, export and sign-off is written to an audit log. Key material is supplied through the environment and is never committed.

Development
bash
pytest              # tests run against a synthetic monitor generator — no real footage needed
ruff check .
mypy src

Tests generate their own monitor screens (coloured numerals on black), so the suite runs on any machine without theatre recordings.

Regulatory position

Adopted from the prototype stage rather than retrofitted before filing:

IEC 62304 software lifecycle
ISO 13485 quality management system
CDSCO Class A submission under the Medical Device Rules 2017, as a low-risk documentation aid
HL7 v2 ORU and FHIR Observation profiles for hospital information system interoperability
Validation targets
Metric	Target
Numeric read accuracy	≥ 98% per parameter
Chart completeness	100% of case duration
Monitor models supported	4
Fabricated values	0 — flagged, never guessed
Acknowledgements

Developed for MEDHA MEDITHON 2026, organised by Leelatai Kulkarni Memorial Hospital & Research Center in association with BETiC (IIT Bombay), V3 Foundation (VNIT Nagpur) and BETiC–GHRCE Nagpur.
