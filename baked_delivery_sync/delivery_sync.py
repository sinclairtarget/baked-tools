import shotgun_api3
import gspread
from datetime import datetime

##############
#GET SG STUFF#
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

#temporary values - need to pull project name from first 3 characters in cell A1, and deilvery_iteration from last 2 (if applicable)- 
#-in worksheet = Submission --- can be delivered in http?
project_name = "BRC"
delivery_iteration = "02"

# Define filters to narrow down the query
filters = [
    ["project.Project.name", "is", project_name], ["sg_status_list", "is", "note"]
]

# Define fields to be retrieved
fields = ['sg_shot_code', 'code', 'sg_work_description']

# Query the ShotGrid site
versions = sg.find("Version", filters, fields)

###############
#PUT ON GSHEET#
###############

# Format the data from SG as a list of lists (each sub-list is a row)
formatted_data = [[version[field] for field in fields] for version in versions]

# Get the current date and time
now = datetime.now()

# Format the datetime object as YYMMDD
formatted_date = now.strftime("%y%m%d")

# remove "_" from below if delivery_iteration = ""
if delivery_iteration:
    delivery_iteration_end_string = "_" + delivery_iteration
else:
    delivery_iteration_end_string = delivery_iteration

# user service account to open sheet
sa = gspread.service_account(filename="baked_delivery_sync/GOOGLE-SHEET-KEYS.json")
sh = sa.open(project_name + "_BKD_VFX_Submission_" + formatted_date + delivery_iteration_end_string)

# access correct worksheet
wks = sh.worksheet("Submission")

# Clear the existing data from the worksheet
# Fetch the range of cells
cell_range_to_clear = 'A3:D30'

# Clear the values
for cell in cell_range_to_clear:
    wks.update(cell_range_to_clear, [["" for _ in range(4)] for _ in range(28)])

# update worksheet
wks.update('A3', formatted_data)