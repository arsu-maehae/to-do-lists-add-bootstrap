from selenium import webdriver

# Selenium Manager automatically finds and downloads the driver for you
driver = webdriver.Chrome()

driver.get("https://docs.djangoproject.com/en/6.0/intro/tutorial01/")
print(driver.title)
assert("part 1" in driver.title)
driver.quit()