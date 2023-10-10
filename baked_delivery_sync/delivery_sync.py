from flask import escape, request
import shotgun_api3
import gspread
from datetime import datetime
import os
import json

def sync_shotgrid_to_sheet(request):
    project_name = request.args.get('project_name')
    delivery_iteration = request.args.get('delivery_iteration')

    if not project_name:
        return 'Project name is missing', 400

    ##############
    # GET SG STUFF#
    ##############

    # Retrieve API KEY from environment variable
    retrieved_key = os.environ.get('SG_API_KEY')
    if not retrieved_key:
        return 'ShotGrid API key is missing from environment variables', 500

    # Define ShotGrid server and script credentials
    SHOTGUN_URL = 'https://baked.shotgunstudio.com'
    SCRIPT_NAME = 'Tidbyt'
    SCRIPT_KEY = retrieved_key

    # Connect to ShotGrid
    sg = shotgun_api3.Shotgun(SHOTGUN_URL, SCRIPT_NAME, SCRIPT_KEY)

    # Define version filters
    filters = [
        ["project.Project.name", "is", project_name], ["sg_status_list", "is", "cli"]
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

    # Sort versions by 'sg_shot_code' in alphabetical order
    sorted_versions = sorted(versions, key=lambda x: x['sg_shot_code'])

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
    for version in sorted_versions:
        version_code = version['code']
        version_row = [version[field] for field in fields]
        notes_for_version = version_note_map.get(version_code, [])
        version_row.extend(notes_for_version)
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

    # Retrieve Google Sheet keys from environment variable
    google_sheet_keys_json = os.environ.get('GOOGLE_SHEET_KEYS')
    if not google_sheet_keys_json:
        return 'Google Sheet keys are missing from environment variables', 500

    google_sheet_keys = json.loads(google_sheet_keys_json)

    # Use service account to open sheet
    sa = gspread.service_account_from_dict(google_sheet_keys)

    ################################
    ## CONTACTS PULL FROM GSHEET ###
    ################################

    # Open contacts sheet
    sh = sa.open(project_name + "_CLIENT_CONTACT_SHEET")

    # access correct contacts worksheet
    wks = sh.worksheet("Sheet1")

    # get cotacts data
    contacts_in_data = wks.get("A2:F15")

     # sync contacts
    contacts_out_data = contacts_in_data

    #open Submission Sheet
    sh = sa.open(project_name + "_BKD_VFX_Submission_" + formatted_date + delivery_iteration_end_string)

    # Access correct worksheet
    wks = sh.worksheet("Submission")

    # Clear existing data
    cell_range_to_clear = 'A3:D30'
    wks.update(cell_range_to_clear, [["" for _ in range(4)] for _ in range(28)])

    # Update worksheet with both versions and corresponding notes
    wks.update('A3', formatted_data_with_notes)

    ##############################
    ## CONTACTS PUSH TO GSHEET ###
    ##############################

    # access correct contacts worksheet in target sheet
    wks = sh.worksheet("Contacts")

    # Fetch the range of contacts cells
    contacts_cell_range_to_clear = 'A3:F15'

    # Clear the values for contacts
    for cell in contacts_cell_range_to_clear:
        wks.update(contacts_cell_range_to_clear, [["" for _ in range(6)] for _ in range(13)])

    # update contacts worksheet
    wks.update('A3', contacts_out_data)

    return 'Sync complete', 200