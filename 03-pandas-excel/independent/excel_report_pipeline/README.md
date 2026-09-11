# Excel Report Pipeline (Independent Project)

This tiny end‑to‑end data‑pipeline demonstrates how a junior engineer would take a **raw CSV sales feed**, **validate** it against a business schema, **clean** common data‑quality issues, **transform** the data into useful aggregates, and finally **export** a polished multi‑sheet Excel workbook.

The project lives under `03-pandas-excel/independent/excel_report_pipeline/` and contains only **executable code** (no NOTES.md). All supporting utilities are imported from the exercises in the same skill, showing how modular, reusable components are wired together.

---

## Directory Layout

```
03-pandas-excel/
├─ independent/
│  └─ excel_report_pipeline/
│     ├─ pipeline.py   # Main script – orchestrates validation → cleaning → report
│     └─ README.md      # You're reading it!
```

---

## How It Works (Step‑by‑Step)

1. **Load raw data** – reads `sample_data/sales_messy.csv`.
2. **Validate** – runs the schema‑driven validator from **3.5 Validation** (`excel_validator.validate`).
   * Returns a `ValidationResult` containing a list of `ValidationError` objects.
   * Errors are **not fatal** – the pipeline continues so you still get a report.
3. **Clean** – calls `clean_messy_dataset.clean` (from **3.2 Cleaning**) which:
   - drops duplicate rows
   - normalises dates, case, and missing values
   - adds a derived `revenue` column
4. **Transform** – builds the monthly summary (`monthly_summary.build_monthly_summary`).
5. **Build Excel** – uses the workbook builder from **3.4 Excel Workbooks** (`build_workbook`).
6. **Error Summary Sheet** – if validation failed, an extra sheet called **Error Summary** is added. It lists the column, rule, human‑readable message, and affected row indices.
7. **Persist** – writes `sample_data/sales_report_with_errors.xlsx` to disk.

---

## Running the Pipeline

```bash
# From the repository root (where the `junior-engineer-learning-track` folder lives):
python 03-pandas-excel/independent/excel_report_pipeline/pipeline.py
```

You will see console output indicating whether validation passed and where the workbook was saved.

---

## Why This Project Matters

* **Separation of concerns** – validation, cleaning, transformation, and reporting each live in their own module. The pipeline simply *orchestrates* them.
* **Reusability** – the same validation rules and cleaning functions are used in the exercises and here, demonstrating how code written for learning can be dropped into a real‑world script.
* **Error transparency** – instead of silently dropping bad rows, the pipeline surfaces a clear *Error Summary* sheet that stakeholders can review.
* **Extensible** – to add more steps (e.g., push the report to S3, send an email, or run additional analytics) you just import the new function and call it in `run_pipeline()`.

---

## Dependencies

The project relies on the libraries already listed in `requirements.txt`:
- `pandas`
- `openpyxl`

Ensure they are installed in your environment before running the script.

---

## Next Steps (Optional Enhancements)

1. **Parameterise file paths** – accept command‑line arguments so the pipeline can be reused with different input files.
2. **Chunked processing** – for millions of rows, read the CSV in chunks, validate each chunk, and append results to the workbook iteratively.
3. **Automated testing** – add unit tests that assert the workbook contains the expected sheets and that the *Error Summary* sheet appears only when validation fails.
4. **CI/CD integration** – make the pipeline part of a GitHub Actions workflow that runs on every push and publishes the Excel report as an artifact.

---

Happy data wrangling!
