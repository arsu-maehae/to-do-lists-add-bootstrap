from django.test import LiveServerTestCase
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import WebDriverException
import time

MAX_WAIT = 10

class NewVisitorTest(LiveServerTestCase):

    def test_layout_and_styling(self):
        # Edith ไปที่หน้าแรก
        self.browser.get(self.live_server_url)
        self.browser.set_window_size(1024, 768)

        # เธอสังเกตเห็นว่ากล่อง input จัดวางอยู่อย่างสวยงามตรงกลาง
        inputbox = self.browser.find_element(By.ID, "id_new_item") # <--- หา element ก่อน
        self.assertAlmostEqual(
            inputbox.location['x'] + inputbox.size['width'] / 2,
            512,
            delta=35,  # แก้ตรงนี้: เพิ่มจาก 10 เป็น 35 เพื่อเผื่อขอบหน้าต่าง
        )

        # เธอเริ่ม list ใหม่ และเห็นว่า input ก็ยังอยู่ตรงกลางดี
        inputbox.send_keys("testing")
        inputbox.send_keys(Keys.ENTER)
        self.wait_for_row_in_list_table("1: testing")
        
        inputbox = self.browser.find_element(By.ID, "id_new_item") # <--- หาใหม่หลัง reload
        self.assertAlmostEqual(
            inputbox.location['x'] + inputbox.size['width'] / 2,
            512,
            delta=35,  # แก้ตรงนี้: เพิ่มจาก 10 เป็น 35 เพื่อเผื่อขอบหน้าต่าง
        )

    def setUp(self):
        self.browser = webdriver.Chrome()

    def tearDown(self):
        self.browser.quit()

    def wait_for_row_in_list_table(self, row_text):
        start_time = time.time()
        while True:
            try:
                table = self.browser.find_element(By.ID, 'id_list_table')
                rows = table.find_elements(By.TAG_NAME, 'tr')
                self.assertIn(row_text, [row.text for row in rows])
                return
            except (AssertionError, WebDriverException) as e:
                if time.time() - start_time > MAX_WAIT:
                    raise e
                time.sleep(0.5)

    def test_can_start_a_list_for_one_user(self):
        # Edith ได้ยินมาว่ามีเว็บ to-do list ใหม่ที่เจ๋งมาก
        # เธอเลยไปเช็คดูที่หน้า homepage
        self.browser.get(self.live_server_url)

        # เธอสังเกตเห็นว่า title และ header ของหน้าเว็บระบุว่าเป็น to-do lists
        self.assertIn('To-Do', self.browser.title)
        header_text = self.browser.find_element(By.TAG_NAME, 'h1').text
        self.assertIn('To-Do', header_text)

        # เธอถูกชวนให้กรอก to-do item ทันที
        inputbox = self.browser.find_element(By.ID, 'id_new_item')
        self.assertEqual(
            inputbox.get_attribute('placeholder'),
            'Enter a to-do item'
        )

        # เธอพิมพ์ "Buy peacock feathers" (ซื้อขนยูง)
        inputbox.send_keys('Buy peacock feathers')

        # เมื่อเธอกด enter, หน้าเว็บจะ update
        # และตอนนี้หน้าเว็บโชว์รายการ "1: Buy peacock feathers"
        inputbox.send_keys(Keys.ENTER)
        self.wait_for_row_in_list_table('1: Buy peacock feathers')

        # เธอพิมพ์รายการเพิ่ม "Use peacock feathers to make a fly"
        inputbox = self.browser.find_element(By.ID, 'id_new_item')
        inputbox.send_keys('Use peacock feathers to make a fly')
        inputbox.send_keys(Keys.ENTER)

        # หน้าเว็บ update อีกครั้ง และตอนนี้โชว์ทั้งสองรายการ
        self.wait_for_row_in_list_table('2: Use peacock feathers to make a fly')
        self.wait_for_row_in_list_table('1: Buy peacock feathers')

        # เธอพอใจแล้วก็เข้านอน

    def test_multiple_users_can_start_lists_at_different_urls(self):
        # Edith เริ่ม list ใหม่
        self.browser.get(self.live_server_url)
        inputbox = self.browser.find_element(By.ID, 'id_new_item')
        inputbox.send_keys('Buy peacock feathers')
        inputbox.send_keys(Keys.ENTER)
        self.wait_for_row_in_list_table('1: Buy peacock feathers')

        # สังเกตว่า list มี URL ที่ไม่เหมือนใคร
        edith_list_url = self.browser.current_url
        self.assertRegex(edith_list_url, '/lists/.+')

        # ตอนนี้มีผู้ใช้ใหม่ชื่อ Francis เข้ามาที่เว็บ

        ## เราใช้ browser session ใหม่ เพื่อให้มั่นใจว่าข้อมูลของ Edith
        ## จะไม่หลุดมาจาก cookies ฯลฯ
        self.browser.quit()
        self.browser = webdriver.Chrome()

        # Francis เข้ามาหน้าแรก
        # เขาไม่เห็น list ของ Edith
        self.browser.get(self.live_server_url)
        page_text = self.browser.find_element(By.TAG_NAME, 'body').text
        self.assertNotIn('Buy peacock feathers', page_text)
        self.assertNotIn('make a fly', page_text)

        # Francis เริ่ม list ใหม่โดยการกรอกข้อมูล
        inputbox = self.browser.find_element(By.ID, 'id_new_item')
        inputbox.send_keys('Buy milk')
        inputbox.send_keys(Keys.ENTER)
        self.wait_for_row_in_list_table('1: Buy milk')

        # Francis ได้ URL ที่ไม่เหมือนใคร
        francis_list_url = self.browser.current_url
        self.assertRegex(francis_list_url, '/lists/.+')
        self.assertNotEqual(francis_list_url, edith_list_url)

        # ข้อมูลของ Edith ยังคงไม่โผล่มา
        page_text = self.browser.find_element(By.TAG_NAME, 'body').text
        self.assertNotIn('Buy peacock feathers', page_text)
        self.assertIn('Buy milk', page_text)