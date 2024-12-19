from models import Config
import json

schema = Config.model_json_schema()

with open("schema.json", "w") as f:
    json.dump(schema, f, indent=2)
