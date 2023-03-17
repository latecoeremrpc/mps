from datetime import datetime, timedelta
from io import StringIO
import zipfile
from io import BytesIO
from django.http import HttpResponse
import numpy as np
import pandas as pd
import psycopg2
from django.db.models import Max
from app.decorators import allowed_users
from app.forms import (CalendarConfigurationCpordoForm,
                       CalendarConfigurationTreatementForm, DivisionForm,
                       MaterialForm, ProductForm)
from app.models import (CalendarConfigurationCpordo,
                        CalendarConfigurationTreatement, Coois, Cycle,
                        Division, HolidaysCalendar, Material, Product,
                        Shopfloor, Staff, WorkData, Zpp, PlanningApproval)
from dateutil.relativedelta import relativedelta
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render

# Create your views here.
#Comment Houssem
#Comment Marwa
#*********************CRUD Division************************


# function to get user connected 
def username(request):
    try:
        username=request.META['REMOTE_USER']
    except Exception:
        username ="Marwa"
    return username


# add new object(Division)
def create_division(request):
    form = DivisionForm(request.POST)
    if request.method == "POST" :
        if form.is_valid():
            form.save()
            messages.success(request,"Division created successfully!")
        else:
            messages.error(request,"Division exit or Form not valid! try again")
    return redirect(read_division)


# read all objects(Division)
def read_division(request): 
    #get Division form
    form = DivisionForm()
    # undeleted_objects object of soft delete manager
    data = Division.objects.all().order_by('id')  
    return render(request, "app/division/home_division.html", {'data':data,'form':form,'username':username(request)})


#update object(Division) by id
def update_division(request):
    #get id
    id = id = request.POST.get('id')
    # fetch the object related to passed id
    obj = get_object_or_404(Division, id = id)
    # pass the object as instance in form
    form = DivisionForm(request.POST or None, instance = obj)
    if request.method == "POST":
        if form.is_valid():
            form.save()
            messages.success(request,"Division updated successfully!")
        else:
            messages.error(request,"try again!")
                
    return redirect("./")


# delete object(Division) by id
def delete_division(request,id):
    # fetch the object related to passed id
    obj = get_object_or_404(Division, id = id)
    # delete object
    obj.soft_delete()
    #alert message
    messages.success(request,"Division deleted successfully!")
    return redirect("../")
    
# restore object(Division) by id
def restore_division(request,id):
    # fetch the object related to passed id
    obj = get_object_or_404(Division, id = id)
    # restore object
    obj.restore() 
    #alert message
    messages.success(request,"Division restored successfully!")
    return redirect("../")


#********************Crud Product****************************
# add new object(product)
def create_product(request,division):
    form = ProductForm(request.POST)
    if request.method == "POST":
        if form.is_valid():
         instance=form.save(commit=False)
         instance.division_id=division
         instance.save()
         messages.success(request," Product created successfully!")
        else:
            messages.error(request,"Form not valid! try again") 
    return redirect(f'../{division}/product/')   

#update object(Product) by id
def update_product(request):
    id = id = request.POST.get('id')
    # fetch the object related to passed id
    obj = get_object_or_404(Product, id = id)
    # pass the object as instance in form
    form = ProductForm(request.POST or None, instance = obj)
    if request.method == "POST":
        if form.is_valid():
            form.save()
            messages.success(request,"Product updated successfully!")  
        else:
            messages.error(request,"Try again!")        
    return redirect(f'./{str(obj.division_id)}/product/')
    

# delete object(Product) by id
def delete_product(request, id):
    # fetch the object related to passed id
    obj = get_object_or_404(Product, id = id)
    # delete object
    obj.soft_delete()
    messages.success(request," Product deleted successfully!")  
    return redirect(f'../{str(obj.division_id)}/product/')
    

# restore object(Product) by id
def restore_product(request, id):
    # fetch the object related to passed id
    obj = get_object_or_404(Product, id = id)
    # restore object
    obj.restore()
    messages.success(request," Product restored successfully!")  
    return redirect(f'../{str(obj.division_id)}/product/')


# find all product for division 
def product(request,division):
    form = ProductForm()
    # undeleted_objects object of soft delete manager
    data = Product.objects.filter(division__pk = division ).order_by('id') 
    division_info=Division.objects.all().filter(id=division).first()  
    return render(request, "app/product/product.html", {'data':data,'division':division,'form':form,'division_info':division_info,'username':username(request)})


#*********************CRUD Material**************************

# add new object(Material)
def create_material(request,division,product):
    form = MaterialForm(request.POST)
    if request.method == "POST":
        if form.is_valid():
            instance=form.save(commit=False)
            instance.product_id=product
            instance.save()
            messages.success(request," Material created successfully!")
        else:
            messages.error(request,"Form not valid! try again")          
    return redirect(f'../{product}/material/')

# update object(Material)
def update_material(request,division):
    #get id
    id = id = request.POST.get('id')
    # fetch the object related to passed id
    obj = get_object_or_404(Material, id = id)
    # pass the object as instance in form
    form = MaterialForm(request.POST or None, instance = obj)
    if request.method == "POST":
        if form.is_valid():
            form.save()
            messages.success(request,"Material updated successfully!")
        else:
            messages.error(request,"try again!")    
    return redirect(f'./{str(obj.product_id)}/material/')
    

# delete object (Material) by id
def delete_material(request,division,id):
    # fetch the object related to passed id
    obj = get_object_or_404(Material, id = id)
    # delete object
    obj.soft_delete()
    #alert message
    messages.success(request,"Material deleted successfully!")
    return redirect(f'../{str(obj.product_id)}/material/')
   

# restore object(Material) by id
def restore_material(request,division,id):
    # fetch the object related to passed id
    obj = get_object_or_404(Material, id = id)
    # restore object
    obj.restore()
    #alert message
    messages.success(request,"Material restored successfully!")
    return redirect(f'../{str(obj.product_id)}/material/')    


# find all Material for product 
def material(request,division,product):
    #get MaterialForm
    form = MaterialForm()
    # undeleted_objects object of soft delete manager
    data = Material.objects.filter(product__pk = product ).order_by('id') 
    product_info=Product.objects.all().filter(id=product).first()  
    return render(request, "app/material/material.html", {'data':data,'division':division,'product':product,'form':form,'product_info':product_info,'username':username(request)})

#******************** calendar*******************************

def calendar(request,division,product):
    #get smooth family from product
    smooth_family = Material.undeleted_objects.filter(product_id = product).values_list('Smooth_Family',flat=True).distinct().order_by('Smooth_Family')
    # get cycle objects
    # cycle=Cycle.undeleted_objects.all().filter(product_id = product, owner = 'officiel',planning_approval__isnull=True, version__isnull=True)
    cycle=Cycle.undeleted_objects.all().filter(product_id = product, owner = 'officiel',shared=True)
    # get product object to display in calendar
    products_data = Product.undeleted_objects.all()
    # get all work data objects to display in Calendar
    workdata = WorkData.undeleted_objects.all().filter(product_id = product, owner = 'officiel')
    # get all holiday objects to display in Calendar
    holidays = HolidaysCalendar.undeleted_objects.all().filter(product_id = product, owner = 'officiel') 
    # get cycle ifo and workdata infos to display in Calendar
    product_info = Product.objects.all().filter(id=product).first()  
    return render(request, "app/calendar/calendar.html",{'product':product,'division':division,'holidays':holidays,'workdata':workdata,'products_data':products_data,'smooth_family': smooth_family,'cycle': cycle,'product_info':product_info,'username':username(request)})


# create calendar for product 
def create_calendar(request,division,product):
    # get list of days from dataBase to compare if exist 
    days = list(HolidaysCalendar.objects.values_list('holidaysDate',flat=True))
    # get list of product_id from database to compare if exist
    products =list(HolidaysCalendar.objects.values_list('product_id',flat=True))
    if request.method=='POST' and 'save-event' in request.POST:
        # get inputs values
        id = request.POST.get('event-index')
        name = request.POST.get('event-name')
        startDate = request.POST.get('event-start-date')
        endDate = request.POST.get('event-end-date')
        # If id exist Update Object if not create new one
        if id:
            #get object HolidaysCalendar
            #first : to get object not queryset 
            holiday=HolidaysCalendar.objects.all().filter(id=id).first() 
            if startDate == endDate:
                startDate= datetime.strptime(startDate,'%m/%d/%Y')
                endDate= datetime.strptime(endDate,'%m/%d/%Y')
                #update attributes values with new values
                holiday.holidaysDate= startDate
                holiday.name=name
                #save
                holiday.save()
        else:
        # add new one day in database
            if startDate == endDate:
                startDate= datetime.strptime(startDate,'%m/%d/%Y')
                endDate= datetime.strptime(endDate,'%m/%d/%Y')
                # check if day and product_id exists in DB don't save else save
                if (startDate.strftime('%Y-%m-%d') in [day.strftime('%Y-%m-%d') for day in days] ) and (int(product) in products):
                    exist_day =HolidaysCalendar.undeleted_objects.all().filter(holidaysDate = startDate,product_id =product) 
                    exist_day.delete()
                    data = HolidaysCalendar(name=name,holidaysDate=startDate,product_id =product)
                    data.save()
                else:
                    # delete workdata
                    exist_on_days = WorkData.undeleted_objects.all().filter(date = startDate,product_id =product) 
                    exist_on_days.delete()
                    # delete cycle with date and product_id
                    exist_cycle=Cycle.undeleted_objects.all().filter(work_day = startDate,product_id =product)
                    exist_cycle.delete()
                    data = HolidaysCalendar(name=name,holidaysDate=startDate,product_id =product)
                    data.save()
            # add list of days in database       
            else: 
                startDate=datetime.strptime(startDate,'%m/%d/%Y')
                endDate=datetime.strptime(endDate,'%m/%d/%Y')
                delta= endDate-startDate
                day=""
                for i in range(delta.days+1):
                    day= startDate + timedelta(days=i)
                    # check if day and product_id exists in DB don't save else save
                    if (day.strftime('%Y-%m-%d') in [day.strftime('%Y-%m-%d') for day in days]) and (int(product) in products):
                        exist_day =HolidaysCalendar.undeleted_objects.all().filter(holidaysDate = day,product_id =product) 
                        exist_day.delete()
                        data = HolidaysCalendar(name=name,holidaysDate=day,product_id =product)
                        data.save()
                    else :
                        exist_on_days = WorkData.undeleted_objects.all().filter(date = day,product_id =product) 
                        exist_on_days.delete()
                        # delete cycle with date and product_id
                        exist_cycle=Cycle.undeleted_objects.all().filter(work_day = day,product_id =product)
                        exist_cycle.delete()
                        data = HolidaysCalendar(name=name,holidaysDate=day,product_id =product)
                        data.save()
    return redirect("../calendar")


# delete day (holiday or workdata and cycle)
def delete_day(request,division,product):  
    if request.method =="POST"  and 'delete' in request.POST:
        # get id value from form
        id = request.POST.get('date_id')
        # get name from form 
        date_type = request.POST.get('date_type')
        #get cycle id from form
        cycle_id = request.POST.getlist('cycle_id')
        # get cycle object by id 
        for i in cycle_id:
            obj_cycle = get_object_or_404(Cycle, id = i)
            # delete cycle object
            obj_cycle.soft_delete()
        model = WorkData if date_type=='Work Day' else HolidaysCalendar
        obj = get_object_or_404(model, id = id)
        # delete object
        obj.soft_delete()
        # redirect to calendar 
    return redirect("../calendar")
    
#********************Custom calendar**************************

#duplicate calendar : 
# delete old data( holidayscalendar, workdata, cycle) and get data from calendar and save new data
def duplicate_calendar(request,division,product):
    #Delete custom holidays
    custom_holidays = HolidaysCalendar.undeleted_objects.all().filter(product_id = product,owner = 'marwa')
    custom_holidays.delete()
    ##Delete custom workday
    work = WorkData.undeleted_objects.all().filter(product_id = product,owner = 'marwa')
    work.delete()
    # delete custom cycle 
    cycle = Cycle.undeleted_objects.all().filter(product_id = product,owner = 'marwa')
    cycle.delete()
    #save data for loop holidays
    holidays = HolidaysCalendar.undeleted_objects.all().filter(product_id = product)
    for data in holidays:
        custom_holidays = HolidaysCalendar(name=data.name,holidaysDate=data.holidaysDate,product_id =data.product_id,owner = 'marwa')
        custom_holidays.save()
    #save data for loop work
    work = WorkData.undeleted_objects.all().filter(product_id = product)  
    for data in work:
        custom_work_data = WorkData(date=data.date,startTime=data.startTime,endTime=data.endTime,FTEhourByDay=data.FTEhourByDay,ExtraHour=data.ExtraHour,Absenteeism_ratio=data.Absenteeism_ratio,Unproductiveness_ratio=data.Unproductiveness_ratio,Efficienty_ratio=data.Efficienty_ratio,product_id =data.product_id,owner = 'marwa')
        custom_work_data.save()
        # get cycle object with product_id and workdata_id 
        cycles = Cycle.undeleted_objects.all().filter(product_id = product, workdata_id=data.id) 
        # save cycle with new value of workdata_id 
        for cycle in cycles:
            custom_cycle= Cycle(work_day=cycle.work_day,division=cycle.division,profit_center=cycle.profit_center,smooth_family=cycle.smooth_family,cycle_time=cycle.cycle_time, workdata_id=custom_work_data.id,product_id = product, owner = 'marwa')
            custom_cycle.save()
    #call function create new holiday object        
    create_custom_calendar(request,division,product)
    #call function create new work data object 
    custom_work(request,division,product)
    return redirect("../customcalendar")

#custom calendar
def custom_calendar(request,division,product):
    #get smooth family
    smooth_family = Material.undeleted_objects.filter(product_id = product).values('Smooth_Family').distinct().order_by('Smooth_Family')
    #  get cycle data objects
    cycle= Cycle.undeleted_objects.all().filter(product_id = product ,owner = 'marwa')
    # material_data=Material.undeleted_objects.filter(product_id = product).values('Smooth_Family').distinct().order_by('Smooth_Family')
    # get all holiday objects to display in Calendar
    holidays = HolidaysCalendar.undeleted_objects.all().filter(product_id = product , owner = 'marwa') 
    # get all work data objects to display in Calendar    
    work = WorkData.undeleted_objects.all().filter(product_id = product ,owner = 'marwa')
    product_info = Product.objects.all().filter(id=product).first()  
    return render(request,"app/calendar/custom_calendar.html",{'product':product,'division':division,'holidays':holidays,'work':work,'smooth_family': smooth_family,'cycle':cycle,'product_info':product_info,'username':username(request)})
    
#create custom calendar
def create_custom_calendar(request,division,product):
    # get list of days from dataBase to compare if exist 
    days = list(HolidaysCalendar.objects.values_list('holidaysDate',flat=True))
    # get list of product_id from database to compare if exist
    products =list(HolidaysCalendar.objects.values_list('product_id',flat=True)) 
    if request.method=='POST' and 'save-event' in request.POST:
        # get inputs values
        id = request.POST.get('event-index')
        owner = request.POST.get('owner')
        name = request.POST.get('event-name')
        startDate = request.POST.get('event-start-date')
        endDate = request.POST.get('event-end-date')
        # If id exist Update Object if not create new one
        if id:
            #get object work data
            #first : to get object not queryset 
            holiday=HolidaysCalendar.objects.all().filter(id=id).first()  #intilisation object
            if startDate == endDate:
                startDate= datetime.strptime(startDate,'%m/%d/%Y')
                endDate= datetime.strptime(endDate,'%m/%d/%Y')
                #update attributes values with new values
                holiday.holidaysDate= startDate
                holiday.name=name
                #save
                holiday.save()
                return redirect("../customcalendar")
        else:
            # add one day in database
            if startDate == endDate:
                startDate= datetime.strptime(startDate,'%m/%d/%Y')
                endDate= datetime.strptime(endDate,'%m/%d/%Y')
                # check if day and product_id exists in DB don't save else save
                if (startDate.strftime('%Y-%m-%d') in [day.strftime('%Y-%m-%d') for day in days] ) and (int(product) in products):
                    exist_day =HolidaysCalendar.undeleted_objects.all().filter(holidaysDate = startDate,product_id =product,owner = 'marwa') 
                    exist_day.delete()
                    data = HolidaysCalendar(name=name,holidaysDate=startDate,product_id =product, owner = owner)
                    data.save()
                else:
                    exist_on_days = WorkData.undeleted_objects.all().filter(date = startDate,product_id =product,owner = 'marwa') 
                    exist_on_days.delete()
                    exist_cycle=Cycle.undeleted_objects.all().filter(work_day = startDate,product_id =product,owner = 'marwa')
                    exist_cycle.delete()
                    data = HolidaysCalendar(name=name,holidaysDate=startDate,product_id =product, owner = owner)
                    data.save()
            # add list of days in database       
            else: 
                startDate=datetime.strptime(startDate,'%m/%d/%Y')
                endDate=datetime.strptime(endDate,'%m/%d/%Y')
                delta= endDate-startDate
                day=""
                for i in range(delta.days+1):
                    day= startDate + timedelta(days=i)
                    # check if day and product_id exists in DB don't save else save
                    if (day.strftime('%Y-%m-%d') in [day.strftime('%Y-%m-%d') for day in days]) and (int(product) in products):
                        #delete exist data and save new objects
                        exist_day =HolidaysCalendar.undeleted_objects.all().filter(holidaysDate = day,product_id =product, owner = 'marwa') 
                        exist_day.delete()
                        data = HolidaysCalendar(name=name,holidaysDate=day,product_id =product, owner = owner)
                        data.save()   
                    else :
                        exist_on_days = WorkData.undeleted_objects.all().filter(date = day,product_id =product,owner = 'marwa') 
                        exist_on_days.delete()
                        exist_cycle=Cycle.undeleted_objects.all().filter(work_day = day,product_id =product,owner = 'marwa')
                        exist_cycle.delete()
                        data = HolidaysCalendar(name=name,holidaysDate=day,product_id =product, owner = owner)
                        data.save()    
    return redirect("../customcalendar")

# delete day (holiday or work) for custom
def delete_day_custom(request,division,product):  
    if request.method =="POST"  and 'delete-custom' in request.POST:
        # get id value from form
        id = request.POST.get('date_id')
        date_type = request.POST.get('date_type')
        #get cycle id from form
        cycle_id = request.POST.getlist('cycle_id')
        #get cycle object by id
        for i in cycle_id:
            obj_cycle = get_object_or_404(Cycle, id = i)
            # delete object
            obj_cycle.soft_delete()
        model = WorkData if date_type=='Work Day' else HolidaysCalendar
        obj = get_object_or_404(model, id = id)
        # delete object
        obj.soft_delete()
        # redirect to calendar 
    return redirect("../customcalendar")


#********************work Data***********************************
# clacul work hours (when type of cycle = Days)
def work_hours(start_time,end_time):
    if start_time == end_time:
        return 24
    elif end_time > start_time:
        return ((end_time - start_time).total_seconds() / 3600)
    else:
        return ((end_time+ timedelta(days =1)) - start_time ).total_seconds() / 3600

#create work data for calendar
def work_data(request,division,product):
    work = WorkData.undeleted_objects.all().filter(product_id = product, owner ='officiel') 
    # get list of days from dataBase to compare if exist 
    days = list(work.values_list('date',flat=True))
    # get list of product_id from database to compare if exist
    products =list(WorkData.objects.values_list('product_id',flat=True))
    # test if method post and button save-work
    if request.method=='POST' and 'save-work' in request.POST:
        # get inputs from form
        #    workdata informations
        id= request.POST.get('event-index')
        startTime= request.POST.get('start-time')
        endTime= request.POST.get('end-time')
        fte= request.POST.get('fte')
        extraHours= request.POST.get('extra-hours')
        AbsenteeismRatio= request.POST.get('Absenteeism-ratio')
        UnproductivenessRatio= request.POST.get('Unproductiveness-ratio')
        EfficientyRatio= request.POST.get('Efficienty-ratio')
        startDate= request.POST.get('event-start-date')
        endDate= request.POST.get('event-end-date')
        #cycle informations
        profit_center= Product.objects.all().filter(id = product).values('Profit_center').first()
        smooth_family= request.POST.getlist('smooth_family')
        cycle_time = request.POST.getlist('cycle_time')
        cycle_id= request.POST.getlist('cycle_id')
        # convert starttime and endtime(str) to datetime
        start_time= datetime.strptime(startTime, '%H:%M:%S')
        end_time= datetime.strptime(endTime, '%H:%M:%S')
       
       
        # If id exist Update Object if not create new one
        if id and cycle_id:
            # get object workdata
            #first : to get object not queryset 
            work_day=WorkData.objects.all().filter(id=id).first()  #intilisation object
            if startDate == endDate:
                startDate= datetime.strptime(startDate,'%m/%d/%Y')
                endDate= datetime.strptime(endDate,'%m/%d/%Y')
                #update attributes values with new values
                #update cycle
                work_day.FTEhourByDay=fte
                work_day.date= startDate
                work_day.ExtraHour=extraHours
                work_day.Absenteeism_ratio=AbsenteeismRatio
                work_day.Unproductiveness_ratio=UnproductivenessRatio
                work_day.Efficienty_ratio=EfficientyRatio
                work_day.startTime=startTime
                work_day.endTime=endTime
                work_day.save()
                # update cycle
                # convert two list in dict
                cycle_dict = dict(zip(cycle_id, cycle_time))
                for key,value in cycle_dict.items(): 

                    # get cycle object with key
                    cycle_info= Cycle.objects.all().filter(id=key).first()  #intilisation object
                    cycle_type_input = request.POST.get('cycle-type-'+cycle_info.smooth_family)
                    if cycle_type_input == 'Days':
                        # update cycle_time
                        # cycle_info.cycle_time=float(value) * 16
                        cycle_info.cycle_time= float(value) * work_hours(start_time,end_time)
                    if cycle_type_input =='Hours':
                        cycle_info.cycle_time= float(value)
                    cycle_info.save()
                        
                return redirect("../calendar")
        # create new object         
        else :
            # add one day in database
            if startDate == endDate:
                startDate= datetime.strptime(startDate,'%m/%d/%Y')
                endDate= datetime.strptime(endDate,'%m/%d/%Y')
                # check if day and product_id exists in DB delete and save new data
                if (startDate.strftime('%Y-%m-%d') in [day.strftime('%Y-%m-%d') for day in days] ) and (int(product) in products):
                   # delete exist data and save new data 
                   # delete work data with date and product_id 
                    exist_day =WorkData.undeleted_objects.all().filter(date = startDate,product_id = product,owner = 'officiel') 
                    exist_day.delete()
                    # delete cycle with date and profit center
                    exist_cycle=Cycle.undeleted_objects.all().filter(work_day = startDate,profit_center = profit_center.get('Profit_center'),owner = 'officiel')
                    exist_cycle.delete()
                    #Save into Workdata table
                    data = WorkData(date=startDate,startTime=startTime,endTime=endTime,FTEhourByDay=fte,ExtraHour=extraHours,Absenteeism_ratio=AbsenteeismRatio,Unproductiveness_ratio=UnproductivenessRatio, Efficienty_ratio=EfficientyRatio,product_id =product)
                    data.save()
                    #Save into Cycle table
                    # loop two list smooth_family and cycle_time
                    for i,j in zip(smooth_family,cycle_time):
                        cycle_type_input = request.POST.get('cycle-type-'+i)
                        if cycle_type_input == 'Days':
                            # new_cycle_time= float(j) * (endTime - startTime)
                            cycle_info.cycle_time=float(value) * work_hours(start_time,end_time)
                        if cycle_type_input == 'Hours':
                            new_cycle_time=j
                        cycle_data=Cycle(work_day=startDate,division=division,profit_center=profit_center.get('Profit_center'),smooth_family=i,cycle_time=new_cycle_time,workdata_id=data.id,product_id = product)
                        cycle_data.save()
                    
                    return redirect("../calendar")
                else:
                    ##replace holidays with work data
                    exist_off_days = HolidaysCalendar.undeleted_objects.all().filter(holidaysDate= startDate,product_id = product) 
                    exist_off_days.delete()
                    #Save into Workdata table
                    data = WorkData(date=startDate,startTime=startTime,endTime=endTime,FTEhourByDay=fte,ExtraHour=extraHours,Absenteeism_ratio=AbsenteeismRatio,Unproductiveness_ratio=UnproductivenessRatio, Efficienty_ratio=EfficientyRatio,product_id =product)
                    data.save()
                    for i,j in zip(smooth_family,cycle_time):
                        cycle_type_input = request.POST.get('cycle-type-'+i)
                        if cycle_type_input == 'Days':
                            new_cycle_time= float(j) * work_hours(start_time,end_time)
                        if cycle_type_input == 'Hours':
                            new_cycle_time=j
                        cycle_data=Cycle(work_day=startDate,division=division,profit_center=profit_center.get('Profit_center'),smooth_family=i,cycle_time=new_cycle_time,workdata_id=data.id,product_id = product)
                        cycle_data.save()    
                    return redirect("../calendar")
            # add list of days in database       
            else: 
                startDate=datetime.strptime(startDate,'%m/%d/%Y')
                endDate=datetime.strptime(endDate,'%m/%d/%Y')
                delta= endDate-startDate
                day=""
                for i in range(delta.days+1):
                    day= startDate + timedelta(days=i)
                    # check if day and product_id exists delete old object and save new workday and cycle object
                    if (day.strftime('%Y-%m-%d') in [day.strftime('%Y-%m-%d') for day in days]) and (int(product) in products):
                        # delete exist workdata and save new workdata
                        exist_days = WorkData.undeleted_objects.all().filter(date = day,product_id = product,owner = 'officiel' ) 
                        exist_days.delete()
                        # delete exist cycle and save new cycle object
                        exist_cycle=Cycle.undeleted_objects.all().filter(work_day = day,profit_center = profit_center.get('Profit_center'),owner = 'officiel')
                        exist_cycle.delete()
                        # Save into workdata table
                        data = WorkData(date=day,startTime=startTime,endTime=endTime,FTEhourByDay=fte,ExtraHour=extraHours,Absenteeism_ratio=AbsenteeismRatio,Unproductiveness_ratio=UnproductivenessRatio, Efficienty_ratio=EfficientyRatio,product_id =product)
                        data.save()
                        #Save into Cycle table
                        for i,j in zip(smooth_family,cycle_time):
                            cycle_type_input = request.POST.get('cycle-type-'+i)
                            if cycle_type_input == 'Days':
                                new_cycle_time= float(j) * work_hours(start_time,end_time)
                            if cycle_type_input == 'Hours':
                                new_cycle_time=j
                            cycle_data=Cycle(work_day=day,division=division,profit_center=profit_center.get('Profit_center'),smooth_family=i,cycle_time=new_cycle_time,workdata_id=data.id,product_id = product)
                            cycle_data.save()    
                    else :
                        #replace holidays with work data
                        #get holidays 
                        exist_off_days = HolidaysCalendar.undeleted_objects.all().filter(holidaysDate = day, product_id = product, owner = 'officiel' ) 
                        #delete exist_off_days
                        exist_off_days.delete()
                        #save into workdata data
                        data = WorkData(date=day,startTime=startTime,endTime=endTime,FTEhourByDay=fte,ExtraHour=extraHours,Absenteeism_ratio=AbsenteeismRatio,Unproductiveness_ratio=UnproductivenessRatio, Efficienty_ratio=EfficientyRatio,product_id =product)
                        data.save()
                        #Save into Cycle table
                        for i,j in zip(smooth_family,cycle_time):
                            cycle_type_input = request.POST.get('cycle-type-'+i)
                            if cycle_type_input == 'Days':
                                print('*****j',j)
                                new_cycle_time= float(j) * work_hours(start_time,end_time)
                            if cycle_type_input == 'Hours':
                                new_cycle_time=j
                            cycle_data=Cycle(work_day=day,division=division,profit_center=profit_center.get('Profit_center'),smooth_family=i,cycle_time=new_cycle_time,workdata_id=data.id,product_id = product)
                            cycle_data.save()  
                return redirect("../calendar")       

#********************custom work data****************************

#create work data for custom calendar
def custom_work(request,division,product):
    # get all work data objects to display in Calendar
    work = WorkData.undeleted_objects.all().filter(product_id = product ,owner = 'marwa') 
    # get list of days from dataBase to compare if exist 
    days = list(work.values_list('date',flat=True))
    # get list of product_id from database to compare if exist
    products =list(WorkData.objects.values_list('product_id',flat=True))       
    if request.method=='POST' and 'save' in request.POST:
        # get inputs values
        # workdata informations
        id = request.POST.get('event-index')
        owner = request.POST.get('owner')
        startTime = request.POST.get('start-time')
        endTime = request.POST.get('end-time')
        fte = request.POST.get('fte')
        extraHours = request.POST.get('extra-hours')
        AbsenteeismRatio = request.POST.get('Absenteeism-ratio')
        UnproductivenessRatio = request.POST.get('Unproductiveness-ratio')
        EfficientyRatio = request.POST.get('Efficienty-ratio')
        startDate = request.POST.get('event-start-date')
        endDate = request.POST.get('event-end-date')
        #cycle informations
        profit_center= Product.objects.all().filter(id = product).values('Profit_center').first()
        smooth_family= request.POST.getlist('smooth_family')
        cycle_time = request.POST.getlist('cycle_time')
        cycle_id = request.POST.getlist('cycle_id')
        # convert startTime and endTime to datetime 
        start_time = datetime.strptime(startTime, '%H:%M:%S')
        end_time = datetime.strptime(endTime, '%H:%M:%S')

        # if id update else save
        if id:
            #get object work data
            #first : to get object not queryset 
            work_day=WorkData.objects.all().filter(id=id).first()  #intilisation object
            if startDate == endDate:
                startDate= datetime.strptime(startDate,'%m/%d/%Y')
                endDate= datetime.strptime(endDate,'%m/%d/%Y')
                #update attributes values with new values
                work_day.FTEhourByDay=fte
                work_day.date= startDate
                work_day.ExtraHour=extraHours
                work_day.Absenteeism_ratio=AbsenteeismRatio
                work_day.Unproductiveness_ratio=UnproductivenessRatio
                work_day.Efficienty_ratio=EfficientyRatio
                work_day.cycle_time=cycle_time
                work_day.startTime=startTime
                work_day.endTime=endTime
                work_day.save()
                # update cycle
                # convert two list in dict
                cycle_dict = dict(zip(cycle_id, cycle_time))
                for key,value in cycle_dict.items(): 
                    # get cycle object with key
                    cycle_info= Cycle.objects.all().filter(id=key).first()  #intilisation object
                    cycle_type_input = request.POST.get('cycle-type-'+cycle_info.smooth_family)
                    if cycle_type_input == 'Days':
                        # update cycle_time
                        cycle_info.cycle_time=float(value) * work_hours(start_time,end_time)
                    if cycle_type_input =='Hours':
                        cycle_info.cycle_time= float(value)
                    cycle_info.save()
                return redirect("../customcalendar")
        # create new object         
        else : 
            # add one day in database
            if startDate == endDate:
                startDate= datetime.strptime(startDate,'%m/%d/%Y')
                endDate= datetime.strptime(endDate,'%m/%d/%Y')
                    # check if day and product_id exists in DB don't save else save
                if (startDate.strftime('%Y-%m-%d') in [day.strftime('%Y-%m-%d') for day in days] ) and (int(product) in products):
                    # delete workdata with date and product_id and owner
                    exist_day =WorkData.undeleted_objects.all().filter(date = startDate, product_id = product, owner = 'marwa') 
                    exist_day.delete()
                    # delete cycle with date and profit center
                    exist_cycle=Cycle.undeleted_objects.all().filter(work_day = startDate,profit_center = profit_center.get('Profit_center'),owner = 'marwa')
                    exist_cycle.delete()
                    # Save into workdata table
                    data = WorkData(date=startDate,startTime=startTime,endTime=endTime,FTEhourByDay=fte,ExtraHour=extraHours,Absenteeism_ratio=AbsenteeismRatio,Unproductiveness_ratio=UnproductivenessRatio, Efficienty_ratio=EfficientyRatio,product_id =product,owner = owner)
                    data.save()
                    #Save into Cycle table
                    for i,j in zip(smooth_family,cycle_time):
                        cycle_type_input = request.POST.get('cycle-type-'+i)
                        if cycle_type_input == 'Days':
                            new_cycle_time= float(j) * work_hours(start_time,end_time)
                        if cycle_type_input == 'Hours':
                            new_cycle_time=j
                        cycle_data=Cycle(work_day=startDate,division=division,profit_center=profit_center.get('Profit_center'),smooth_family=i,cycle_time=new_cycle_time,workdata_id=data.id,owner = owner,product_id = product)
                        cycle_data.save()
                    
                    return redirect("../customcalendar")
                else:
                    #replace holiday with workdata
                    exist_off_days = HolidaysCalendar.undeleted_objects.all().filter(holidaysDate= startDate,product_id = product, owner = 'marwa') 
                    #delete holidays
                    exist_off_days.delete()
                    #save data work object
                    data = WorkData(date=startDate,startTime=startTime,endTime=endTime,FTEhourByDay=fte,ExtraHour=extraHours,Absenteeism_ratio=AbsenteeismRatio,Unproductiveness_ratio=UnproductivenessRatio, Efficienty_ratio=EfficientyRatio,product_id =product,owner = owner)
                    data.save()
                    #Save into Cycle table
                    for i,j in zip(smooth_family,cycle_time):
                        cycle_type_input = request.POST.get('cycle-type-'+i)
                        if cycle_type_input == 'Days':
                            new_cycle_time= float(j) * work_hours(start_time,end_time)
                        if cycle_type_input == 'Hours':
                            new_cycle_time=j
                        cycle_data=Cycle(work_day=startDate,division=division,profit_center=profit_center.get('Profit_center'),smooth_family=i,cycle_time=new_cycle_time,workdata_id=data.id,owner = owner,product_id = product)
                        cycle_data.save() 
                    return redirect("../customcalendar")
            # add list of days in database       
            else: 
                startDate=datetime.strptime(startDate,'%m/%d/%Y')
                endDate=datetime.strptime(endDate,'%m/%d/%Y')
                delta= endDate-startDate
                day=""
                for i in range(delta.days+1):
                    day= startDate + timedelta(days=i)
                    # check if day and product_id exists in DB delete old objects of workdata and cycle and save new objects
                    if (day.strftime('%Y-%m-%d') in [day.strftime('%Y-%m-%d') for day in days]) and (int(product) in products):
                        # delete workdata object
                        exist_days = WorkData.undeleted_objects.all().filter(date = day,product_id = product,owner = 'marwa') 
                        exist_days.delete()
                        # delete cycle with date and profit center
                        exist_cycle=Cycle.undeleted_objects.all().filter(work_day = day,profit_center = profit_center.get('Profit_center'),owner = 'marwa')
                        exist_cycle.delete()
                        # save into workdata table
                        data = WorkData(date=day,startTime=startTime,endTime=endTime,FTEhourByDay=fte,ExtraHour=extraHours,Absenteeism_ratio=AbsenteeismRatio,Unproductiveness_ratio=UnproductivenessRatio, Efficienty_ratio=EfficientyRatio,product_id =product,owner = owner)
                        data.save()
                        # save into cycle object 
                        for i,j in zip(smooth_family,cycle_time):
                            cycle_type_input = request.POST.get('cycle-type-'+i)
                        if cycle_type_input == 'Days':
                            new_cycle_time= float(j) * work_hours
                        if cycle_type_input == 'Hours':
                            new_cycle_time=j  
                            cycle_data=Cycle(work_day=day,division=division,profit_center=profit_center.get('Profit_center'),smooth_family=i,cycle_time=new_cycle_time,workdata_id=data.id,owner = owner,product_id = product)
                            cycle_data.save() 
                    else :
                        #replace holidays with work data
                        #get holidays 
                        exist_off_days = HolidaysCalendar.undeleted_objects.all().filter(holidaysDate = day,product_id = product,owner = 'marwa') 
                        #delete exist_off_days
                        exist_off_days.delete()
                        #save work data
                        data = WorkData(date=day,startTime=startTime,endTime=endTime,FTEhourByDay=fte,ExtraHour=extraHours,Absenteeism_ratio=AbsenteeismRatio,Unproductiveness_ratio=UnproductivenessRatio, Efficienty_ratio=EfficientyRatio,product_id =product,owner = owner)
                        data.save()
                        # save into cycle object 
                        for i,j in zip(smooth_family,cycle_time):
                            cycle_type_input = request.POST.get('cycle-type-'+i)
                            if cycle_type_input == 'Days':
                                new_cycle_time= float(j) * work_hours(start_time,end_time)
                            if cycle_type_input == 'Hours':
                                new_cycle_time=j
                            cycle_data=Cycle(work_day=day,division=division,profit_center=profit_center.get('Profit_center'),smooth_family=i,cycle_time=new_cycle_time,workdata_id=data.id,owner = owner,product_id = product)
                            cycle_data.save() 
                return redirect("../customcalendar")
    return render(request,"app/calendar/custom_calendar.html",{'product':product,'division':division, 'work':work,'username':username(request)}) 

#***********CRUD CalendarConfigurationTraitement*****************

# add new object(CalendarConfigurationTraitement)
def create_conf_trait(request,division,product):
    form = CalendarConfigurationTreatementForm(request.POST)
    if request.method == "POST":
     if form.is_valid():
        instance=form.save(commit=False)
        instance.product_id = product
        instance.save()
        messages.success(request,"CalendarConfigurationTraitement created successfully!")
     else:
         messages.error(request,"Form not valid! try again")
    return redirect(f'../{product}/configTrait')
    

#update object(CalendarConfigurationTraitement) by id
def update_conf_trait(request,division):  
    #get id
    id = request.POST.get('id')
    # fetch the object related to passed id
    obj = get_object_or_404(CalendarConfigurationTreatement, id = id)
    # pass the object as instance in form
    form = CalendarConfigurationTreatementForm(request.POST or None, instance = obj)
    if request.method == "POST":
        if form.is_valid():
            form.save()
            messages.success(request,"CalendarConfigurationTraitement updated successfully!")   
        else:
          messages.error(request,"try again !")           
    return redirect(f'./{str(obj.product_id)}/configTrait')
    
# delete object (CalendarConfigurationTraitement) by id
def delete_conf_trait(request, division ,id):
    # fetch the object related to passed id
    obj = get_object_or_404(CalendarConfigurationTreatement, id = id)
    # delete object
    obj.soft_delete()
    messages.success(request,"CalendarConfigurationTraitement deleted successfully!")   
    return redirect(f'../{str(obj.product_id)}/configTrait')
    
# restore object (CalendarConfigurationTraitement) by id
def restore_conf_trait(request, division ,id):
    # fetch the object related to passed id
    obj = get_object_or_404(CalendarConfigurationTreatement, id = id)
    # restore object
    obj.restore()
    messages.success(request,"CalendarConfigurationTraitement restored successfully!")   
    return redirect(f'../{str(obj.product_id)}/configTrait')
    
# find all CalendarConfigurationTraitement for product 
def config_trait(request, division,product):
    #get CalendarConfigurationTraitementForm
    form = CalendarConfigurationTreatementForm()
    # undeleted_objects object of soft delete manager
    data = CalendarConfigurationTreatement.objects.filter(product__pk = product ).order_by('id')   
    product_info=Product.objects.all().filter(id=product).first()  
    return render(request, "app/CalendarConfigurationTraitement/home_conf_traitement.html", {'data':data,'division':division,'product':product,'form':form,'product_info':product_info,'username':username(request)})


#***************CRUD CalendarConfigurationCpOrdo*****************

# add new object(CalendarConfigurationCpordo)
def create_conf_cpordo(request,division,product):
    form = CalendarConfigurationCpordoForm(request.POST)
    if request.method == "POST":
        if form.is_valid():
            instance=form.save(commit=False)
            instance.product_id = product
            instance.save()
            messages.success(request,"CalendarConfigurationCpordo created successfully!")
        else:
            messages.error(request,"Form not valid! try again")     
    return redirect(f'../{product}/configCpordo')
    
#update object(CalendarConfigurationCpordo) by id
def update_conf_cpordo(request, division):
    #get id
    id = request.POST.get('id')
    # fetch the object related to passed id
    obj = get_object_or_404(CalendarConfigurationCpordo, id = id)
    # pass the object as instance in form
    form = CalendarConfigurationCpordoForm(request.POST or None, instance = obj)
    if request.method == "POST":
        if form.is_valid():
            form.save()
            messages.success(request,"CalendarConfigurationCpordo updated successfully!")
        else:
            messages.error(request,"try again!")    
    return redirect(f'./{str(obj.product_id)}/configCpordo')
    
# delete object (CalendarConfigurationCpordo) by id
def delete_conf_cpordo(request,division,id):
    # fetch the object related to passed id
    obj = get_object_or_404(CalendarConfigurationCpordo, id = id)
    # delete object
    obj.soft_delete()
    messages.success(request,"CalendarConfigurationCpordo deleted successfully!")
    return redirect(f'../{str(obj.product_id)}/configCpordo')

# restore object (CalendarConfigurationCpordo) by id
def restore_conf_cpordo(request,division,id):
    # fetch the object related to passed id
    obj = get_object_or_404(CalendarConfigurationCpordo, id = id)
    # restore object
    obj.restore()
    messages.success(request,"CalendarConfigurationCpordo restored successfully!")
    return redirect(f'../{str(obj.product_id)}/configCpordo')
    
# find all CalendarConfigurationCpordo for product 
def config_cpordo(request,division,product):
    #get CalendarConfigurationCpordoForm
    form = CalendarConfigurationCpordoForm()
    # undeleted_objects object of soft delete manager
    data = CalendarConfigurationCpordo.objects.filter(product__pk = product ).order_by('id') 
    product_info=Product.objects.all().filter(id=product).first()  
    return render(request, "app/CalendarConfigurationCpordo/home_conf_cpordo.html", {'data':data,'division':division,'product':product,'form':form,'product_info':product_info,'username':username(request)})

#********************** Home***********************************

def home_page(request):

    divisions = Division.undeleted_objects.all()
    division=products=None
    current_user = request.user
    try:
        staff_connected = Staff.objects.values_list('division',flat=True).filter(username ='L0030959').first()
        products= Product.undeleted_objects.all().filter(division__id= staff_connected)
        division= staff_connected

        if request.method == "POST":
            divisionName = request.POST.get('division')
            divisionId = Division.undeleted_objects.values('id').filter(name=divisionName).first()
            products= Product.undeleted_objects.all().filter(division__id= divisionId['id'])
            division=divisionId['id']
    except Exception:
        messages.error(request,"User not connected!")  


    return render(request,'app/home/index.html', {'division':division, 'divisions':divisions,'products':products,'username':username(request)})

#*******************copy calendar*************************
def copy_calendar(request,division,product):
    #Delete holidays
    holidays_data = HolidaysCalendar.objects.all().filter(product_id = product,owner = 'officiel')
    holidays_data.delete()
    #Delete work
    work_data = WorkData.objects.all().filter(product_id = product,owner = 'officiel')
    work_data.delete() 
    # Delete cycle
    cycle_data = Cycle.objects.all().filter(product_id = product,owner = 'officiel')
    cycle_data.delete() 
    #get product copied id 
    product_copied= request.POST.get('product_copied')
    #get holiday object with product id
    holidays_data = HolidaysCalendar.undeleted_objects.all().filter(product_id = product_copied, owner = 'officiel')
    #save holiday object in DB
    for data in holidays_data:
        holidays = HolidaysCalendar(name=data.name,holidaysDate=data.holidaysDate,product_id = product)
        holidays.save()

    #get work data object with product id 
    work = WorkData.undeleted_objects.all().filter(product_id = product_copied ,owner = 'officiel')  
    #save data for loop work
    for data in work:
        work_data = WorkData(date=data.date,startTime=data.startTime,endTime=data.endTime,FTEhourByDay=data.FTEhourByDay,ExtraHour=data.ExtraHour,Absenteeism_ratio=data.Absenteeism_ratio,Unproductiveness_ratio=data.Unproductiveness_ratio,Efficienty_ratio=data.Efficienty_ratio,product_id = product)
        work_data.save()
        # get profit center from product
        # profit_center =Product.undeleted_objects.filter(id=product).values('Profit_center')
        # get cycle object with product_id and workdata_id 
        # cycles = Cycle.undeleted_objects.all().filter(product_id = product_copied, workdata_id=data.id, owner = 'officiel') 
        # save cycle with new value of workdata_id 
        # for cycle in cycles:
        #     custom_cycle= Cycle(work_day=cycle.work_day,division=cycle.division,profit_center=profit_center,smooth_family=cycle.smooth_family,cycle_time=cycle.cycle_time, workdata_id=work_data.id,product_id = product)
        #     custom_cycle.save()  
    return redirect("../calendar")

#*********************Planning Approval************************

#All Planning Approval
def all_planning(request,division,product):
    # to use in info barre
    product_info=Product.objects.all().filter(id=product).first()
    # get all planning from database with product
    all_planning=PlanningApproval.objects.all().filter(product=product)
    #Convert data to dict to get number of versions and shered status and other informations
    planning_informations=[]
    for planning in all_planning:
        informations=dict()
        version_count=[]
        shared_status=[]
        informations['id']=planning.id
        informations['name']=planning.name
        informations['created_at']=planning.created_at
        informations['created_by']=planning.created_by



        for planning in planning.shopfloor_set.all():
            if planning.shared == True:
                informations['shared_version']=planning.version
            version_count.append(planning.version)
            shared_status.append(planning.shared)
            informations['version_count']= len(set(version_count))
            informations['shared_status']=any(set(shared_status))
            informations['last_version']=max(set(version_count))

        planning_informations.append(informations)
    return render(request,'app/Shopfloor/all_planning.html',{'all_planning':all_planning,'division':division,'product':product,'product_info':product_info,'planning_informations':planning_informations,'username':username(request)})
   
#Save new Planning Approval
def new_planning(request,division,product):
    product_info=Product.objects.all().filter(id=product).first() 
    data=None
    # get list of planning name
    planning_approval_name_list=list(PlanningApproval.objects.values_list('name',flat=True).filter(product=product))

    if request.method == "POST":
        planning_name=request.POST.get('name')
        # check if name exist don't save else save
        if planning_name not in planning_approval_name_list:
            data= PlanningApproval(name=planning_name,product_id= product)
            data.save()
            messages.success(request,"Name saved successfully!")
            return redirect(f'../planningapproval/{data.id}/files/uploadcoois')
        else:
            messages.error(request,"Name exist! try again")
            return redirect('../newplanning')
    return render(request,'app/Shopfloor/new_planning.html',{'division':division,'product':product,'product_info':product_info,'username':username(request)})

#To DO
def update_planning(request,division,product,planningapproval):
    
    planning_approval_name_list=list(PlanningApproval.objects.values_list('name',flat=True).filter(product=product))

    return render(request,'app/Shopfloor/new_planning.html',{'division':division,'product':product, 'username':username(request)})


#*********************Upload To DB COOIS************************
# From upload coois
def upload_coois(request,division,product,planningapproval):  
    coois_files= Coois.objects.filter(product_id = product, product__division = division,planning_approval_id=planningapproval).values('created_at','created_by').distinct() 
    # planning approval for info page
    planningapproval_info=PlanningApproval.objects.all().filter(id=planningapproval).first() 
    if request.method == 'POST' and request.FILES['coois']:
        # Delete coois data 
        coois_data = Coois.undeleted_objects.all().filter(product=product,created_by='Marwa',planning_approval_id=planningapproval)
        coois_data.delete()
        file=request.FILES['coois']
        try:
            conn = psycopg2.connect(host='localhost',dbname='mps_db',user='postgres',password='054Ibiza',port='5432')
            import_coois(file,conn,product,planningapproval)
            messages.success(request,"COOIS file uploaded successfully!") 
            return redirect('./uploadzpp')
        except Exception:
            messages.error(request,"unable to upload files, not exist or unreadable") 
 
    return render(request,'app/files/coois.html',{'planningapproval_info':planningapproval_info,'division':division,'product':product,'planningapproval':planningapproval,'coois_files':coois_files,'username':username(request)})  

def import_coois(file,conn,product,planningapproval):
    #read file with pandas
    dc=pd.read_excel(file)
    #insert informations into file
    dc.insert(0,'created_at',datetime.now())
    dc.insert(1,'updated_at',datetime.now())
    dc.insert(2,'created_by','Marwa')
    dc.insert(3,'updated_by','Marwa')
    dc.insert(4,'is_deleted',False)
    dc.insert(5,'deleted_by','Marwa')
    dc.insert(6,'deleted_at',datetime.now())
    dc.insert(7,'restored_at',datetime.now())
    dc.insert(8,'restored_by','Marwa')
    dc.insert(24,'product_id',product)
    dc.insert(25,'planning_approval_id',planningapproval)

    # Using the StringIO method to set
    # as file object
    # print(dc.head(10))
    coois = StringIO()
    #convert file to csv
    coois.write(dc.to_csv(index=None , header=None))
    # This will make the cursor at index 0
    coois.seek(0)
    with conn.cursor() as c:
        c.copy_from(
            file=coois,
            #file name in DB
            table="app_coois",
            columns=[
                'created_at',
                'updated_at',
                'created_by',
                'updated_by',
                'is_deleted',
                'deleted_by',
                'deleted_at',
                'restored_at',
                'restored_by',
                'division',
                'profit_centre',
                'order',
                'material',
                'designation',
                'order_type',
                'order_quantity',
                'date_start_plan',
                'date_end_plan',
                'fixation',
                'manager',
                'order_stat',
                'customer_order',
                'date_end_real',
                'entered_by',
                'product_id',
                'planning_approval_id',
                
            ],

            null="",
            sep=",",

        )
    conn.commit()       

#*********************Upload TO DB ZPP************************
# Form upload zpp 
def upload_zpp(request,division,product,planningapproval):  
    zpp_files= Zpp.objects.filter(product_id = product, product__division = division,planning_approval_id=planningapproval).values('created_at','created_by').distinct()
    # planning approval for info page
    planningapproval_info=PlanningApproval.objects.all().filter(id=planningapproval).first()  

    if request.method == 'POST' and request.FILES['zpp']:
        file=request.FILES['zpp']
        #Delete zpp data 
        zpp_data = Zpp.undeleted_objects.all().filter(product=product,created_by='Marwa',planning_approval_id=planningapproval)
        zpp_data.delete()
        #Save file to DB
        try:
            conn = psycopg2.connect(host='localhost',dbname='mps_db',user='postgres',password='054Ibiza',port='5432')
            import_zpp(file,conn,product,planningapproval)
            messages.success(request,"ZPP file uploaded successfully!") 
            return redirect("../needs")    
        except Exception:
            messages.error(request,"unable to upload ZPP files, not exist or unreadable") 

    return render(request,'app/files/zpp.html',{'planningapproval_info':planningapproval_info,'division':division,'product':product,'planningapproval':planningapproval, 'zpp_files':zpp_files,'username':username(request)})  


def import_zpp(file,conn,product,planningapproval):

    #read file with pandas
    # to read csv because the type of zpp file is text
    dc=pd.read_csv(file.temporary_file_path(),header=0,skiprows=4,encoding='UTF-16 LE', error_bad_lines=False, sep ='\t', names=['A','material','plan_date','B','element','data_element_planif','message','needs','qte_available','date_reordo','supplier','customer'])
    # to drop empty columns
    dc=dc.drop(columns=['A','B',])
    
    # dc.rename(columns ={'material','plan_date','element','data_element_planif','message','needs','qte_available','date_reordo','supplier','customer'} , inplace=True)
    #insert informations into file
    dc.insert(0,'created_at',datetime.now())
    dc.insert(1,'updated_at',datetime.now())
    dc.insert(2,'created_by','Marwa')
    dc.insert(3,'updated_by','Marwa')
    dc.insert(4,'is_deleted',False)
    dc.insert(5,'deleted_by','Marwa')
    dc.insert(6,'deleted_at',datetime.now())
    dc.insert(7,'restored_at',datetime.now())
    dc.insert(8,'restored_by','Marwa')
    dc.insert(19,'product_id',product)
    dc.insert(20,'planning_approval_id',planningapproval)

    
    # delete the slash and the part after the slash
    dc['data_element_planif']= dc['data_element_planif'].astype(str).str.split("/").str[0]
    # delete the zeros on the left
    dc['data_element_planif']= dc['data_element_planif'].astype(str).str.lstrip("0")

    dc['needs']= dc['needs'].astype(str).str.split(",").str[0]
    dc['needs']= dc['needs'].astype(str).str.lstrip("1")
    dc['qte_available']= dc['qte_available'].astype(str).str.split(",").str[0]
    dc['qte_available']= dc['qte_available'].astype(str).str.lstrip("1")
    
    # dc.to_csv('zpp_test.csv')
    
    # Using the StringIO method to set
    # as file object
    zpp = StringIO()
    #convert file to csv
    zpp.write(dc.to_csv(index=None , header=None, sep=';'))
    # This will make the cursor at index 0
    zpp.seek(0)
    with conn.cursor() as c:
        c.copy_from(
            file=zpp,
            #file name in DB
            table="app_zpp",
            columns=[
                'created_at',
                'updated_at',
                'created_by',
                'updated_by',
                'is_deleted',
                'deleted_by',
                'deleted_at',
                'restored_at',
                'restored_by',
                'material',
                'plan_date',
                'element',
                'data_element_planif',
                'message',
                'needs',
                'qte_available',
                'date_reordo',
                'supplier',
                'customer', 
                'product_id',
                'planning_approval_id',  
            ],
            null="",
            sep=";",
            

        )
    conn.commit()


#******************Shopfloor and smoothing****************

# @allowed_users(allowed_roles=["Planificateur"])
# merge between coois and zpp and material
def needs(request,division,product,planningapproval):
    # to diplay for info page
    planningapproval_info=PlanningApproval.objects.all().filter(id=planningapproval).first()  
    # data for merge
    zpp_data=Zpp.objects.filter(created_by= 'Marwa',product=product,planning_approval_id=planningapproval).values('material','data_element_planif','created_by','message','date_reordo','product__Profit_center','product__division__name')
    coois_data= Coois.objects.all().filter(created_by= 'Marwa',product=product,planning_approval_id=planningapproval).values()
    material_data=Material.undeleted_objects.values('material','product__Profit_center','product__division__name','created_by','workstation','AllocatedTime','Leadtime','Allocated_Time_On_Workstation','Smooth_Family').filter(product=product)
    #  check if data existe
    if zpp_data and coois_data and material_data:
       
        #to Convert data to DataFrame
        df_zpp=pd.DataFrame(list(zpp_data))
        df_coois=pd.DataFrame(list(coois_data))
        df_material=pd.DataFrame(list(material_data))
        
        # rename df_material column 
        df_material=df_material.rename(columns={'product__division__name':'division','product__Profit_center':'profit_center'})
        # rename df_zpp column 
        df_zpp=df_zpp.rename(columns={'product__division__name':'division','product__Profit_center':'profit_center'})
        
        # add column key for zpp (concatinate  material and data_element_planif and created_by)
        df_zpp['key']=df_zpp['material'].astype(str)+df_zpp['division'].astype(str)+df_zpp['profit_center'].astype(str)+df_zpp['data_element_planif'].astype(str)+df_zpp['created_by'].astype(str)
        #add column key for coois (concatinate material, order, created_by)    
        df_coois['key']=df_coois['material'].astype(str)+df_coois['division'].astype(str)+df_coois['profit_centre'].astype(str)+df_coois['order'].astype(str)+df_coois['created_by'].astype(str)

        # add column key for material (concatinate material, created_by)  
        df_material['key']=df_material['material'].astype(str)+df_material['division'].astype(str)+df_material['profit_center'].astype(str)+df_material['created_by'].astype(str)
        #add column key for coois (concatinate material,division,profit_centre, created_by )    
        df_coois['key2']=df_coois['material'].astype(str)+df_coois['division'].astype(str)+df_coois['profit_centre'].astype(str)+df_coois['created_by'].astype(str)
        
        #Convert df_zpp to dict
        df_zpp_dict_message=dict(zip(df_zpp.key, df_zpp.message))
        df_zpp_dict_date_reordo=dict(zip(df_zpp.key, df_zpp.date_reordo))

        #Merge ZPP and COOIS with keys
        df_coois['message']=df_coois['key'].map(df_zpp_dict_message)
        df_coois['date_reordo']=df_coois['key'].map(df_zpp_dict_date_reordo)

        #convert df_material to dict
        df_material_dict_AllocatedTime= dict((zip(df_material.key,df_material.AllocatedTime)))
        df_material_dict_Leadtime= dict((zip(df_material.key,df_material.Leadtime)))
        df_material_dict_workstation= dict((zip(df_material.key,df_material.workstation)))
        df_material_dict_Allocated_Time_On_Workstation= dict((zip(df_material.key,df_material.Allocated_Time_On_Workstation)))
        df_material_dict_Smooth_Family= dict((zip(df_material.key,df_material.Smooth_Family)))

        #Merge coois and material with keys
        df_coois['AllocatedTime']=df_coois['key2'].map(df_material_dict_AllocatedTime)
        df_coois['Leadtime']=df_coois['key2'].map(df_material_dict_Leadtime)
        df_coois['workstation']=df_coois['key2'].map(df_material_dict_workstation)
        df_coois['Allocated_Time_On_Workstation']=df_coois['key2'].map(df_material_dict_Allocated_Time_On_Workstation)
        df_coois['Smooth_Family']=df_coois['key2'].map(df_material_dict_Smooth_Family)

        # add conditions :
        # 1: for Ranking : equal date reordo if exist else equal date end plan
        df_coois['Ranking']=np.where((df_coois['date_reordo'].isna()),(pd.to_datetime(df_coois['date_end_plan'])),(pd.to_datetime(df_coois['date_reordo'])))
        # 2: for closed  : equal true where order_stat containes TCLO ou LIVR
        df_coois['closed']=np.where(df_coois['order_stat'].str.contains('TCLO|LIVR'),True,False)
        filter_product_info= Product.undeleted_objects.values('Profit_center','planning','division__name').filter(id = product).first()
        # filter df_coois by division and product
        df_coois_by_division_product = df_coois[ (df_coois['profit_centre'] == filter_product_info['Profit_center']) & (df_coois['division'] == int(filter_product_info['division__name'])) & (df_coois['designation'] == filter_product_info['planning'])]
        records=df_coois_by_division_product.sort_values(['Smooth_Family','Ranking'])
    else :
        messages.error(request,"Import files and Input Materials Please !") 
        return render(request,'app/Shopfloor/Shopfloor.html',{'planningapproval_info':planningapproval_info,'planningapproval':planningapproval,'division':division,'product':product}) 
        
    return render(request,'app/Shopfloor/Shopfloor.html',{'planningapproval_info':planningapproval_info,'planningapproval':planningapproval,'records': records,'division':division,'product':product,'username':username(request)}) 

#create needs
# get inputs value, calculate smoothing end date and save 
def create_needs(request,division,product,planningapproval):

    if request.method=='POST':
        id = request.POST.getlist('index')
        # get inputs values
        division = request.POST.getlist('division')
        profit_centre = request.POST.getlist('profit_centre')
        order = request.POST.getlist('order')
        material = request.POST.getlist('material')
        designation = request.POST.getlist('designation')
        order_type = request.POST.getlist('order_type')
        order_quantity = request.POST.getlist('order_quantity')
        date_start_plan= request.POST.getlist('date_start_plan')
        date_end_plan = request.POST.getlist('date_end_plan')
        fixation = request.POST.getlist('fixation')
        date_reordo = request.POST.getlist('date_reordo')
        message = request.POST.getlist('message')
        order_stat = request.POST.getlist('order_stat')
        customer_order = request.POST.getlist('customer_order')
        date_end_real = request.POST.getlist('date_end_real')
        AllocatedTime = request.POST.getlist('AllocatedTime')
        Leadtime = request.POST.getlist('Leadtime')
        workstation = request.POST.getlist('workstation')
        Allocated_Time_On_Workstation = request.POST.getlist('Allocated_Time_On_Workstation')
        Smooth_Family = request.POST.getlist('Smooth_Family')
        Ranking = request.POST.getlist('Ranking')
        Freeze_end_date = request.POST.getlist('freeze_end_date')
        Remain_to_do = request.POST.getlist('Remain to do')
        closed = request.POST.getlist('closed')
        calendar_type=request.POST.get('calendar')

        #Convert Input Data to DateFrame
        data={
            'division':division,
            'profit_centre':profit_centre,
            'order':order,
            'material':material,
            'designation':designation,
            'order_type':order_type,
            'order_quantity':order_quantity,
            'date_start_plan':date_start_plan,
            'date_end_plan': date_end_plan,
            'fixation':fixation,
            'date_reordo':date_reordo,
            'message':message,
            'order_stat':order_stat,
            'customer_order':customer_order,
            'date_end_real':date_end_real, 
            'AllocatedTime':AllocatedTime, 
            'Leadtime':Leadtime, 
            'workstation':workstation,
            'Allocated_Time_On_Workstation':Allocated_Time_On_Workstation, 
            'Smooth_Family':Smooth_Family,
            'Ranking':Ranking, 
            'Freeze_end_date':Freeze_end_date, 
            'Remain_to_do':Remain_to_do, 
            'closed':closed,
            }

        # convert data to dataframe 
        df=pd.DataFrame.from_dict(data)
        # convert freeze_end_date to datetime 
        df['Freeze_end_date'] = pd.to_datetime(df['Freeze_end_date'])
        df_for_check = df[df['closed'].str.contains('False')].groupby(["Smooth_Family"], as_index=False)["Freeze_end_date"].first()        
        # test line by line to return the index of smooth family is not filled
        for i in range(len(df_for_check)):
            if (pd.isnull(df_for_check.loc[i,'Freeze_end_date'])):
                messages.error(request,'Please fill at least the first Freeze end date, for the Smooth Family: '+df_for_check.loc[i,'Smooth_Family'])
                return redirect("../needs")
        
        #call function smoothing_calculate to calcul smoothing end date 
        df=smoothing_calculate(df,calendar_type,product)

        # delete key,freezed, key_start_day column
        del df['key']
        del df['freezed']
        del df['key_start_day']
        # delete index from df
        df=df.reset_index(drop=True)
        # save shofloor with version 
        # get version_data 
        version_number = Shopfloor.objects.values('version').filter(product=product,planning_approval_id=planningapproval).order_by('-version').first()
        version = version_number['version']+1 if version_number else 1
        save_needs(df,product,planningapproval,version)
        print('end save needs')
        # to save cycle with the same version of shopfloor
        save_cycle_with_version(product,planningapproval,version)
        print('end save save_cycle_with_version')

        messages.success(request,"Data saved successfully!") 
        return redirect(f'../result/')

# @allowed_users(allowed_roles=["Planificateur"]) 
#  calculate smoothing end date to use in create needs      
def smoothing_calculate(df_data,calendar_type,product):
    # make holidays and cycle_data as global varibale to reduce access to 
    
    global holidays, cycle_data
    if calendar_type == 'official':
        # we use holidays in is_in_open_hours function
        holidays = HolidaysCalendar.undeleted_objects.values_list('holidaysDate',flat=True).filter(product=product,owner = 'officiel') 
        # we use cycle_data in smoothing_calculate function
        cycle_data=Cycle.undeleted_objects.values('product__division__name','profit_center','smooth_family','cycle_time','work_day').filter(product=product,owner = 'officiel') 
        # print('cycle_data', cycle_data)
    else:
        holidays = HolidaysCalendar.undeleted_objects.values_list('holidaysDate',flat=True).filter(product=product,owner = 'marwa') 
        cycle_data=Cycle.undeleted_objects.values('product__division__name','profit_center','smooth_family','cycle_time','work_day').filter(product=product,owner = 'marwa') 
    #Get Work date data
    # cycle_data=Cycle.undeleted_objects.values('profit_center','smooth_family','cycle_time','work_day') 
    #Convert to DataFrame cycle_data( globale variable)
    df_cycle_data=pd.DataFrame(list(cycle_data))
    # concatinate profit_center and smooth_family and work_day
    df_cycle_data['key']= df_cycle_data['product__division__name'].astype(str)+df_cycle_data['profit_center'].astype(str)+df_cycle_data['smooth_family'].astype(str)+df_cycle_data['work_day'].astype(str)
   # df_product_work_data_dict_date=dict(zip(df_product_work_data.key, df_product_work_data.workdate))
    df_dict_cycle=dict(zip(df_cycle_data.key, df_cycle_data.cycle_time))
    # sort values with Ranking
    df_data=df_data.sort_values('Ranking') 
    #Add col freezed to know how row is freezed
    df_data['freezed']=np.where((df_data['Freeze_end_date'].notna()),'Freezed','not_freezed')
    df_data['key']=df_data['division'].astype(str)+df_data['profit_centre'].astype(str)+df_data['Smooth_Family'].astype(str)+pd.to_datetime(df_data['Freeze_end_date']).astype(str)
    df_data[['Freeze_end_date']] = df_data[['Freeze_end_date']].astype(object).where(df_data[['Freeze_end_date']].notnull(), None)
    df_data['smoothing_end_date']=df_data['Freeze_end_date']
    df_data.insert(0,'key_start_day','')
    df_data['closed']=df_data['closed'].astype(str)
    # create dataframe where closed False 
    df_closed_false= df_data[df_data['closed']=='False']

    # to sort value with smooth family and ranking 
    df_closed_false = df_closed_false.sort_values(['Smooth_Family','Ranking']).reset_index()
    # to delete index
    del df_closed_false['index']
    # create dataframe where closed True
    df_closed_true = df_data[df_data['closed'] =='True']
    # reset index from df_closed_true
    df_closed_true=df_closed_true.reset_index()
    del df_closed_true['index']
    # to applicate calcul on df_closed_false
    for i in range(len(df_closed_false)-1):
        # test if df_closed_false not freezed calculate smoothing end date 
        if (df_closed_false.loc[i+1,'freezed']=='not_freezed'):
            df_closed_false.loc[i+1,'smoothing_end_date'] = smooth_date_calcul(df_closed_false.loc[i,'smoothing_end_date'],df_dict_cycle.items(),df_closed_false.loc[i,'division'],df_closed_false.loc[i,'profit_centre'],df_closed_false.loc[i,'Smooth_Family'])
    df_data = pd.concat([df_closed_true, df_closed_false])
    return df_data
 
#calcul smooth end date(Recursive Function) to use in smoothing_calculate
def smooth_date_calcul(current_date,table,division,profit_center,Smooth_Family,prev_cycle=None,prev_date=None):
    
    #Get cycle for current day
    key_date=str(division)+str(profit_center)+str(Smooth_Family)+str(current_date).split(' ')[0]
    #initial case treatment (when prev_date =  current_date)
    if prev_date is None:
        prev_date=current_date
    # Check and get cycle
    try:
        # key : contains the concatenation between division and profit_center and smooth family and date of the table 
        # value :cycle time
        for key,value in table:
            if key_date == key:
                cycle=value
        print(cycle)     
    #when cycle not found  in table return date(1900,1,1)    
    except Exception:
        
        return datetime(1900, 1, 1, 6) 
            
    #stop condition to avoid the infinite loop
    if cycle==prev_cycle:
        return current_date
    
    # get start time for current date
    # flat=True this will mean the returned results are single values, rather than one-tuples
    start_time = WorkData.undeleted_objects.filter(date=current_date).values_list('startTime',flat=True).first()
    # get end time for current date
    end_time = WorkData.undeleted_objects.filter(date=current_date).values_list('endTime',flat=True).first()
      
    # dictionary of business_hours
    business_hours = {
    "from": start_time, # startTime
    "to": end_time,  # endTime
    }

    # function is_in_open_hours
    def is_in_open_hours(dt):
            return  dt.date() not in holidays \
            and business_hours["from"].hour <= dt.time().hour < business_hours["to"].hour

    # function get_next_open_datetime 
    def get_next_open_datetime(dt):
        while True:
            dt = dt + timedelta(days=1)
            # check if open date
            if dt.date() not in holidays:
                # combine date and hour
                # dt = datetime.combine(dt.date(), business_hours["from"])
                dt = datetime.combine(dt.date(), business_hours["from"])+timedelta(minutes=dt.time().minute)
                return dt
    
    # function add hours
    def add_hours(dt, hours):
        while hours > 0:
            if is_in_open_hours(dt) :
                dt = dt + timedelta(hours=1)
                hours = hours - 1
            else:
                dt = get_next_open_datetime(dt)

        if hours < 1:
            dt= dt+timedelta(hours=hours)
        # check if dt is the last hour of work
        if  dt.time().hour == business_hours["to"].hour or dt.time().hour > business_hours["to"].hour:
            dt = get_next_open_datetime(dt)
        return dt

    new_date=add_hours(prev_date, cycle)
    return   smooth_date_calcul(new_date,table,division,profit_center,Smooth_Family,cycle,current_date)


# save shoploor to use in create_needs
def save_needs(df,product,planningapproval,version):
   
    conn = psycopg2.connect(host='localhost',dbname='mps_db',user='postgres',password='054Ibiza',port='5432')
    # # get version_data 
    # version_number = Shopfloor.objects.values('version').filter(product=product,planning_approval_id=planningapproval).order_by('-version').first()
    # version = version_number['version']+1 if version_number else 1
    
    # to save cycle with the same version of shopfloor
    # save_cycle_with_version(product,planningapproval)

    #insert base informations into file
    df.insert(0,'created_at',datetime.now())
    df.insert(1,'updated_at',datetime.now())
    df.insert(2,'created_by','Marwa')
    df.insert(3,'updated_by','Marwa')
    df.insert(4,'is_deleted',False)
    df.insert(5,'deleted_by','')
    df.insert(6,'deleted_at',datetime.now())
    df.insert(7,'restored_at',datetime.now())
    df.insert(8,'restored_by','')
    df['version']=version
    df['shared']=False
    df['product_id']=product
    df['planning_approval_id']=planningapproval

    # as file object
    shopfloor = StringIO()

    #convert file to csv
    shopfloor.write(df.to_csv(index=False , header=None,sep=';'))
    # This will make the cursor at index 0
    shopfloor.seek(0)
    with conn.cursor() as c:
        c.copy_from(
            file=shopfloor,
            #file name in DB
            table="app_shopfloor",
            columns=[
                    'created_at',
                    'updated_at',
                    'created_by',
                    'updated_by',
                    'is_deleted',
                    'deleted_by',
                    'deleted_at',
                    'restored_at',
                    'restored_by',
                    'division',
                    'profit_centre',
                    'order',
                    'material',
                    'designation',
                    'order_type',
                    'order_quantity',
                    'date_start_plan',
                    'date_end_plan',
                    'fixation',
                    'date_reordo',
                    'message',
                    'order_stat',
                    'customer_order',
                    'date_end_real',
                    'AllocatedTime',
                    'Leadtime',
                    'workstation',
                    'Allocated_Time_On_Workstation',
                    'Smooth_Family',
                    'Ranking',
                    'Freeze_end_date',
                    'Remain_to_do',
                    'closed',
                    'smoothing_end_date',
                    'version',
                    'shared',
                    'product_id',
                    'planning_approval_id',  
                    ],

            null="",
            sep=";",
        )
    conn.commit()



# save cycle with version ==> call function in save needs 
def save_cycle_with_version(product,planningapproval,version):
    conn = psycopg2.connect(host='localhost',dbname='mps_db',user='postgres',password='054Ibiza',port='5432')
    #Get last cycle data shared
    if version == 1:
        cycles= Cycle.objects.all().filter(product=product,owner='officiel',shared=True)
    else:
        cycles= Cycle.objects.all().filter(product=product,owner='officiel',planning_approval_id=planningapproval)

    df_cycles=pd.DataFrame(cycles.values())
    df_cycles['planning_approval_id']=planningapproval
    df_cycles['shared']=False
    df_cycles['version']=version
    print(df_cycles)
    del df_cycles['id']
    cycle_data = StringIO()
    #convert file to csv
    cycle_data.write(df_cycles.to_csv(index=False ,header=None,sep=';'))
    # This will make the cursor at index 0
    cycle_data.seek(0)
    with conn.cursor() as c:
        c.copy_from(
            file=cycle_data,
            #file name in DB
            table="app_cycle",
            columns=[
                    'created_at',
                    'updated_at',
                    'created_by',
                    'updated_by',
                    'is_deleted',
                    'deleted_by',
                    'deleted_at',
                    'restored_at',
                    'restored_by',
                    'division',
                    'profit_center',
                    'work_day',
                    'smooth_family',
                    'cycle_time',
                    'workdata_id',
                    'owner',
                    'product_id',
                    'version',
                    'planning_approval_id',
                    'shared',
                    ],

            null="",
            sep=";",
        )
    conn.commit()



# def result display result of shoploor data with version  
def result(request,division,product,planningapproval):
    data= versions= selected_version = None
    # name of planning approval for info page
    planningapproval_info=PlanningApproval.objects.all().filter(id=planningapproval).first()

    try:
        data=Shopfloor.objects.all().order_by('smoothing_end_date','closed','Smooth_Family','Ranking').filter(planning_approval_id=planningapproval)
        df_data=pd.DataFrame(data.values())
        df_data['Freeze_end_date'] = df_data['Freeze_end_date'].astype(object).where(df_data['Freeze_end_date'].notnull(), None)
        df_data['smoothing_end_date'] = df_data['smoothing_end_date'].astype(object).where(df_data['smoothing_end_date'].notnull(), None)
        #Get all verison to show them in input list
        versions=sorted(df_data['version'].unique(),reverse=True)
        #return data with last version
        grater_version=max(versions)
        records=df_data[df_data['version']==grater_version]
        version_number=grater_version

    except Exception:
        messages.error(request,"Empty data here, Please fill in needs") 
        return redirect("../needs")  

    if request.method=='POST':
        selected_version= request.POST.get('selected_version')
        # convert selected_version (str to int) 
        selected_version=int(selected_version)
        records=df_data[df_data['version']==selected_version]
        version_number=selected_version

    if selected_version is None:
        selected_version= grater_version

    return render(request,'app/Shopfloor/result.html',{'planningapproval_info':planningapproval_info,
    'planningapproval':planningapproval,'records':records,'division':division,'product':product,
    'versions':versions,'version_number':version_number,'grater_version':grater_version})


# filter planning result
def kpis(request,division,product,planningapproval,come_from,version_number):

    data=Shopfloor.objects.filter(product=product,planning_approval_id=planningapproval).values('order','date_start_plan','smoothing_end_date').order_by('Smooth_Family','Ranking')
    

    # initialization
    from_date = to_date = date_from = date_to =date_from_year_week = date_to_year_week= date_from_year_month= date_to_year_month = None
    demand_prod_planning.week_count=None
    demand_prod_planning.week_count_axis_x=None
    demand_prod_planning.month_count=None
    demand_prod_planning.month_count_axis_x=None
    cycle_time_kpi.cycle_mean=None
    cycle_time_kpi.week_cycle_mean_axis_x=None
    cycle_time_kpi.smooth_family=None
    cycle_time_kpi.smooth_family_month=None
    cycle_time_kpi.cycle_mean_month=None
    cycle_time_kpi.month_cycle_mean_axis_x=None
    production_plan_kpi.date_production_week=None
    production_plan_kpi.date_production_month=None
    demand_prod_planning.work_days_count =None
    demand_prod_planning.work_days_count_month=None
    logistic_stock_kpi.logistic_stock_week = None
    logistic_stock_kpi.logistic_stock_month =None

    # get cuurent year for filter cycle data dates (for adjust cycle)
    current_year=datetime.now().year
    
    # name of planning approval for info page
    planningapproval_info = PlanningApproval.objects.all().filter(id=planningapproval).first()
    # get data from database
    cycles_data=Cycle.undeleted_objects.all().filter(division=division,product=product,owner='officiel',planning_approval_id=planningapproval,  work_day__year= current_year)
    # cycles_data=Cycle.undeleted_objects.all().filter(division=division,product=product,owner='officiel',planning_approval_id=planningapproval)
    shopfloor_data=Shopfloor.objects.all().filter(product=product,planning_approval_id=planningapproval)
    # get workday to use in calcul of demonstrated capacity
    work_days=WorkData.undeleted_objects.values('date').filter(product__division=division,product=product,owner='officiel')
    
    # to convert data objects  to dataframe
    df_cycles_data=pd.DataFrame(cycles_data.values())
    df_shopfloor_data=pd.DataFrame(shopfloor_data.values())
    df_work_days=pd.DataFrame(work_days.values())
    print(df_cycles_data)

    if df_cycles_data.size:
            grater_version= df_cycles_data['version'].max()
            available_versions= df_cycles_data['version'].unique()

    if come_from == 'planning_list':
        '''Check planning state:  '''
        check_coois = Coois.objects.filter(planning_approval=planningapproval).all()
        check_zpp = Zpp.objects.filter(planning_approval=planningapproval).all()
        check_shopfloor = Shopfloor.objects.filter(planning_approval=planningapproval).all()
        
        if not check_coois:
            return redirect(upload_coois,division=division,product=product,planningapproval=planningapproval)
        if not check_zpp:
            return redirect(upload_zpp,division=division,product=product,planningapproval=planningapproval)
        if not check_shopfloor:
            return redirect(needs,division=division,product=product,planningapproval=planningapproval)
        '''End Check planning state:  '''
        df_cycles_data=df_cycles_data[df_cycles_data['version'] == int(version_number)]
        df_cycles_data['work_day_week']= pd.to_datetime(df_cycles_data['work_day'],errors='coerce').dt.isocalendar().week
        df_cycles_data['work_day_year']= pd.to_datetime(df_cycles_data['work_day'],errors='coerce').dt.isocalendar().year
        df_cycles_data['work_day_week_year']= df_cycles_data['work_day_year'].astype(str)+'-'+'W'+df_cycles_data['work_day_week'].astype(str)

        df_cycles_data["cycle_time"] = pd.to_numeric(df_cycles_data["cycle_time"], downcast="float")
        #Mean of cycle time to show them in front table adjust cycle
        cycle_mean= df_cycles_data.groupby(['work_day_year','work_day_week_year','smooth_family']).agg(cycle_mean_week_count=('cycle_time','mean')).unstack().fillna(0).stack().reset_index()         
        cycle_mean=cycle_mean[cycle_mean['work_day_year']== current_year]
        # Convert the work_day_week_year column to date objects and use them as the sort key
        cycle_mean = cycle_mean.sort_values(by='work_day_week_year', key=lambda x: pd.to_datetime(x + '-1', format='%Y-W%W-%w'))

        df_shopfloor_data=df_shopfloor_data[df_shopfloor_data['version'] == int(version_number)]
        
    if come_from == 'shopfloor':
        df_cycles_data=df_cycles_data[df_cycles_data['version'] == int(grater_version)]

        df_cycles_data['work_day_week']= pd.to_datetime(df_cycles_data['work_day'],errors='coerce').dt.isocalendar().week
        df_cycles_data['work_day_year']= pd.to_datetime(df_cycles_data['work_day'],errors='coerce').dt.isocalendar().year
        df_cycles_data['work_day_week_year']= df_cycles_data['work_day_year'].astype(str)+'-'+'W'+df_cycles_data['work_day_week'].astype(str)
        grater_version= df_cycles_data['version'].max()
        available_versions= df_cycles_data['version'].unique()
        df_cycles_data["cycle_time"] = pd.to_numeric(df_cycles_data["cycle_time"], downcast="float")
        #Mean of cycle time to show them in front table adjust cycle
        cycle_mean= df_cycles_data.groupby(['work_day_year','work_day_week_year','smooth_family']).agg(cycle_mean_week_count=('cycle_time','mean')).unstack().fillna(0).stack().reset_index()         
        cycle_mean=cycle_mean[cycle_mean['work_day_year']== current_year]
        # Convert the work_day_week_year column to date objects and use them as the sort key
        cycle_mean = cycle_mean.sort_values(by='work_day_week_year', key=lambda x: pd.to_datetime(x + '-1', format='%Y-W%W-%w'))

        df_shopfloor_data=df_shopfloor_data[df_shopfloor_data['version'] == int(grater_version)]
        version_number = grater_version

    if come_from == 'form_after_update_cycle' and request.method == "POST":
        version_number = request.POST.get('version_number')
        smooth_family_list= request.POST.getlist('smooth_family')
        cycle_time_list= request.POST.getlist('cycle_time')
        week_cycle_list= request.POST.getlist('week_cycle')
        cycle_type = request.POST.get('cycle-type')

        # cycle_type=[]
        # for date in week_cycle_list:
        #     cycle_type.append(request.POST.get('cycle-type-'+ date))
        data = {
        "smooth_family": smooth_family_list,
        "cycle_time": cycle_time_list,
        "week_cycle": week_cycle_list,
        "cycle_type":cycle_type
        }


        df_cycle_input = pd.DataFrame(data)
        df_cycle_input['year']= df_cycle_input['week_cycle'].str.split('-W').str[0]
        df_cycle_input['week']= df_cycle_input['week_cycle'].str.split('-W').str[1]
        df_cycle_input['key']= df_cycle_input['week_cycle'].astype(str)+df_cycle_input['smooth_family'].astype(str)
        df_cycle_input_dict_cycle_time=dict(zip(df_cycle_input['key'],df_cycle_input['cycle_time']))
        df_cycle_input_dict_cycle_type=dict(zip(df_cycle_input['key'],df_cycle_input['cycle_type']))
        #  get cycle data with version selected 
        df_cycles_data=df_cycles_data[df_cycles_data['version'] == int(version_number)]
        #  make new column key (work_day_week_year and smooth_family)
        df_cycles_data['work_day_week']= pd.to_datetime(df_cycles_data['work_day'],errors='coerce').dt.isocalendar().week
        df_cycles_data['work_day_year']= pd.to_datetime(df_cycles_data['work_day'],errors='coerce').dt.isocalendar().year
        df_cycles_data['work_day_week_year']= df_cycles_data['work_day_year'].astype(str)+'-'+'W'+df_cycles_data['work_day_week'].astype(str)
        df_cycles_data['key']=df_cycles_data['work_day_week_year'].astype(str)+df_cycles_data['smooth_family'].astype(str)
        #  map cycle time
        df_cycles_data['cycle_time']=df_cycles_data['key'].map(df_cycle_input_dict_cycle_time)
        #  map cycle type 
        df_cycles_data['cycle_type']=df_cycles_data['key'].map(df_cycle_input_dict_cycle_type)


        work_data=WorkData.undeleted_objects.all().filter(product=product)
        df_work_data=pd.DataFrame(work_data.values())
        df_work_data_dict_start_time=dict(zip(df_work_data['date'],df_work_data['startTime'])) 
        df_work_data_dict_end_time=dict(zip(df_work_data['date'],df_work_data['endTime'])) 
        df_cycles_data['start_time']= df_cycles_data['work_day'].map(df_work_data_dict_start_time)
        df_cycles_data['end_time']= df_cycles_data['work_day'].map(df_work_data_dict_end_time)
        df_cycles_data['work_hours']=(pd.to_datetime(df_cycles_data['end_time'],format='%H:%M:%S') - pd.to_datetime(df_cycles_data['start_time'],format='%H:%M:%S'))/ pd.Timedelta(hours=1)
        df_cycles_data['cycle_time']=np.where(df_cycles_data['cycle_type'] == 'Days',df_cycles_data['cycle_time'].astype(float) * df_cycles_data['work_hours'].astype(float),df_cycles_data['cycle_time'])
        
        #Prepar DF to upload into DB
        df_cycles_data['version']=grater_version+1
        df_cycles_data['shared']=False
        df_cycles_data['created_at']=datetime.now()
        df_cycles_data['updated_at']=datetime.now()
        df_cycles_data['created_by']='Marwa'
        df_cycles_data['updated_by']='Marwa'
        df_cycles_data['is_deleted']=False
        df_cycles_data['deleted_by']=None
        df_cycles_data['deleted_at']=None
        df_cycles_data['restored_at']=None
        df_cycles_data['restored_by']=None
        df_cycles_data=df_cycles_data[['created_at',
                                        'updated_at',
                                        'created_by',
                                        'updated_by',
                                        'is_deleted',
                                        'deleted_by',
                                        'deleted_at',
                                        'restored_at',
                                        'restored_by',
                                        'division',
                                        'profit_center',
                                        'work_day',
                                        'smooth_family',
                                        'cycle_time',
                                        'workdata_id',
                                        'owner',
                                        'product_id',
                                        'version',
                                        'planning_approval_id',
                                        'shared',]]
        
        update_cycle(df_cycles_data)

        shopfloor_data=Shopfloor.objects.filter(
                                                version=version_number,
                                                product_id=product,
                                                planning_approval_id=planningapproval
                                                ).values(
                                                        'division',
                                                        'profit_centre',
                                                        'order',
                                                        'material',
                                                        'designation',
                                                        'order_type',
                                                        'order_quantity',
                                                        'date_start_plan',
                                                        'date_end_plan' ,
                                                        'fixation',
                                                        'date_reordo',
                                                        'message',
                                                        'order_stat',
                                                        'customer_order',
                                                        'date_end_real', 
                                                        'AllocatedTime', 
                                                        'Leadtime', 
                                                        'workstation',
                                                        'Allocated_Time_On_Workstation', 
                                                        'Smooth_Family',
                                                        'Ranking', 
                                                        'Freeze_end_date', 
                                                        'Remain_to_do', 
                                                        'closed')
        df_shopfloor_data=pd.DataFrame(shopfloor_data)
        # get calendar type
        calendar_type= 'official'
        # => smoothing_calculate (df, calendar type)
        df=smoothing_calculate(df_shopfloor_data,calendar_type,product)
        # delete key,freezed, key_start_day column
        del df['key']
        del df['freezed']
        del df['key_start_day']
        # delete index from df
        df=df.reset_index(drop=True)
        # =>  save_needs (df, product, planningapproval)
        save_needs(df,product,planningapproval,grater_version+1)
        df_shopfloor_data = df

        #Get new cycle data after update
        df_cycles_data['work_day_week']= pd.to_datetime(df_cycles_data['work_day'],errors='coerce').dt.isocalendar().week
        df_cycles_data['work_day_year']= pd.to_datetime(df_cycles_data['work_day'],errors='coerce').dt.isocalendar().year
        df_cycles_data['work_day_week_year']= df_cycles_data['work_day_year'].astype(str)+'-'+'W'+df_cycles_data['work_day_week'].astype(str)
        df_cycles_data["cycle_time"] = pd.to_numeric(df_cycles_data["cycle_time"], downcast="float")

        #Mean of cycle time to show them in front table adjust cycle
        cycle_mean= df_cycles_data.groupby(['work_day_year','work_day_week_year','smooth_family']).agg(cycle_mean_week_count=('cycle_time','mean')).unstack().fillna(0).stack().reset_index()         
        cycle_mean=cycle_mean[cycle_mean['work_day_year']== current_year]
        # Convert the work_day_week_year column to date objects and use them as the sort key
        cycle_mean = cycle_mean.sort_values(by='work_day_week_year', key=lambda x: pd.to_datetime(x + '-1', format='%Y-W%W-%w'))


        version_number = grater_version+1

    if come_from == 'form_filter_date_version' and request.method == "POST":
            version_selected = request.POST.get('version_selected')
            from_date= request.POST.get('from')
            to_date= request.POST.get('to') 
            version_number=version_selected

            df_shopfloor_data=df_shopfloor_data[df_shopfloor_data['version'] == int(version_number)]
            df_cycles_data=df_cycles_data[df_cycles_data['version'] == int(version_number)]

            df_cycles_data['work_day_week']= pd.to_datetime(df_cycles_data['work_day'],errors='coerce').dt.isocalendar().week
            df_cycles_data['work_day_year']= pd.to_datetime(df_cycles_data['work_day'],errors='coerce').dt.isocalendar().year
            df_cycles_data['work_day_week_year']= df_cycles_data['work_day_year'].astype(str)+'-'+'W'+df_cycles_data['work_day_week'].astype(str)

            df_cycles_data["cycle_time"] = pd.to_numeric(df_cycles_data["cycle_time"], downcast="float")
            #Mean of cycle time to show them in front table adjust cycle
            cycle_mean= df_cycles_data.groupby(['work_day_year','work_day_week_year','smooth_family']).agg(cycle_mean_week_count=('cycle_time','mean')).unstack().fillna(0).stack().reset_index()         
            cycle_mean=cycle_mean[cycle_mean['work_day_year']== current_year]
            # Convert the work_day_week_year column to date objects and use them as the sort key
            cycle_mean = cycle_mean.sort_values(by='work_day_week_year', key=lambda x: pd.to_datetime(x + '-1', format='%Y-W%W-%w'))

    if come_from=='form_shared':
        df_cycles_data=df_cycles_data[df_cycles_data['version'] == int(version_number)]

        df_cycles_data['work_day_week']= pd.to_datetime(df_cycles_data['work_day'],errors='coerce').dt.isocalendar().week
        df_cycles_data['work_day_year']= pd.to_datetime(df_cycles_data['work_day'],errors='coerce').dt.isocalendar().year
        df_cycles_data['work_day_week_year']= df_cycles_data['work_day_year'].astype(str)+'-'+'W'+df_cycles_data['work_day_week'].astype(str)
        grater_version= df_cycles_data['version'].max()
        available_versions= df_cycles_data['version'].unique()
        df_cycles_data["cycle_time"] = pd.to_numeric(df_cycles_data["cycle_time"], downcast="float")
        #Mean of cycle time to show them in front table adjust cycle
        cycle_mean= df_cycles_data.groupby(['work_day_year','work_day_week_year','smooth_family']).agg(cycle_mean_week_count=('cycle_time','mean')).unstack().fillna(0).stack().reset_index()         
        cycle_mean=cycle_mean[cycle_mean['work_day_year']== current_year]
        # Convert the work_day_week_year column to date objects and use them as the sort key
        cycle_mean = cycle_mean.sort_values(by='work_day_week_year', key=lambda x: pd.to_datetime(x + '-1', format='%Y-W%W-%w'))

        data_Shopfloor=Shopfloor.objects.all().filter(version=version_number,product= product,planning_approval=planningapproval)    
        data_Shopfloor.update(shared=True)

        data_Shopfloor_df = pd.DataFrame(data_Shopfloor.values())
        data_Shopfloor_df['order_nature']=np.where((data_Shopfloor_df['order_type'].str.startswith('YP')),'OF','OP')
        

        df_OP = data_Shopfloor_df[(data_Shopfloor_df['order_nature']== 'OP') & (data_Shopfloor_df['closed']==False)]
        #Select columns to download
        df_OP_result = df_OP[['order','smoothing_end_date']]
        df_OP_result['smoothing_end_date']= pd.to_datetime( df_OP_result['smoothing_end_date'], format='%Y/%m/%d')
        df_OP_result['smoothing_end_date'] = df_OP_result['smoothing_end_date'].dt.strftime('%d.%m.%Y')
        df_OP_result = df_OP_result.rename(mapper={'order': 'Planned order number', 'smoothing_end_date': 'End date (String : DD.MM.YYYY)'},axis='columns') 
        df_OP_result.insert(0,"Journal d'execution Winshuttle TRANSACTION ",'')
        
        
        df_OF = data_Shopfloor_df[(data_Shopfloor_df['order_nature']== 'OF') & (data_Shopfloor_df['closed']==False)]
        #Select columns to download
        df_OF_result = df_OF[['order', 'date_start_plan','smoothing_end_date']]
        df_OF_result['date_start_plan']= pd.to_datetime( df_OF_result['date_start_plan'], format='%Y/%m/%d')
        df_OF_result['date_start_plan'] = df_OF_result['date_start_plan'].dt.strftime('%d.%m.%Y')
        df_OF_result['smoothing_end_date']= pd.to_datetime( df_OF_result['smoothing_end_date'], format='%Y/%m/%d')
        df_OF_result['smoothing_end_date'] = df_OF_result['smoothing_end_date'].dt.strftime('%d.%m.%Y')
        # Third position would be at index 2, because of zero-indexing.
        # df_OF_result.insert(1, 'LOG (Do not write values in this column)',)

        df_OF_result = df_OF_result.rename(mapper={'order': 'Work order number', 'date_start_plan': 'Start date (String : DD.MM.YYYY)', 'smoothing_end_date': 'End date (String : DD.MM.YYYY)'},axis='columns') 
        df_OF_result.insert(0,"LOG",'')


        # store dataframes as Excel files in BytesIO
        file1 = BytesIO()
        df_OF_result.to_excel(file1, index=False)
        file1.seek(0)

        file2 = BytesIO()
        df_OP_result.to_excel(file2, index=False)
        file2.seek(0)

        # create a zipfile of the two Excel files
        zip_file = BytesIO()
        with zipfile.ZipFile(zip_file, mode='w') as z:
            z.writestr('Smooth work orders.xlsx', file1.read())
            z.writestr('Smooth Planned orders.xlsx', file2.read())
        zip_file.seek(0)

        # create Django response with ZIP file
        response = HttpResponse(zip_file.getvalue(), content_type='application/zip')
        response['Content-Disposition'] = 'attachment; filename=files.zip'

        # return response
        return response





    
    #********** convert dates ************
    if  from_date and  to_date != 'None': 
        date_from = datetime.strptime(from_date,'%Y-%m-%d')
        date_to = datetime.strptime(to_date,'%Y-%m-%d')  
        
        date_from_year_week= date_from.strftime('%Y' '-W' '%V')
        date_to_year_week = date_to.strftime('%Y' '-W' '%V')
        date_from_year_month= date_from.strftime('%Y' '-M' '%m')
        date_to_year_month = date_to.strftime('%Y' '-M' '%m') 

    #********** Call here functions ************
    cycle_time_kpi(df_cycles_data,date_from,date_to)   
    demand_prod_planning(df_shopfloor_data,df_work_days,date_from,date_to)
    production_plan_kpi(df_shopfloor_data,date_from,date_to)
    logistic_stock_kpi(date_from_year_week, date_to_year_week,date_from_year_month,date_to_year_month)

    

    return render(request,'app/kpi_test.html',{
    'username':username(request),
    'version_number':version_number,'available_versions':available_versions,'grater_version':grater_version,
    'cycles_data':df_cycles_data,
    'cycle_mean_adjust_cycle':cycle_mean,
    'records':df_shopfloor_data,
    'division':division,
    'product':product,
    'from_date':from_date,
    'to_date':to_date,
    'planningapproval':planningapproval,
    'planningapproval_info':planningapproval_info,
    'week_count':demand_prod_planning.week_count,
    'week_count_axis_x':demand_prod_planning.week_count_axis_x,
    'month_count':demand_prod_planning.month_count,
    'month_count_axis_x':demand_prod_planning.month_count_axis_x,
    'date_production_week':production_plan_kpi.date_production_week,
    'date_production_month':production_plan_kpi.date_production_month,
    'work_days_count_week': demand_prod_planning.work_days_count,
    'work_days_count_month':demand_prod_planning.work_days_count_month,
    'logistic_stock_week':logistic_stock_kpi.logistic_stock_week,
    'logistic_stock_month':logistic_stock_kpi.logistic_stock_month,
    'cycle_mean':cycle_time_kpi.cycle_mean,
    'week_cycle_mean_axis_x':cycle_time_kpi.week_cycle_mean_axis_x,
    'smooth_family': cycle_time_kpi.smooth_family,
    'cycle_mean_month':cycle_time_kpi.cycle_mean_month,
    'month_cycle_mean_axis_x':cycle_time_kpi.month_cycle_mean_axis_x,
    'smooth_family_month':cycle_time_kpi.smooth_family_month,
    })
    
# Adjust cycle time  
def update_cycle(data):

    conn = psycopg2.connect(host='localhost',dbname='mps_db',user='postgres',password='054Ibiza',port='5432')
    cycle_data = StringIO()
    #convert file to csv
    cycle_data.write(data.to_csv(index=False , header=None,sep=';'))
    # This will make the cursor at index 0
    cycle_data.seek(0)
    with conn.cursor() as c:
        c.copy_from(
            file=cycle_data,
            #file name in DB
            table="app_cycle",
            columns=[
                    'created_at',
                    'updated_at',
                    'created_by',
                    'updated_by',
                    'is_deleted',
                    'deleted_by',
                    'deleted_at',
                    'restored_at',
                    'restored_by',
                    'division',
                    'profit_center',
                    'work_day',
                    'smooth_family',
                    'cycle_time',
                    'workdata_id',
                    'owner',
                    'product_id',
                    'version',
                    'planning_approval_id',
                    'shared',
                    ],

            null="",
            sep=";",
        )
    conn.commit()


# calculate nomber of OF and OP ( wek and month)
def demand_prod_planning(df_data,df_work_days,date_from,date_to):
   
    df_data['date']=np.where((df_data['date_reordo'].isna()),(df_data['date_end_plan']),(df_data['date_reordo']))
    
    if date_from and date_to:
        # get df between two dates
        df_data_demand_prod_interval=df_data[(df_data['date'] >= date_from.date()) & (df_data['date'] <= date_to.date())]
    else:
        df_data_demand_prod_interval= df_data 
    
    # week of date
    df_data_demand_prod_interval['date_week']=pd.to_datetime(df_data_demand_prod_interval['date'], errors='coerce').dt.week
    # month of date
    df_data_demand_prod_interval['date_month']=pd.to_datetime(df_data_demand_prod_interval['date'], errors='coerce').dt.month
    # year of date
    df_data_demand_prod_interval['date_year']=pd.to_datetime(df_data_demand_prod_interval['date'], errors='coerce').dt.year
    # concatenate year and week
    df_data_demand_prod_interval['date_year_week']=df_data_demand_prod_interval['date_year'].astype(str)+'-'+'W'+df_data_demand_prod_interval['date_week'].astype(str)
    # concatenate year and month
    df_data_demand_prod_interval['date_year_month']=df_data_demand_prod_interval['date_year'].astype(str)+'-'+'M'+df_data_demand_prod_interval['date_month'].astype(str)
    # new column contains OF or OP
    df_data_demand_prod_interval['order_nature']=np.where((df_data_demand_prod_interval['order_type'].str.startswith('YP')),('OF'),('OP'))
    # new column contains closed and order nature to display closed 
    df_data_demand_prod_interval['order_nature_closed']=df_data_demand_prod_interval['order_nature'].astype('str')+df_data_demand_prod_interval['closed'].astype('str')
    # use unstack and stack to get duplicate data (for chart js)
    # *******************************
    #  to use in calcul of logistic stock
    demand_prod_week=df_data_demand_prod_interval.groupby(['date_year_week']).agg(demand_prod_count_week=('division','count')).reset_index()
    demand_prod_month=df_data_demand_prod_interval.groupby(['date_year_month']).agg(demand_prod_of_month_count=('division','count')).reset_index()
    
    # *******************************
    week_count=df_data_demand_prod_interval.groupby(['date_year_week','order_nature_closed']).agg(demand_prod_week_count=('division','count')).unstack().fillna(0).stack().reset_index()
    # get year from date_year_week 
    week_count['year']=week_count['date_year_week'].str.split('-W').str[0].astype(int)
    # get week from date_year_week 
    week_count['week']=week_count['date_year_week'].str.split('-W').str[1].astype(int)
    # sort values with year week (to get orderd values(year, week))
    week_count=week_count.sort_values(by=['year','week']).reset_index()
    # get unique date_year_week (because value date_year_week duplicate)
    week_count_axis_x=week_count['date_year_week'].unique()
    
    ### month
    month_count=df_data_demand_prod_interval.groupby(['date_year_month','order_nature_closed']).agg(demand_prod_month_count=('division','count')).unstack().fillna(0).stack().reset_index()
    month_count['year']=month_count['date_year_month'].str.split('-M').str[0].astype(int)
    month_count['week']=month_count['date_year_month'].str.split('-M').str[1].astype(int)
    month_count=month_count.sort_values(by=['year','week']).reset_index()
    month_count_axis_x=month_count['date_year_month'].unique()

    demand_prod_planning.week_count=week_count
    demand_prod_planning.week_count_axis_x=week_count_axis_x
    demand_prod_planning.month_count=month_count
    demand_prod_planning.month_count_axis_x=month_count_axis_x
    demand_prod_planning.demand_prod_week=demand_prod_week
    demand_prod_planning.demand_prod_month=demand_prod_month

    # ********************to calculate Demonstrated capacity (week and month)*************************

    # get current_date 
    # current_date = datetime.now()
    current_date = datetime.now()
    # previous month
    # first = current_date.replace(day=1)
    # last_month = first - timedelta(days=1)
    # get previous_month
    previous_month =current_date - relativedelta(months=1)
    df_prev_month = df_data[(df_data['date'] > previous_month.date()) & (df_data['date'] <= current_date.date())]
    df_data.to_csv('df_data.csv')
    # df_prev_month.to_csv('df_prev_month.csv')
    #  calcul sum of closed in previous_month
    df_prev_month_closed=df_prev_month[df_prev_month['closed']==True]
    previous_month_closed_count=df_prev_month_closed.shape[0]
   
    #calcul number of work_days in previous_month
    work_days_in_previous_month = df_work_days[(df_work_days['date'] >= previous_month.date()) & (df_work_days['date'] <= current_date.date())]
    work_days_in_previous_month_count = work_days_in_previous_month.shape[0]
   
    # calcul number of work_days in period(week)
    df_work_days['date_week']=pd.to_datetime(df_work_days['date'], errors='coerce').dt.week
    df_work_days['date_year']=pd.to_datetime(df_work_days['date'], errors='coerce').dt.year
    work_days_count=df_work_days.groupby(['date_week','date_year']).agg(work_days_count_week=('id','count')).reset_index()
    
    work_days_count['date_year_week']= work_days_count['date_year'].astype(str)+'-'+'W'+work_days_count['date_week'].astype(str)
    work_days_count = work_days_count[work_days_count['date_year_week'].isin(week_count_axis_x)]
    # calcul number of work_days in period(month)
    df_work_days['date_month']=pd.to_datetime(df_work_days['date'], errors='coerce').dt.month
    work_days_count_month=df_work_days.groupby(['date_month','date_year']).agg(work_days_count_month=('id','count')).reset_index()
    work_days_count_month['date_year_month']= work_days_count_month['date_year'].astype(str)+'-'+'M'+work_days_count_month['date_month'].astype(str)
    work_days_count_month = work_days_count_month[work_days_count_month['date_year_month'].isin(month_count_axis_x)]
    
    
    # test if work_days_in_previous_month_count == 0
    if work_days_in_previous_month_count == 0 :
        work_days_count['result_demonstrated_capacity'] = 0
        work_days_count_month['result_demonstrated_capacity'] = 0
    else:
        work_days_count['result_demonstrated_capacity'] = work_days_count['work_days_count_week'] * (previous_month_closed_count / work_days_in_previous_month_count)
        work_days_count_month['result_demonstrated_capacity'] = work_days_count_month['work_days_count_month'] * (previous_month_closed_count / work_days_in_previous_month_count)

   
    demand_prod_planning.work_days_count=work_days_count
    demand_prod_planning.work_days_count_month=work_days_count_month

# to display Kpi cycle time per smooth family (week and month)
def cycle_time_kpi(df_data,date_from,date_to):

    if date_from and date_to:
        df_cycle_time_interval = df_data[(df_data['work_day'] >= date_from.date()) & (df_data['work_day'] <= date_to.date())]
    else :
        df_cycle_time_interval= df_data

    # work_day_week
    df_cycle_time_interval['work_day_week']=pd.to_datetime(df_cycle_time_interval['work_day'],errors='coerce').dt.week
    # work_day_month
    df_cycle_time_interval['work_day_month']=pd.to_datetime(df_cycle_time_interval['work_day'],errors='coerce').dt.month
    # work_day_year
    df_cycle_time_interval['work_day_year']=pd.to_datetime(df_cycle_time_interval['work_day'], errors='coerce').dt.year
    # to concatenate year and week
    df_cycle_time_interval['work_year_week']=df_cycle_time_interval['work_day_year'].astype(str)+'-'+'W'+df_cycle_time_interval['work_day_week'].astype(str)
    #to concatenate year and month
    df_cycle_time_interval['work_year_month']=df_cycle_time_interval['work_day_year'].astype(str)+'-'+'M'+df_cycle_time_interval['work_day_month'].astype(str)
    # convert cycle_time to numeric
    df_cycle_time_interval["cycle_time"] = pd.to_numeric(df_cycle_time_interval["cycle_time"], downcast="float")
    # cycle_mean= df_cycle_time_interval.groupby(['work_year_week','smooth_family'])['cycle_time'].mean().unstack().fillna(0).stack().reset_index()
    cycle_mean= df_cycle_time_interval.groupby(['work_year_week','smooth_family']).agg(cycle_mean_week_count=('cycle_time','mean')).unstack().fillna(0).stack().reset_index()
    
    # split year week to sort orderd values
    cycle_mean['year']=cycle_mean['work_year_week'].str.split('-W').str[0].astype(int)
    cycle_mean['week']=cycle_mean['work_year_week'].str.split('-W').str[1].astype(int)
    cycle_mean=cycle_mean.sort_values(by=['year','week']).reset_index()

    week_cycle_mean_axis_x=cycle_mean['work_year_week'].unique()
    smooth_family= cycle_mean['smooth_family'].unique()


    cycle_mean_month= df_cycle_time_interval.groupby(['work_year_month','smooth_family']).agg(cycle_mean_month_count=('cycle_time','mean')).unstack().fillna(0).stack().reset_index()
    # split year month to sort orderd values
    cycle_mean_month['year']=cycle_mean_month['work_year_month'].str.split('-M').str[0].astype(int)
    cycle_mean_month['week']=cycle_mean_month['work_year_month'].str.split('-M').str[1].astype(int)
    cycle_mean_month=cycle_mean_month.sort_values(by=['year','week']).reset_index()
    month_cycle_mean_axis_x=cycle_mean_month['work_year_month'].unique()
    smooth_family_month= cycle_mean_month['smooth_family'].unique()

    ### for week 
    # list of colors
    colors_list=['#f39763','#0b2659','#1A9DD9','#E8E8DE','#68C1B6','#EC6462','#F2E8B8','#9e2a2b']
    # get colors for len smooth_family
    colors = [colors_list[color] for color in range(len(list(smooth_family)))]
    # dict of smooth_family(keys) and color (values)
    cycle_time_kpi.smooth_family=dict(zip(list(smooth_family),colors))
    cycle_time_kpi.cycle_mean=cycle_mean
    cycle_time_kpi.week_cycle_mean_axis_x=week_cycle_mean_axis_x

    ### for month
    colores_list_month=['#f39763','#0b2659','#1A9DD9','#E8E8DE','#68C1B6','#EC6462','#F2E8B8','#9e2a2b']
    # get colors for len smooth_family_month
    colors_month = [colores_list_month[color] for color in range(len(list(smooth_family_month)))]
    # dict of smooth_family_month(keys) and color (values)
    cycle_time_kpi.smooth_family_month=dict(zip(list(smooth_family_month),colors_month))
    cycle_time_kpi.cycle_mean_month=cycle_mean_month
    cycle_time_kpi.month_cycle_mean_axis_x=month_cycle_mean_axis_x

   
# to calculate production plan (Freeze_end_date or smoothing_end_date) (week and month)
def production_plan_kpi(df_data,date_from,date_to): 

    df_data['date_production']=np.where((pd.to_datetime(df_data['Freeze_end_date'],errors='coerce').dt.date),(pd.to_datetime(df_data['smoothing_end_date'],errors='coerce').dt.date),(pd.to_datetime(df_data['Freeze_end_date'],errors='coerce').dt.date))
    if date_from and date_to:

        # get df between two dates
        df_production_plan_kpi_interval= df_data[(df_data['date_production'] >= date_from.date()) & (df_data['date_production'] <= date_to.date())]
    else:
        df_production_plan_kpi_interval = df_data
    
    
    # week of date date_production
    df_production_plan_kpi_interval['date_production_week']=pd.to_datetime(df_production_plan_kpi_interval['date_production'],errors='coerce').dt.week
    # month of date_production
    df_production_plan_kpi_interval['date_production_month']=pd.to_datetime(df_production_plan_kpi_interval['date_production'],errors='coerce').dt.month
    # year of date_production
    df_production_plan_kpi_interval['date_production_year']=pd.to_datetime(df_production_plan_kpi_interval['date_production'],errors='coerce').dt.year
    #  to convert date_production_week,date_production_month, date_production_year column type float64 to int64
    df_production_plan_kpi_interval[['date_production_week','date_production_month','date_production_year']]=df_production_plan_kpi_interval[['date_production_week','date_production_month','date_production_year']].fillna(value=0)
    df_production_plan_kpi_interval[['date_production_week','date_production_month','date_production_year']]=df_production_plan_kpi_interval[['date_production_week','date_production_month','date_production_year']].astype('int64')
    
    # concatenate year and week
    df_production_plan_kpi_interval['date_production_year_week']=df_production_plan_kpi_interval['date_production_year'].astype(str)+'-'+'W'+df_production_plan_kpi_interval['date_production_week'].astype(str)
    # concatenate year and month
    df_production_plan_kpi_interval['date_production_year_month']=df_production_plan_kpi_interval['date_production_year'].astype(str)+'-'+'M'+df_production_plan_kpi_interval['date_production_month'].astype(str)
    

    date_production_week=df_production_plan_kpi_interval.groupby(['date_production_year_week']).agg(date_production_week_count=('division','count')).reset_index()
    date_production_month=df_production_plan_kpi_interval.groupby(['date_production_year_month']).agg(date_production_month_count=('division','count')).reset_index()
    # to delete date production when equal 1900-W1
    date_production_week.drop(date_production_week[date_production_week['date_production_year_week'] == "1900-W1"].index, inplace = True)
    date_production_week.drop(date_production_week[date_production_week['date_production_year_week'] == "0-W0"].index, inplace = True)
    date_production_month.drop(date_production_month[date_production_month['date_production_year_month'] == "0-M0"].index, inplace = True)
    date_production_month.drop(date_production_month[date_production_month['date_production_year_month'] == "1900-M1"].index, inplace = True)
    
    
    production_plan_kpi.date_production_week =date_production_week
    production_plan_kpi.date_production_month =date_production_month
   

# to calculate logistic stock per week and per month 
def logistic_stock_kpi(date_from_year_week, date_to_year_week,date_from_year_month,date_to_year_month): 
    
    # to reate new dataframes 
    Df_calcul_logistic_stock_week = production_plan_kpi.date_production_week[['date_production_year_week','date_production_week_count']].copy()
    Df_calcul_logistic_stock_month = production_plan_kpi.date_production_month[['date_production_year_month','date_production_month_count']].copy()
    
    # to filter data frame between two dates
    # if date_from_year_week and date_to_year_week and date_from_year_month and date_to_year_month:
    #     monday_date_from_year_week = datetime.strptime(date_from_year_week+'-1','%Y-W%W-%w')
    #     monday_date_to_year_week = datetime.strptime(date_to_year_week+'-1','%Y-W%W-%w')
        
    #     first_day_date_from_year_month = datetime.strptime(date_from_year_month+'-1','%Y-M%m-%w')
    #     first_date_to_year_month = datetime.strptime(date_to_year_month+'-1','%Y-M%m-%w')


    #     Df_calcul_logistic_stock_week['monday_date_production_year_week']= pd.to_datetime(Df_calcul_logistic_stock_week['date_production_year_week'].astype(str) + "-1", format= '%Y-W%W-%w')
    #     Df_calcul_logistic_stock_month['first_date_production_year_month']= pd.to_datetime(Df_calcul_logistic_stock_month['date_production_year_month'].astype(str) + "-1", format= '%Y-M%m-%w')
        

    #     Df_calcul_logistic_stock_week=Df_calcul_logistic_stock_week[(Df_calcul_logistic_stock_week['monday_date_production_year_week'] >= monday_date_from_year_week) & (Df_calcul_logistic_stock_week['monday_date_production_year_week'] <= monday_date_to_year_week)]
    #     Df_calcul_logistic_stock_month=Df_calcul_logistic_stock_month[(Df_calcul_logistic_stock_month['first_date_production_year_month'] >= first_day_date_from_year_month) & (Df_calcul_logistic_stock_month['first_date_production_year_month'] <= first_date_to_year_month)]
    # else:
    Df_calcul_logistic_stock_week
    Df_calcul_logistic_stock_month
    
    # to get data from zpp
    zpp_data=Zpp.objects.values('plan_date','element')
    zpp_data_df=pd.DataFrame(zpp_data.values())
    zpp_data_df['element_stock_stkcli']=np.where((zpp_data_df['element'].str.startswith(('Stock','StkCli'))),('true'),('false'))
    
    # to filter zpp_data_df column element_stock_stkcli rqual true
    zpp_data_df= zpp_data_df[zpp_data_df['element_stock_stkcli']=='true']
    

    zpp_data_df['plan_date_week']=pd.to_datetime(zpp_data_df['plan_date'],errors='coerce').dt.week
    zpp_data_df['plan_date_month']=pd.to_datetime(zpp_data_df['plan_date'],errors='coerce').dt.month
    zpp_data_df['plan_date_year']=pd.to_datetime(zpp_data_df['plan_date'],errors='coerce').dt.year


    zpp_data_df['plan_date_year_week']=zpp_data_df['plan_date_year'].astype(str)+'-'+'W'+zpp_data_df['plan_date_week'].astype(str)
    zpp_data_df['plan_date_year_month']=zpp_data_df['plan_date_year'].astype(str)+'-'+'M'+zpp_data_df['plan_date_month'].astype(str)

    #  to calculate stock initial from zpp file
    week_initial_stock_count=zpp_data_df.groupby(['plan_date_year_week','element_stock_stkcli']).agg(week_initial_stock_count=('id','count')).reset_index()
    month_initial_stock_count=zpp_data_df.groupby(['plan_date_year_month','element_stock_stkcli']).agg(month_initial_stock_count=('id','count')).reset_index()


    # to map date_production_year_month and dict_demand_prod_date_id
    dict_demand_prod_date_week_value=dict(zip(demand_prod_planning.demand_prod_week['date_year_week'],demand_prod_planning.demand_prod_week['demand_prod_count_week']))
    Df_calcul_logistic_stock_week['date_demand_prod_value'] =Df_calcul_logistic_stock_week['date_production_year_week'].map(dict_demand_prod_date_week_value).fillna(0)


    # to map date_production_year_month and dict_demand_prod_date_id
    dict_demand_prod_date_month_value=dict(zip(demand_prod_planning.demand_prod_month['date_year_month'],demand_prod_planning.demand_prod_month['demand_prod_of_month_count']))
    Df_calcul_logistic_stock_month['dict_demand_prod_date_month_value'] = Df_calcul_logistic_stock_month['date_production_year_month'].map(dict_demand_prod_date_month_value).fillna(0)


    # to map date_production_year_week and dict_demand_prod_date_id
    dict_demand_prod_date_id=dict(zip(week_initial_stock_count['plan_date_year_week'],week_initial_stock_count['week_initial_stock_count'])) 
    Df_calcul_logistic_stock_week['week-1']= Df_calcul_logistic_stock_week['date_production_year_week'].str[6:].astype(int) - 1
    Df_calcul_logistic_stock_week['year'] = Df_calcul_logistic_stock_week['date_production_year_week'].str[:4].astype(str)
    
    # to replace week 0 to 52 and year to year -1 
    Df_calcul_logistic_stock_week['year-1'] = np.where(Df_calcul_logistic_stock_week['week-1'] == 0, (Df_calcul_logistic_stock_week['year'].astype(int) - 1), Df_calcul_logistic_stock_week['year'])
    Df_calcul_logistic_stock_week['week-1'] = np.where(Df_calcul_logistic_stock_week['week-1'] == 0, (52), Df_calcul_logistic_stock_week['week-1'])
    

    Df_calcul_logistic_stock_week['production_plan_year_week-1'] = (Df_calcul_logistic_stock_week['year-1'].astype(str)+ '-'+ 'W'+ Df_calcul_logistic_stock_week['week-1'].astype(str))    
    Df_calcul_logistic_stock_week['plan_date_value'] = Df_calcul_logistic_stock_week['production_plan_year_week-1'].map(dict_demand_prod_date_id).fillna(0)
    


    # to map date_production_year_month and dict_demand_prod_date_month_value
    dict_demand_prod_date_month_value=dict(zip(month_initial_stock_count['plan_date_year_month'],month_initial_stock_count['month_initial_stock_count']))
    Df_calcul_logistic_stock_month['month-1']= Df_calcul_logistic_stock_month['date_production_year_month'].str[6:].astype(int) - 1
    Df_calcul_logistic_stock_month['year'] = Df_calcul_logistic_stock_month['date_production_year_month'].str[:4].astype(str)
    Df_calcul_logistic_stock_month['year-1'] = np.where(Df_calcul_logistic_stock_month['month-1'] == 0, (Df_calcul_logistic_stock_month['year'].astype(int) - 1), Df_calcul_logistic_stock_month['year'])
    Df_calcul_logistic_stock_month['month-1'] = np.where(Df_calcul_logistic_stock_month['month-1'] == 0, (12), Df_calcul_logistic_stock_month['month-1'])
    
    Df_calcul_logistic_stock_month['production_plan_year_month-1'] = Df_calcul_logistic_stock_month['year-1'].astype(str)+ '-'+ 'M' + Df_calcul_logistic_stock_month['month-1'].astype(str)
    
    Df_calcul_logistic_stock_month['plan_date_value'] = Df_calcul_logistic_stock_month['production_plan_year_month-1'].map(dict_demand_prod_date_month_value).fillna(0)


   
    # to calculate logitic stock per week 
    Df_calcul_logistic_stock_week['logistic_stock_week_count'] = Df_calcul_logistic_stock_week['plan_date_value'] + Df_calcul_logistic_stock_week['date_production_week_count'] - Df_calcul_logistic_stock_week['date_demand_prod_value']
    # to calculate logitic stock per month
    Df_calcul_logistic_stock_month['logistic_stock_month_count'] = Df_calcul_logistic_stock_month['plan_date_value'] + Df_calcul_logistic_stock_month['date_production_month_count'] - Df_calcul_logistic_stock_month['dict_demand_prod_date_month_value']

    
    logistic_stock_kpi.logistic_stock_week = Df_calcul_logistic_stock_week
    logistic_stock_kpi.logistic_stock_month = Df_calcul_logistic_stock_month



