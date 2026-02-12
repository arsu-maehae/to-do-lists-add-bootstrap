
# Create your views here.

# src/calculator/views.py
from django.shortcuts import render
from urllib import request

def calculator_page(request):
    # แค่ render ไฟล์ HTML ไปให้ user
    return render(request, 'calculator_landing.html')

def js_cal(request):
    # แค่ render ไฟล์ HTML ไปให้ user
    return render(request, 'js_cal.html')

def django_cal(request):
    result = None  # ค่าเริ่มต้นให้เป็นว่างๆ ไว้ก่อน
    
    # เช็คว่ามีการกดปุ่มส่งข้อมูลมาหรือเปล่า (POST)
    if request.method == 'POST':
        try:
            # รับค่าจากฟอร์ม (HTML)
            # request.POST.get('ชื่อช่อง', ค่าดีฟอลต์)
            num1 = float(request.POST.get('num1', 0))
            num2 = float(request.POST.get('num2', 0))
            operator = request.POST.get('operator')

            # เริ่มคำนวณ
            if operator == 'add':
                result = num1 + num2
            elif operator == 'subtract':
                result = num1 - num2
            elif operator == 'multiply':
                result = num1 * num2
            elif operator == 'divide':
                if num2 != 0:
                    result = num1 / num2
                else:
                    result = "หาค่าไม่ได้ (หารด้วยศูนย์)"
        except ValueError:
            result = "กรุณาใส่ตัวเลขที่ถูกต้อง"

    # ส่งตัวแปร result กลับไปแสดงที่หน้าเว็บ
    return render(request, 'django_cal.html', {'result': result})