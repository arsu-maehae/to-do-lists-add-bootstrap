from django.test import LiveServerTestCase
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import WebDriverException # <--- 1. เพิ่มตัวนี้
import time

MAX_WAIT = 10  # <--- 2. ตั้งเวลา "ตื๊อ" สูงสุด (วินาที)

class NewVisitorTest(LiveServerTestCase):

    def setUp(self):
        self.browser = webdriver.Chrome()

    def tearDown(self):
        self.browser.quit()

    # 3. เปลี่ยนชื่อฟังก์ชันเป็น wait_for... และเพิ่ม Logic การรอ
    def wait_for_row_in_list_table(self, row_text):
        start_time = time.time()
        while True:  # <--- วนลูปไม่รู้จบ
            try:
                table = self.browser.find_element(By.ID, 'id_list_table')
                rows = table.find_elements(By.TAG_NAME, 'tr')
                self.assertIn(row_text, [row.text for row in rows])
                return  # <--- ถ้าเจอแล้ว ให้จบฟังก์ชันทันที (Success)
            except (AssertionError, WebDriverException) as e:
                # ถ้ายังไม่เจอ หรือหาตารางไม่ได้
                if time.time() - start_time > MAX_WAIT:
                    raise e  # <--- ถ้าเกินเวลาที่กำหนดแล้ว ให้ยอมแพ้ (Fail)
                time.sleep(0.5)  # <--- ถ้ายังไม่ครบเวลา ให้พัก 0.5 วิ แล้ววนไปลองใหม่

    def test_can_start_a_list_and_retrieve_it_later(self):
        self.browser.get(self.live_server_url)

        self.assertIn('To-Do', self.browser.title)
        header_text = self.browser.find_element(By.TAG_NAME, 'h1').text
        self.assertIn('To-Do', header_text)

        inputbox = self.browser.find_element(By.ID, 'id_new_item')
        self.assertEqual(
            inputbox.get_attribute('placeholder'),
            'Enter a to-do item'
        )

        inputbox.send_keys('Buy peacock feathers')
        inputbox.send_keys(Keys.ENTER)
        
        # 4. ลบ time.sleep() ทิ้งไปเลย! แล้วเรียกฟังก์ชันใหม่แทน
        self.wait_for_row_in_list_table('1: Buy peacock feathers')

        inputbox = self.browser.find_element(By.ID, 'id_new_item')
        inputbox.send_keys('Use peacock feathers to make a fly')
        inputbox.send_keys(Keys.ENTER)
        
        # 5. ลบ time.sleep() ทิ้งอีกจุด
        self.wait_for_row_in_list_table('1: Buy peacock feathers')
        self.wait_for_row_in_list_table('2: Use peacock feathers to make a fly')