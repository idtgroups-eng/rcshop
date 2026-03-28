import json
import os
from main.models import Product


def run_bulk_update():

    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(BASE_DIR, "products_bulk.json")

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        print("❌ products_bulk.json file not found!")
        print("Make sure file exists inside main folder")
        return

    for item in data:
        try:
            p = Product.objects.get(name=item["name"])
            p.highlights = item["highlights"]
            p.specs = item["specs"]
            p.save()
            print("✅ Updated:", p.name)

        except Product.DoesNotExist:
            print("❌ Product Not Found:", item["name"])

    print("\n🔥 Bulk Update Done Successfully!")
