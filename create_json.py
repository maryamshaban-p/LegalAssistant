import os
import json

laws_folder = "laws"

all_data = []

# Read all txt files            
for file_name in os.listdir(laws_folder):

    if file_name.endswith(".txt"):

        file_path = os.path.join(laws_folder, file_name)

        with open(file_path, "r", encoding="utf-8") as file:

            content = file.read()

            # Split into paragraphs
            paragraphs = content.split("\n")

            for paragraph in paragraphs:

                paragraph = paragraph.strip()

                if len(paragraph) > 30:

                    item = {
                        "law": file_name,
                        "text": paragraph
                    }

                    all_data.append(item)

# Save JSON
with open("legal_data.json", "w", encoding="utf-8") as json_file:

    json.dump(
        all_data,
        json_file,
        ensure_ascii=False,
        indent=4
    )

print("JSON CREATED SUCCESSFULLY")