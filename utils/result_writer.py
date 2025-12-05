import csv

def write_csv(path, results):
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["ID", "Status", "Detail", "Fixable"])

        for r in results:
            writer.writerow([
                r["ID"], r["Status"], r["Detail"], r["Fixable"]
            ])
