<div align="center">

# Anaesthesia Vitals Digitizer

**Turn any anaesthesia monitor into a complete digital record — with a camera.**

No cable into the monitor · No vendor SDK · No workflow change

![Python](https://img.shields.io/badge/python-3.11+-3776AB?logo=python&logoColor=white)
![OpenCV](https://img.shields.io/badge/OpenCV-vision-5C3EE8?logo=opencv&logoColor=white)
![ONNX Runtime](https://img.shields.io/badge/ONNX-INT8%20edge-005CED?logo=onnx&logoColor=white)
![Edge only](https://img.shields.io/badge/inference-100%25%20on--device-1FA97A)
![Phase](https://img.shields.io/badge/phase-1%20complete%20%C2%B7%202%20in%20progress-4A2B8C)

</div>

---

## The problem

```mermaid
flowchart LR
    M["ANAESTHESIA MONITOR<br/>HR · NIBP · SpO2 · EtCO2<br/><b>1 reading / second</b>"]
    A["ANAESTHETIST<br/>managing airway<br/>+ transcribing"]
    P["PAPER CHART<br/><b>1 entry / 5 minutes</b>"]
    G["<b>99.7% of measured data<br/>never reaches the record</b>"]

    M -->|reads| A
    A -->|writes by hand| P
    P --> G

    style M fill:#4A2B8C,stroke:#4A2B8C,color:#fff
    style A fill:#EFEAF8,stroke:#00A3BF,color:#4A2B8C
    style P fill:#EFEAF8,stroke:#E1416A,color:#4A2B8C
    style G fill:#00A3BF,stroke:#00A3BF,color:#fff
```

Documentation competes with clinical care — and during induction, intubation or hypotension it is the documentation that is deferred, precisely when the record matters most. Commercial digitisation needs proprietary monitor interfaces and costs **Rs. 3–10 lakh per theatre**, which no hospital running a mixed monitor fleet will approve.

This project reads what the monitor **already displays**.

> **The device is a documentation aid.** It does not diagnose, does not raise alarms, and does not influence therapy. The monitor remains the sole source of truth for clinical alerts, and the anaesthetist signs every chart before it becomes the record.

---

## How it works

```mermaid
flowchart TD
    S1["Clamp camera unit<br/>on monitor bezel"] --> S2["60-second calibration"]
    S2 --> S3{"Profile exists?"}
    S3 -->|no| S2
    S3 -->|yes| S4["Load brand profile"]
    S4 --> LOOP

    subgraph LOOP["RUNTIME LOOP — 1 Hz, fully on-device"]
        direction LR
        L1["Frame<br/>capture"] --> L2["Rectify<br/>homography"] --> L3["ROI crop<br/>from profile"] --> L4["INT8<br/>digit CNN"] --> L5["Colour tag<br/>by channel"] --> L6["Kalman +<br/>outlier reject"]
    end

    LOOP --> C{"Confidence ≥ threshold?"}
    C -->|no| U["Mark UNVERIFIED<br/>prompt manual entry"]
    C -->|yes| W["Append to case record<br/>encrypted local store"]

    U --> K{"Case still active?"}
    W --> K
    K -->|yes| LOOP
    K -->|no| E["Auto-close case<br/>probe off + screen idle"]

    E --> O1["PDF chart"]
    E --> O2["CSV dataset"]
    E --> O3["FHIR / HL7 → HIS"]

    style S1 fill:#4A2B8C,stroke:#4A2B8C,color:#fff
    style S2 fill:#4A2B8C,stroke:#4A2B8C,color:#fff
    style S4 fill:#00A3BF,stroke:#00A3BF,color:#fff
    style LOOP fill:#EFEAF8,stroke:#4A2B8C
    style C fill:#00A3BF,stroke:#00A3BF,color:#fff
    style K fill:#00A3BF,stroke:#00A3BF,color:#fff
    style U fill:#FDF0F4,stroke:#E1416A,color:#4A2B8C
    style W fill:#1FA97A,stroke:#1FA97A,color:#fff
    style E fill:#4A2B8C,stroke:#4A2B8C,color:#fff
    style O1 fill:#EFEAF8,stroke:#00A3BF,color:#4A2B8C
    style O2 fill:#EFEAF8,stroke:#00A3BF,color:#4A2B8C
    style O3 fill:#EFEAF8,stroke:#00A3BF,color:#4A2B8C
```

### Two decisions carry all the weight

| | |
|---|---|
| **Profile-driven layout** | Each monitor model is a JSON file describing where each parameter sits on screen. Supporting a new brand is a **60-second calibration**, not a new model and not new code. |
| **Confidence gating** | A reading is rejected if it breaks the plausible range, the expected colour channel, or the rate-of-change limit. Rejected intervals are marked `unverified` and referred for manual entry. **The system never guesses a value.** |

---

## Architecture

```mermaid
flowchart TB
    CAP["<b>CAPTURE LAYER</b><br/>5 MP global-shutter camera · IR-cut · polariser · bezel clamp"]
    EDGE["<b>EDGE COMPUTE</b> — RK3588 / Orin Nano class, offline<br/>vision pipeline → plausibility filter → Kalman"]
    DATA["<b>DATA LAYER</b><br/>AES-256 encrypted SQLite · RBAC · full audit trail · no cloud"]
    APP["<b>APPLICATION LAYER</b><br/>live chart · event annotation · anaesthetist sign-off"]
    X["PDF · CSV · FHIR / HL7"]

    CAP --> EDGE --> DATA --> APP --> X

    style CAP fill:#00A3BF,stroke:#00A3BF,color:#fff
    style EDGE fill:#EFEAF8,stroke:#4A2B8C,color:#4A2B8C
    style DATA fill:#4A2B8C,stroke:#4A2B8C,color:#fff
    style APP fill:#00A3BF,stroke:#00A3BF,color:#fff
    style X fill:#EFEAF8,stroke:#4A2B8C,color:#4A2B8C
```

---

## Quick start

```bash
git clone https://github.com/dhaks-cse/anaesthesiavitals_digitizer.git
cd anaesthesiavitals_digitizer

python -m venv .venv && source .venv/bin/activate    # Windows: .venv\Scripts\activate
pip install -e ".[dev]"

export AVD_DB_KEY="your-key-here"
```

| Task | Command |
|---|---|
| **Calibrate** a monitor | `avd calibrate --source 0 --out profiles/my_monitor.json` |
| **Run** the pipeline | `avd run --source 0 --profile profiles/my_monitor.json` |
| **Annotate** an event | `avd event add --case 12 --category drug --label "Propofol 120 mg"` |
| **Export** a chart | `avd export --case 12 --format pdf --out charts/case_012.pdf` |
| **Replay** vs ground truth | `avd replay --video bench_01.mp4 --profile p.json --truth truth.csv` |

Every command accepts a webcam index, a video file or an image directory as `--source`, so the whole system runs on a laptop with no hardware.

---

## Project layout

```
src/avd/
├── capture/      frame sources: webcam · video file · image directory
├── calibrate/    interactive ROI selection → brand profile
├── vision/       rectify · roi_extract · digit_recognize · colour_tag
├── filter/       plausibility checks · Kalman smoothing
├── store/        SQLAlchemy models · encrypted local database
└── cli.py        Typer entrypoints
profiles/         per-monitor JSON layout profiles
tests/            unit tests + synthetic monitor generator
```

---

## Monitor profile format

```json
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
```

A new hospital, a new monitor brand, a new theatre — all of it is one more file in `profiles/`.

---

## Roadmap

| Window | Phase | Scope |
|---|---|---|
| 0–3 months | **Phase 1** ✅ | Capture, calibration, recognition skeleton, storage |
| 3–9 months | **Phase 2** 🚧 | Case lifecycle, events, PDF, FHIR, trained model |
| 9–15 months | **Phase 3** | Clinical shadow-mode trial, 2 partner hospitals |
| 15–24 months | **Phase 4** | IEC 62304, ISO 13485, CDSCO Class A filing |

---

## Validation targets

| Metric | Target |
|---|---|
| Numeric read accuracy | **≥ 98%** per parameter |
| Chart completeness | **100%** of case duration |
| Monitor models supported | **4** |
| Fabricated values | **0** — flagged, never guessed |

The replay harness is the regression gate. Accuracy is measured on every commit and must not drop.

---

## Data handling

All inference runs locally on the edge device. No frames are retained, no data leaves the hospital, and there is no network dependency at runtime. The database is encrypted at rest, access is role-based, and every read, export and sign-off is written to an audit log. Key material is supplied through the environment and is never committed.

---

## Development

```bash
pytest          # runs against a synthetic monitor generator — no real footage needed
ruff check .
mypy src
```

---

## Regulatory position

Adopted from the prototype stage rather than retrofitted before filing:

`IEC 62304` software lifecycle · `ISO 13485` QMS · `CDSCO Class A` under Medical Device Rules 2017 · `HL7 v2 ORU` and `FHIR Observation` for HIS interoperability

---

<div align="center">

Developed for **MEDHA MEDITHON 2026** — organised by Leelatai Kulkarni Memorial Hospital & Research Center,
in association with BETiC (IIT Bombay), V3 Foundation (VNIT Nagpur) and BETiC–GHRCE Nagpur.

</div>
