from django.db import models

class List(models.Model):
    pass

class Item(models.Model):
    text = models.TextField(default='')  # ข้อความของรายการ
    list = models.ForeignKey(List, default=None, on_delete=models.CASCADE) # รายการที่รายการนี้เป็นของ
    
    # --- เพิ่มส่วนนี้ครับ ---
    PRIORITY_CHOICES = [
        ('high', 'High'),
        ('medium', 'Medium'),
        ('low', 'Low'),
    ]
    priority = models.CharField(
        max_length=10, 
        choices=PRIORITY_CHOICES, 
        default='medium'
    )
    # --------------------