import csv

# reads sales data from csv and computes revenue and top-selling product
def generate_sales_report(csv_filepath, report_filepath):
    total_revenue = 0.0
    row_count = 0
    best_seller_name = ""
    highest_qty = 0
    
    with open(csv_filepath, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        header = next(reader, None)  # skip header
        
        for row in reader:
            if not row or len(row) < 3:
                continue
            name = row[0].strip()
            qty = int(row[1].strip())
            price = float(row[2].strip())
            
            row_count += 1
            revenue = qty * price
            total_revenue += revenue
            
            if qty > highest_qty:
                highest_qty = qty
                best_seller_name = name
                
    # write formatted text report
    with open(report_filepath, "w", encoding="utf-8") as f:
        f.write("=== Sales Performance Report ===\n")
        f.write(f"Total rows processed: {row_count}\n")
        f.write(f"Total revenue:        ${total_revenue:,.2f}\n")
        f.write(f"Best-selling item:    {best_seller_name} ({highest_qty} units sold)\n")
        
    return {
        "rows": row_count,
        "revenue": round(total_revenue, 2),
        "best_seller": best_seller_name,
        "highest_qty": highest_qty
    }

if __name__ == "__main__":
    csv_file = "sample_data.csv"
    report_file = "report.txt"
    
    summary = generate_sales_report(csv_file, report_file)
    print(f"Report generated successfully to {report_file}:")
    print(f"- Rows Processed: {summary['rows']}")
    print(f"- Total Revenue:  ${summary['revenue']:,.2f}")
    print(f"- Top Product:    {summary['best_seller']} ({summary['highest_qty']} units)")
