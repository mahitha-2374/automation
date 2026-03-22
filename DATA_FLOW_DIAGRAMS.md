# Architecture & Data Flow Diagrams

## System Component Diagram

```
┌──────────────────────────────────────────────────────────┐
│            USER INTERFACES                               │
├──────────────────────────────────────────────────────────┤
│                                                           │
│    ┌─────────────────┐        ┌──────────────────┐      │
│    │  Streamlit UI   │        │    CLI Tool      │      │
│    │   (app.py)      │        │  (main.py)       │      │
│    └────────┬────────┘        └────────┬─────────┘      │
│             │                          │                │
└─────────────┼──────────────────────────┼────────────────┘
              │                          │
              └──────────────┬───────────┘
                             │
                    ┌────────▼────────┐
                    │  Data Inputs    │
                    │  • users.csv    │
                    │  • roles.csv    │
                    └────────┬────────┘
                             │
        ┌────────────────────┼────────────────────┐
        │                    │                    │
    ┌───▼────┐          ┌────▼────┐         ┌────▼────┐
    │   GSI  │          │Adaptive │         │Template │
    │Manager │          │ Engine  │         │Manager  │
    └───┬────┘          └────┬────┘         └────┬────┘
        │                    │                    │
        └────────────────────┼────────────────────┘
                             │
                    ┌────────▼────────┐
                    │ Export Manager  │
                    └────────┬────────┘
                             │
        ┌────────────────────┼────────────────────┐
        │                    │                    │
    ┌───▼──────┐        ┌────▼─────┐        ┌───▼───┐
    │ Excel    │        │   Word   │        │ PDF   │
    │Generator │        │Generator │        │Gen    │
    └───┬──────┘        └────┬─────┘        └───┬───┘
        │                    │                   │
        └────────────────────┼───────────────────┘
                             │
                    ┌────────▼────────┐
                    │  Output Files   │
                    │  output/        │
                    │  ├─ *.xlsx      │
                    │  ├─ *.docx      │
                    │  └─ *.pdf       │
                    └─────────────────┘
```

## GSI-Based Data Flow

```
CSV Export
  ↓
┌─────────────────────────────────────┐
│     GSI AUTO-DETECT                 │
│  Looks for: gsi, app, system,      │
│  application, enterprise columns    │
└────────────────────┬────────────────┘
                     ↓
┌─────────────────────────────────────┐
│   GSI DATA EXTRACTION               │
│  • User data grouped by GSI         │
│  • Role data grouped by GSI         │
│  • Statistics per GSI               │
└────────────────────┬────────────────┘
                     ↓
┌─────────────────────────────────────┐
│   GSI FILTERING                     │
│  • Filter users by GSI ID           │
│  • Filter roles by GSI ID           │
│  • Get GSI-specific data            │
└────────────────────┬────────────────┘
                     ↓
           Enriched GSI Data
```

## Template Selection Workflow

```
┌─────────────────────────────────────────────────────┐
│         TEMPLATE REGISTRY                           │
│  • T3_Standard (Excel)                              │
│  • OLA_Standard (Word)                              │
│  • Executive_Summary (PDF)                          │
│  • Detailed_Report (PDF)                            │
│  • IAM_Audit (Excel)                                │
└─────────────────────────────────────────────────────┘
       ↑                ↑                  ↑
       │                │                  │
   ┌───┴────┐    ┌──────┴───┐    ┌───────┴────┐
   │Single  │    │Multiple  │    │ All GSI-   │
   │Template│    │Templates │    │ Aware      │
   └────────┘    └──────────┘    └────────────┘
       │                │                  │
       └────────────────┼──────────────────┘
                        │
              Export per Template
```

## Output Generation Timeline

```
User Initiates Export
         ↓
[100ms] Parse Configuration
         ↓
[50ms]  Load Templates
         ↓
┌─────────────────────────────┐
│  FOR EACH TEMPLATE          │
│                             │
│  [500-2000ms] Generate      │
│  • Excel: Fill sheets       │
│  • Word: Populate template  │
│  • PDF: Render report       │
└─────────────────────────────┘
         ↓
[500-1500ms] Optional Audit Trail
         ↓
[100ms] Create Summary
         ↓
Display Results & Download Buttons

Total: 3-15 seconds (varies by dataset size)
```

## Export Manager State Flow

```
START EXPORT
     │
     ├─ Validate GSI ID
     ├─ Load Template Registry
     ├─ Prepare GSI Data
     │  ├─ Extract GSI-specific records
     │  ├─ Add metadata
     │  └─ Merge with processing results
     │
     ├─ SELECT EXPORT MODE
     │  │
     │  ├─ Mode=Single
     │  │  └─ Single export
     │  │
     │  ├─ Mode=Multiple
     │  │  └─ Multiple exports
     │  │
     │  ├─ Mode=All-GSI-Aware
     │  │  └─ All templates
     │  │
     │  └─ Mode=By-Format
     │     └─ All in format
     │
     ├─ GENERATE FILES
     │  ├─ Create output files
     │  ├─ Track results
     │  └─ Handle errors
     │
     ├─ OPTIONAL: Generate Audit Trail
     │
     └─ RETURN RESULTS
        ├─ File list
        ├─ Status info
        └─ Summary
```
