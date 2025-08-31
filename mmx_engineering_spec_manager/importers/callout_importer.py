import json


class CalloutImporter:
    def parse_json_file(self, file_path):
        with open(file_path, 'r') as file:
            data = json.load(file)

        callouts = []
        current_type = None
        header_rows = ["SPECIFICATIONS", "FINISHES", "HARDWARE", "SINKS", "APPLIANCES"]

        for item in data.get("d", []):
            # Check if the item is a header row
            if item[0] in header_rows:
                current_type = item[0]
            # Check if the item is a data row and has a type
            elif len(item) > 2 and current_type:
                callout_data = {
                    "material": item[0],
                    "tag": item[1],
                    "description": item[2],
                    "type": current_type
                }
                callouts.append(callout_data)

        return callouts