from openpyxl import load_workbook
import xlwings as xw

def update_and_read_excel(filepath, entries, submodule_type='Water Distribution', part_start_row=4, summary_start_row=2):
    """
    Update specific cells in an existing Excel file and read calculated values.
    
    Args:
        filepath: Path to Excel file
        sheet_name: Sheet name to update
        submodule_type: 'Water Collection Welded', 'Water Collection TriArmor', 'Water Collection Unwelded', or 'Water Distribution'
        entries: List of lists containing values to write to the Excel file
        start_row: Starting row for writing entries
    
    Returns:
        List of calculated values from the Excel file
    """
    part_sheet = 'BAC Part List'
    joint_sheet = 'Joints List'
    summary_sheet = 'Summary'

    try:
        # Load the workbook and sheet
        workbook = load_workbook(filepath)
        sheet = workbook[part_sheet]
        
        # Write entries to the Excel file
        for i, entry in enumerate(entries):
            for j, value in enumerate(entry):
                sheet.cell(row=part_start_row + i, column=j + 1, value=value)
        
        # Save the workbook
        workbook.save(filepath)

        sheet = workbook[summary_sheet]
        sheet.cell(row=summary_start_row + 1, column=1, value=entries[0][0])
        sheet.cell(row=summary_start_row + 1, column=2, value=submodule_type)

        force_recalculation(filepath)

        # Reload the workbook to read calculated values
        workbook = load_workbook(filepath, data_only=True)
        sheet = workbook[summary_sheet]
        
        # Read calculated values ()
        calculated_values = []
        for i in range(len(entries)):
            row_values = [sheet.cell(row=summary_start_row + i, column=col).value for col in range(22, 25)]  # Adjust columns as needed
            calculated_values.append(row_values)
        
        return calculated_values
    
    except Exception as e:
        print(f"Error updating or reading Excel: {e}")
        return None

def force_recalculation(filepath):
    """
    Open the Excel file with xlwings to force recalculation of formulas.
    """
    try:
        app = xw.App(visible=False)
        wb = app.books.open(filepath)
        wb.app.calculate()  # Force recalculation
        wb.save()
        wb.close()
        app.quit()
    except Exception as e:
        print(f"Error forcing recalculation: {e}")

entries = [
    ['Set1', 'ID1', 10, 'Auto Tube Laser', 'Roll Form (outsourced)', 'GLV-M5', 10, 5, 120.5, 3, 0, 50.0, 20.0, 'Class 1'],
    # ['Set2', 'ID2', 20, 'Plasma', 'Roll Form', 'Aluminum', 14, 8, 200.0, 5, 'No', 80.0, 30.0, 'Category2']
]

calculated_values = update_and_read_excel(
    filepath='cost_calculator.xlsx',
    sheet_name='BAC Part List',
    entries=entries,
    start_row=4
)

print("Calculated Values:", calculated_values)