from openpyxl import load_workbook
from selenium.webdriver.common.by import By


def read_data_from_excel(file_name, sheet):
    # Retrieves the data list from the manifest Excel sheet
    datalist = []
    workbook = load_workbook(filename=file_name)

    sheet = workbook.get_sheet_by_name(sheet)  # workbook[sheet]
    row_count = sheet.max_row
    column_count = sheet.max_column

    for i in range(2, row_count + 1):
        row = []
        for j in range(1, column_count + 1):
            row.append(sheet.cell(row=i, column=j).value)
            datalist.append(row)
    return datalist


def one_of_these_elements_is_visible(element1, element2):
    def wait_for_condition(driver):
        attribute = driver.find_element(By.ID, element1)
        if attribute.is_displayed():
            return attribute
        elif driver.find_element(By.ID, element2).is_displayed():
            return driver.find_element(By.ID, element2)

        else:
            return False

    return wait_for_condition
