import re
import subprocess
from rpw import DB, UI


def subprocess_cmd(command):
    """ Helper function to call subprocess.Popen consistently without having
    to repeat keyword settings"""
    # print('CMD: ' + command)
    process = subprocess.Popen(
        command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True
    )
    proc_stdout, errmsg = process.communicate()
    # print(proc_stdout)
    # if errmsg:
    #     print(errmsg)
    return process, proc_stdout, errmsg


def get_sheet_key(url):
    pat = r"(?:/d/)(?P<key>.+)(?:/)"
    match = re.search(pat, url)
    if match and match.group("key"):
        return match.group("key")


def get_schedule_values(view):
    """Gets list of values from first column.
    Example
        {'Length': ['11\' - 7 15/32"', '22\' - 2"', \
            '7\' - 4"', '20\' - 7"', '3\' - 4"'], 'title': 'Schedule: Wall Schedule',
        'Family': ['Basic Wall', 'Basic Wall', 'Basic Wall', \
            'Basic Wall', 'Basic Wall']}

    # TODO: Coerce/format data

    """
    if not isinstance(view, DB.ViewSchedule):
        UI.TaskDialog.Show("pyWeWork Drive Uploader", "View must be a schedule")
    else:
        schedule = view
        # print('Processing: {}'.format(view.Name))
        body = schedule.GetTableData().GetSectionData(DB.SectionType.Body)
        # header = schedule.GetTableData().GetSectionData(DB.SectionType.Body)
        schedule_title = schedule.Name
        qty_rows = body.NumberOfRows
        qty_cols = body.NumberOfColumns

        schedule_data = [[schedule_title]]
        for row_num in range(0, qty_rows):
            row = []
            for col_num in range(0, qty_cols):
                cell = schedule.GetCellText(DB.SectionType.Body, row_num, col_num)
                row.append(cell)
            schedule_data.append(row)

        schedule_data.append([])  # Add blank row at end
        # print('Returned Data: {}'.format(schedule_data))
        return schedule_data
