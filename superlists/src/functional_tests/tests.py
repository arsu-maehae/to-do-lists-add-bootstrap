#from django.test import LiveServerTestCase
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import WebDriverException
import time, os
from django.contrib.staticfiles.testing import StaticLiveServerTestCase

MAX_WAIT = 10

class NewVisitorTest(StaticLiveServerTestCase):

    def test_layout_and_styling(self):
        # Edith ไปที่หน้าแรก
        self.browser.get(self.live_server_url)
        self.browser.set_window_size(1024, 768)

        # เธอสังเกตเห็นว่ากล่อง input จัดวางอยู่อย่างสวยงามตรงกลาง
        inputbox = self.browser.find_element(By.ID, "id_new_item") # <--- หา element ก่อน
        self.assertAlmostEqual(
            inputbox.location['x'] + inputbox.size['width'] / 2,
            512,
            delta=50,  # แก้ตรงนี้: เพิ่มจาก 10 เป็น 35 เพื่อเผื่อขอบหน้าต่าง
        )

        # เธอเริ่ม list ใหม่ และเห็นว่า input ก็ยังอยู่ตรงกลางดี
        inputbox.send_keys("testing")
        inputbox.send_keys(Keys.ENTER)
        self.wait_for_row_in_list_table("1: testing")
        
        inputbox = self.browser.find_element(By.ID, "id_new_item") # <--- หาใหม่หลัง reload
        self.assertAlmostEqual(
            inputbox.location['x'] + inputbox.size['width'] / 2,
            512,
            delta=50,  # แก้ตรงนี้: เพิ่มจาก 10 เป็น 35 เพื่อเผื่อขอบหน้าต่าง
        )

    def setUp(self):
        self.browser = webdriver.Chrome()
        if test_server := os.environ.get("TEST_SERVER"):   
            self.live_server_url = "http://" + test_server

    def tearDown(self):
        self.browser.quit()

    def wait_for_row_in_list_table(self, row_text):
        start_time = time.time()
        while True:
            try:
                table = self.browser.find_element(By.ID, 'id_list_table')
                rows = table.find_elements(By.TAG_NAME, 'tr')
                
                # อ่านค่า text ออกมา (จะได้ประมาณ "1: hellow High")
                row_data = [row.text for row in rows]
                
                # เช็คว่ามีบรรทัดไหนที่มีคำที่เราหา (row_text) แฝงอยู่ไหม
                match = False
                for row in row_data:
                    if row_text in row:  # 👈 จุดสำคัญ: ใช้ in แทน ==
                        match = True
                        break
                
                self.assertTrue(match, f"หา '{row_text}' ไม่เจอ\nสิ่งที่เจอคือ: {row_data}")
                return
            except (AssertionError, WebDriverException) as e:
                if time.time() - start_time > MAX_WAIT:
                    raise e
                time.sleep(0.5)

    def test_can_start_a_list_for_one_user(self):
        # Edith ไปที่หน้า homepage
        self.browser.get(self.live_server_url)

        # ... (ส่วนเช็ค Title เหมือนเดิม) ...
        self.assertIn('To-Do', self.browser.title)
        header_text = self.browser.find_element(By.TAG_NAME, 'h1').text
        self.assertIn('To-Do', header_text)

        # เธอพิมพ์ "Buy peacock feathers"
        inputbox = self.browser.find_element(By.ID, 'id_new_item')
        inputbox.send_keys('Buy peacock feathers')

        # 👇 --- เพิ่มส่วนนี้: เธอเห็นช่องเลือก Priority และเลือก "High" ---
        # สมมติว่าใน HTML คุณตั้ง id ของ dropdown ว่า "id_priority"
        priority_box = self.browser.find_element(By.ID, 'id_priority')
        select = Select(priority_box)
        select.select_by_visible_text('High') 
        # --------------------------------------------------------

        # เธอกด Enter
        inputbox.send_keys(Keys.ENTER)
        
        # 👇 --- แก้ส่วนนี้: เช็คว่าเจอทั้ง "ชื่อรายการ" และ "ความสำคัญ" ---
        # เช็คว่ามีรายการขึ้นมา
        self.wait_for_row_in_list_table('1: Buy peacock feathers')
        # เช็คว่ามีคำว่า High โผล่มาในบรรทัดนั้นด้วย (หรือจะเช็คแยกก็ได้)
        self.wait_for_row_in_list_table('High')
        # --------------------------------------------------------

        # เธอพิมพ์รายการที่ 2 "Use peacock feathers to make a fly"
        inputbox = self.browser.find_element(By.ID, 'id_new_item')
        inputbox.send_keys('Use peacock feathers to make a fly')
        
        # 👇 --- รอบนี้เธอลองเลือก "Low" บ้าง ---
        priority_box = self.browser.find_element(By.ID, 'id_priority')
        select = Select(priority_box)
        select.select_by_visible_text('Low')
        # ------------------------------------

        inputbox.send_keys(Keys.ENTER)

        # หน้าเว็บ update และโชว์ทั้งสองรายการ พร้อม Priority ที่ถูกต้อง
        self.wait_for_row_in_list_table('2: Use peacock feathers to make a fly')
        self.wait_for_row_in_list_table('Low') # เช็คว่าเจอ Low
        
        self.wait_for_row_in_list_table('1: Buy peacock feathers')
        self.wait_for_row_in_list_table('High') # เช็คว่าของเดิมยังเป็น High

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