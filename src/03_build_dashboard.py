"""Step 3 - Inject data.json into a self-contained interactive HTML dashboard."""
import json
data = json.load(open("dashboard/data.json"))
tpl = open("src/dashboard_template.html").read()
open("dashboard/index.html", "w").write(tpl.replace("__DATA__", json.dumps(data)))
print("dashboard/index.html written")
