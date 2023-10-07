import shotgun_api3
import gspread
from datetime import datetime

#temporary values - need to pull project name from first 3 characters in cell A1, and deilvery_iteration from last 2 (if applicable)- 
#-in worksheet = Submission --- can be delivered in http?
project_name = "BRC"
delivery_iteration = "02"

# user service account
sa = gspread.service_account(filename="baked_delivery_sync/GOOGLE-SHEET-KEYS.json")

##################
#PULL FROM GSHEET#
##################

# Open sheet
sh = sa.open(project_name + "_CLIENT_CONTACT_SHEET")

# access correct worksheet
wks = sh.worksheet("Sheet1")

# get data
contacts_in_data = wks.get("A2:F15")

###############
#PUT ON GSHEET#
###############

# Sync
contacts_out_data = contacts_in_data

# Get the current date and time
now = datetime.now()

# Format the datetime object as YYMMDD
formatted_date = now.strftime("%y%m%d")

# remove "_" from below if delivery_iteration = ""
if delivery_iteration:
    delivery_iteration_end_string = "_" + delivery_iteration
else:
    delivery_iteration_end_string = delivery_iteration

# Open sheet
sh = sa.open(project_name + "_BKD_VFX_Submission_" + formatted_date + delivery_iteration_end_string)

# access correct worksheet
wks = sh.worksheet("Contacts")

# Clear the existing data from the worksheet
# Fetch the range of cells
cell_range_to_clear = 'A3:F15'

# Clear the values
for cell in cell_range_to_clear:
    wks.update(cell_range_to_clear, [["" for _ in range(6)] for _ in range(13)])

# update worksheet
wks.update('A3', contacts_out_data)