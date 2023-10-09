import shotgun_api3
import gspread
from datetime import datetime

##############
# GET SG STUFF#
##############

# Retrieve API KEY
with open('baked_delivery_sync/SG-API-KEY.txt', 'r') as f:
    retrieved_key = f.read().strip()

# Define ShotGrid server and script credentials
SHOTGUN_URL = 'https://baked.shotgunstudio.com'
SCRIPT_NAME = 'Tidbyt'
SCRIPT_KEY = retrieved_key

# Connect to ShotGrid
sg = shotgun_api3.Shotgun(SHOTGUN_URL, SCRIPT_NAME, SCRIPT_KEY)

# Temporary values - need to pull project name from first 3 characters in cell A1, and deilvery_iteration from last 2 (if applicable)- 
#-in worksheet = Submission --- can be delivered in http?
project_name = "BRC"
delivery_iteration = "02"

# Define version filters
filters = [
    ["project.Project.name", "is", project_name], ["sg_status_list", "is", "note"]
]

# Define note filters
note_filters = [
    ["project.Project.name", "is", project_name], ["content", "contains", "FROM PRODUCTION"]
]

# Define fields to be retrieved
fields = ['sg_shot_code', 'code', 'sg_work_description']

# Define note fields to be retrieved
note_fields = ['content', 'addressings_to']

# Query ShotGrid for versions
versions = sg.find("Version", filters, fields)

# Query ShotGrid for notes
notes = sg.find("Note", note_filters, note_fields)

###############
# PUT ON GSHEET#
###############

# Create a mapping between versions and notes
version_note_map = {}
for version in versions:
    version_code = version['code']
    version_note_map[version_code] = []

for note in notes:
    note_content = note['content']
    for version_code in version_note_map.keys():
        if version_code in note_content:
            version_note_map[version_code].append(note_content)

# Create a list that includes both versions and corresponding notes
formatted_data_with_notes = []
for version in versions:
    version_code = version['code']
    version_row = [version[field] for field in fields]
    notes_for_version = version_note_map.get(version_code, [])
    version_row.extend(notes_for_version)  # Add notes to the row
    formatted_data_with_notes.append(version_row)

# Get the current date and time
now = datetime.now()

# Format the datetime object
formatted_date = now.strftime("%y%m%d")

# Update delivery_iteration_end_string based on delivery_iteration
if delivery_iteration:
    delivery_iteration_end_string = "_" + delivery_iteration
else:
    delivery_iteration_end_string = delivery_iteration

# Use service account to open sheet
sa = gspread.service_account(filename="baked_delivery_sync/GOOGLE-SHEET-KEYS.json")
sh = sa.open(project_name + "_BKD_VFX_Submission_" + formatted_date + delivery_iteration_end_string)

# Access correct worksheet
wks = sh.worksheet("Submission")

# Clear existing data
cell_range_to_clear = 'A3:D30'
for cell in cell_range_to_clear:
    wks.update(cell_range_to_clear, [["" for _ in range(4)] for _ in range(28)])

# Update worksheet with both versions and corresponding notes
wks.update('A3', formatted_data_with_notes)
