from selenium.webdriver.common.by import By


def prone_of_these_elements_is_visible(element1, element2):
    def wait_for_condition(driver):
        attribute = driver.find_element(By.ID, element1)
        if attribute.is_displayed():
            return attribute
        elif driver.find_element(By.ID, element2).is_displayed():
            return driver.find_element(By.ID, element2)
        else:
            return False

    return wait_for_condition
