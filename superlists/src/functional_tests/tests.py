from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import WebDriverException
import time, os
from django.contrib.staticfiles.testing import StaticLiveServerTestCase

MAX_WAIT = 10

# 1. สร้าง Base Class เพื่อเก็บ setUp และ tearDown ที่ใช้ร่วมกัน
class FunctionalTest(StaticLiveServerTestCase):
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
                row_data = [row.text for row in rows]
                
                match = False
                for row in row_data:
                    if row_text in row:
                        match = True
                        break
                
                self.assertTrue(match, f"หา '{row_text}' ไม่เจอ\nสิ่งที่เจอคือ: {row_data}")
                return
            except (AssertionError, WebDriverException) as e:
                if time.time() - start_time > MAX_WAIT:
                    raise e
                time.sleep(0.5)

# 2. Test ของ To-Do List (สืบทอดมาจาก FunctionalTest)
class NewVisitorTest(FunctionalTest):

    def test_layout_and_styling(self):
        # Edith ไปที่หน้าแรก
        self.browser.get(self.live_server_url)
        self.browser.set_window_size(1024, 768)

        # 👇 แก้ไข: ต้องกดปุ่ม To-Do List ก่อน ถึงจะเจอ inputbox
        # (หาปุ่มที่มีคำว่า To-Do List แล้วคลิก)
        self.browser.find_element(By.PARTIAL_LINK_TEXT, "To-Do List").click()

        # เธอสังเกตเห็นว่ากล่อง input จัดวางอยู่อย่างสวยงามตรงกลาง
        inputbox = self.browser.find_element(By.ID, "id_new_item")
        self.assertAlmostEqual(
            inputbox.location['x'] + inputbox.size['width'] / 2,
            512,
            delta=80,
        )

    def test_can_start_a_list_for_one_user(self):
        # Edith ไปที่หน้า homepage
        self.browser.get(self.live_server_url)

        # 👇 แก้ไข: ต้องคลิกเข้า To-Do List ก่อน
        self.browser.find_element(By.PARTIAL_LINK_TEXT, "To-Do List").click()

        # เช็คว่าเข้ามาถูกหน้า (Title มีคำว่า To-Do)
        self.assertIn('To-Do', self.browser.title)
        header_text = self.browser.find_element(By.TAG_NAME, 'h1').text
        self.assertIn('To-Do', header_text)

        # เธอพิมพ์ "Buy peacock feathers"
        inputbox = self.browser.find_element(By.ID, 'id_new_item')
        inputbox.send_keys('Buy peacock feathers')

        # เธอเห็นช่องเลือก Priority และเลือก "High"
        # (หมายเหตุ: ถ้าหน้า HTML คุณยังไม่มี dropdown id="id_priority" บรรทัดนี้จะ Error นะครับ)
        # priority_box = self.browser.find_element(By.ID, 'id_priority')
        # Select(priority_box).select_by_visible_text('High')

        # เธอกด Enter
        inputbox.send_keys(Keys.ENTER)
        
        # เช็คตาราง
        self.wait_for_row_in_list_table('1: Buy peacock feathers')

        # เธอพิมพ์รายการที่ 2
        inputbox = self.browser.find_element(By.ID, 'id_new_item')
        inputbox.send_keys('Use peacock feathers to make a fly')
        inputbox.send_keys(Keys.ENTER)

        # เช็คตารางอีกรอบ
        self.wait_for_row_in_list_table('2: Use peacock feathers to make a fly')
        self.wait_for_row_in_list_table('1: Buy peacock feathers')

    def test_multiple_users_can_start_lists_at_different_urls(self):
        # Edith เริ่ม list ใหม่
        self.browser.get(self.live_server_url)
        
        # 👇 แก้ไข: คลิกเข้า App ก่อน
        self.browser.find_element(By.PARTIAL_LINK_TEXT, "To-Do List").click()
        
        inputbox = self.browser.find_element(By.ID, 'id_new_item')
        inputbox.send_keys('Buy peacock feathers')
        inputbox.send_keys(Keys.ENTER)
        self.wait_for_row_in_list_table('1: Buy peacock feathers')

        edith_list_url = self.browser.current_url
        self.assertRegex(edith_list_url, '/lists/.+')

        # Francis ผู้ใช้ใหม่เข้ามา
        self.browser.quit()
        self.browser = webdriver.Chrome()

        # Francis เข้ามาหน้าแรก
        self.browser.get(self.live_server_url)
        
        # 👇 แก้ไข: Francis ก็ต้องคลิกเข้า App เหมือนกัน
        self.browser.find_element(By.PARTIAL_LINK_TEXT, "To-Do List").click()

        page_text = self.browser.find_element(By.TAG_NAME, 'body').text
        self.assertNotIn('Buy peacock feathers', page_text)

        inputbox = self.browser.find_element(By.ID, 'id_new_item')
        inputbox.send_keys('Buy milk')
        inputbox.send_keys(Keys.ENTER)
        self.wait_for_row_in_list_table('1: Buy milk')

        francis_list_url = self.browser.current_url
        self.assertRegex(francis_list_url, '/lists/.+')
        self.assertNotEqual(francis_list_url, edith_list_url)

        page_text = self.browser.find_element(By.TAG_NAME, 'body').text
        self.assertNotIn('Buy peacock feathers', page_text)
        self.assertIn('Buy milk', page_text)


# 3. Test ของ Calculator (สืบทอดมาจาก FunctionalTest เช่นกัน)
# ตอนนี้จะมี browser ให้ใช้แล้ว!
class CalculatorTest(FunctionalTest):

    def test_can_navigate_to_calculator_and_calculate_django(self):
        # 1. Edith เข้ามาที่หน้าแรก (Home)
        self.browser.get(self.live_server_url)
        self.browser.set_window_size(1024, 768)

        # 2. เธอเห็นปุ่มไป Calculator และกดมัน
        self.browser.find_element(By.PARTIAL_LINK_TEXT, "Calculator").click()

        # 3. ตอนนี้เธออยู่ที่หน้าเลือกโหมด เธอเลือก "Django Style"
        # (ต้องมั่นใจว่าในหน้า landing ของ calc มีลิงก์ที่เขียนว่า Django Style หรือมี href='/calc/django/')
        try:
            self.browser.find_element(By.CSS_SELECTOR, "a[href='/calc/django/']").click()
        except:
            # ถ้าหาไม่เจอ ลองหาจาก partial link text
            self.browser.find_element(By.PARTIAL_LINK_TEXT, "Django").click()

        # 4. เธอเจอฟอร์มเครื่องคิดเลข และลองกรอกเลข
        num1_box = self.browser.find_element(By.NAME, 'num1')
        num1_box.send_keys('10')

        num2_box = self.browser.find_element(By.NAME, 'num2')
        num2_box.send_keys('5')

        operator_box = self.browser.find_element(By.NAME, 'operator')
        Select(operator_box).select_by_value('add') 

        submit_button = self.browser.find_element(By.TAG_NAME, 'button')
        submit_button.click()

        body_text = self.browser.find_element(By.TAG_NAME, 'body').text
        self.assertIn('15.0', body_text)

    def test_can_use_js_calculator(self):
        # เข้าไปที่หน้า JS โดยตรง
        self.browser.get(self.live_server_url + "/calc/js/")

        self.browser.find_element(By.ID, 'num1').send_keys('8')
        self.browser.find_element(By.ID, 'num2').send_keys('8')
        
        select = Select(self.browser.find_element(By.ID, 'operator'))
        select.select_by_value('multiply')

        self.browser.find_element(By.TAG_NAME, 'button').click()

        result_span = self.browser.find_element(By.ID, 'result')
        self.assertEqual(result_span.text, '64')


    def test_division_by_zero(self):
        # --- 1. ทดสอบโหมด Django (Server-Side) ---
        # เข้าไปหน้า Django Calculator
        self.browser.get(self.live_server_url + "/calc/django/")
        
        # กรอกเลข 10 หาร 0
        self.browser.find_element(By.NAME, 'num1').send_keys('10')
        self.browser.find_element(By.NAME, 'num2').send_keys('0')
        
        # เลือกหาร (/)
        operator_box = self.browser.find_element(By.NAME, 'operator')
        Select(operator_box).select_by_value('divide')
        
        # กดคำนวณ
        self.browser.find_element(By.TAG_NAME, 'button').click()

        # เช็คว่าเจอข้อความแจ้งเตือน (ต้องตรงกับข้อความที่คุณเขียนใน views.py เป๊ะๆ)
        body_text = self.browser.find_element(By.TAG_NAME, 'body').text
        self.assertIn("หาค่าไม่ได้ (หารด้วยศูนย์)", body_text) 



        # --- 2. ทดสอบโหมด JavaScript (Client-Side) ---
        # เข้าไปหน้า JS Calculator
        self.browser.get(self.live_server_url + "/calc/js/")
        
        # กรอกเลข 7 หาร 0
        self.browser.find_element(By.ID, 'num1').send_keys('7')
        self.browser.find_element(By.ID, 'num2').send_keys('0')
        
        # เลือกหาร (/)
        operator_box = self.browser.find_element(By.ID, 'operator')
        Select(operator_box).select_by_value('divide')
        
        # กดคำนวณ
        self.browser.find_element(By.TAG_NAME, 'button').click()

        # เช็คผลลัพธ์ที่ id="result"
        result_span = self.browser.find_element(By.ID, 'result')
        # (ต้องตรงกับข้อความที่คุณเขียนใน calculator.html ตรงส่วน <script>)
        self.assertIn("Error", result_span.text)