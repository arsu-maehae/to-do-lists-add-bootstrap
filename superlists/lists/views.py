from django.shortcuts import render
from django.shortcuts import render, redirect  # <--- เพิ่ม redirect
from lists.models import Item, List # <--- เพิ่ม List
def home_page(request):

    # ดึงข้อมูลทั้งหมดออกมา
    # items = Item.objects.all()
    # ส่งไปที่ template ในชื่อ 'items'
    # return render(request, "home.html", {"items": items})
    return render(request, "home.html")

def about_page(request):
    return render(request, 'about.html')

def view_list(request, list_id):
    our_list = List.objects.get(id=list_id)
    #items = Item.objects.filter(list=our_list)
    #return render(request, "list.html", {"items": items})
    #return render(request, "list.html", {"items": items, "list": our_list})
    return render(request, "list.html", {"list": our_list})


def new_list(request):
    nulist = List.objects.create()
    Item.objects.create(text=request.POST["item_text"], list=nulist)
    return redirect(f"/lists/{nulist.id}/")

def add_item(request, list_id):
    our_list = List.objects.get(id=list_id)
    Item.objects.create(text=request.POST["item_text"], list=our_list)
    return redirect(f"/lists/{our_list.id}/")