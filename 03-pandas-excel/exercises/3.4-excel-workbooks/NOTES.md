# 3.4 Excel Workbooks

openpyxl is the Python library for reading and writing `.xlsx` files at the worksheet level — you control individual cells, styles, and sheet structure. pandas has a built-in `to_excel()` shortcut, but openpyxl gives you full control over formatting.

---

## Core Methods Used Here

| Method | Purpose |
|---|---|
| `openpyxl.Workbook()` | Create a new in-memory workbook |
| `wb.create_sheet("Name")` | Add a named worksheet |
| `wb.remove(wb.active)` | Delete the default blank sheet that every new Workbook creates |
| `wb.save("path.xlsx")` | Write the workbook to disk |
| `ws.cell(row, column, value)` | Write a value to a specific cell |
| `ws.freeze_panes = "A2"` | Lock row 1 (header) so it stays visible when scrolling |
| `ws.column_dimensions["A"].width` | Set column width |
| `Font(bold=True, color="FFFFFF")` | Style: bold white text |
| `PatternFill(start_color=hex, fill_type="solid")` | Style: solid background colour |
| `Alignment(horizontal="center")` | Cell alignment |
| `cell.number_format = '#,##0.00'` | Apply a currency/number display format |
| `get_column_letter(n)` | Convert column integer index (1-based) to letter (A, B, …) |

---

## Key Ideas

**pandas `to_excel()` vs openpyxl directly**: `df.to_excel("file.xlsx")` is fine for dumping data quickly, but it gives you no control over formatting, multiple sheets, or cell-level structure. For production reports (styled headers, frozen panes, multi-sheet workbooks), write directly with openpyxl.

**Number formats are display-only.** `cell.number_format = '#,##0.00'` tells Excel how to render the number — the underlying value stored in the cell is still a plain Python float. Don't confuse display format with the actual value.

**Freeze panes.** `ws.freeze_panes = "A2"` means "freeze everything above and to the left of A2" — i.e., row 1. This makes header rows stay visible as you scroll down.

**numpy scalar types.** When iterating rows from a pandas DataFrame, numeric values may be numpy scalars (`np.int64`, `np.float64`). openpyxl prefers Python native types — call `.item()` on numpy scalars before writing them to avoid serialization issues.

---

## What was built here

`build_excel_report.py` produces `sales_report.xlsx` with three sheets: Raw Sales (cleaned data), Monthly (groupby summary), and Category Pivot (category × month revenue matrix). Every sheet has a styled dark-blue header row, freeze panes, zebra-stripe rows, currency formatting on money columns, and auto-fitted column widths.
