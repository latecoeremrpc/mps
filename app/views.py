from datetime import datetime, timedelta
from io import StringIO
import numpy as np
import pandas as pd
import psycopg2
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
    return render(request, "app/division/home_division.html", {'data':data,'form':form})


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
    return render(request, "app/product/product.html", {'data':data,'division':division,'form':form,'division_info':division_info})


#*********************CRUD Material************************

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
    return render(request, "app/material/material.html", {'data':data,'division':division,'product':product,'form':form,'product_info':product_info})

#******************** calendar****************************

def calendar(request,division,product):
    #get smooth family from product
    smooth_family= Material.undeleted_objects.filter(product_id = product).values_list('Smooth_Family',flat=True).distinct().order_by('Smooth_Family')
    # get cycle objects
    cycle=Cycle.undeleted_objects.all().filter(product_id = product, owner = 'officiel')
    # get product object to display in calendar
    products_data= Product.undeleted_objects.all()
    # get all work data objects to display in Calendar
    workdata = WorkData.undeleted_objects.all().filter(product_id = product, owner = 'officiel')
    # get all holiday objects to display in Calendar
    holidays = HolidaysCalendar.undeleted_objects.all().filter(product_id = product, owner = 'officiel') 
    # get cycle ifo and workdata infos to display in Calendar
    product_info=Product.objects.all().filter(id=product).first()  
    return render(request, "app/calendar/calendar.html",{'product':product,'division':division,'holidays':holidays,'workdata':workdata,'products_data':products_data,'smooth_family': smooth_family,'cycle': cycle,'product_info':product_info})


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
            holiday=HolidaysCalendar.objects.all().filter(id=id).first()  #intilisation object
            if startDate == endDate:
                startDate= datetime.strptime(startDate,'%m/%d/%Y')
                endDate= datetime.strptime(endDate,'%m/%d/%Y')
                #update attributes values with new values
                holiday.holidaysDate= startDate
                holiday.name=name
                #save
                holiday.save()
        else:
        # add one day in database
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
    
#********************Custom calendar**********************

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
    return render(request,"app/calendar/custom_calendar.html",{'product':product,'division':division,'holidays':holidays,'work':work,'smooth_family': smooth_family,'cycle':cycle,'product_info':product_info})
    
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
                                new_cycle_time= float(j) * work_hours
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
    return render(request,"app/calendar/custom_calendar.html",{'product':product,'division':division, 'work':work}) 

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
    return render(request, "app/CalendarConfigurationTraitement/home_conf_traitement.html", {'data':data,'division':division,'product':product,'form':form,'product_info':product_info})


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
    return render(request, "app/CalendarConfigurationCpordo/home_conf_cpordo.html", {'data':data,'division':division,'product':product,'form':form,'product_info':product_info})

#********************** Home***********************************

def home_page(request):
    divisions = Division.undeleted_objects.all()
    division=products=None
    current_user = request.user
    try:
        staff_connected = Staff.objects.values_list('division',flat=True).filter(username = current_user.username).first()
        products= Product.undeleted_objects.all().filter(division__id= staff_connected)
        division= staff_connected

        if request.method == "POST":
            divisionName = request.POST.get('division')
            divisionId = Division.undeleted_objects.values('id').filter(name=divisionName).first()
            products= Product.undeleted_objects.all().filter(division__id= divisionId['id'])
            division=divisionId['id']
    except Exception:
        messages.error(request,"User not connected!")     

    return render(request,'app/home/index.html', {'division':division, 'divisions':divisions,'products':products})

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
    product_info=Product.objects.all().filter(id=product).first()
    all_planning=PlanningApproval.objects.all().filter(product=product)      
    return render(request,'app/Shopfloor/all_planning.html',{'all_planning':all_planning,'division':division,'product':product,'product_info':product_info})
   
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
            messages.error(request,"Name exit! try again")
            return redirect('../newplanning')
    return render(request,'app/Shopfloor/new_planning.html',{'division':division,'product':product,'product_info':product_info})


def update_planning(request,division,product,planningapproval):
    
    planning_approval_name_list=list(PlanningApproval.objects.values_list('name',flat=True).filter(product=product))

    return render(request,'app/Shopfloor/new_planning.html',{'division':division,'product':product})


def palnning_details(request,division,product,planningapproval):
    
    version = Shopfloor.objects.values_list('version',flat=True).filter(product=product,planning_approval_id=planningapproval).order_by('-version').first()
    
    return filter_kpi(request,division,product,planningapproval,version)
    # return render(request,'app/shopfloor/planning_details.html',{'planningapproval_info':planningapproval_info,'division':division,'product':product,'versions':versions})  


#*********************Upload To DB COOIS************************
# From upload coois
def upload_coois(request,division,product,planningapproval):  
    coois_files= Coois.objects.filter(product_id = product, product__division = division,planning_approval_id=planningapproval).values('created_at','created_by').distinct() 
    # planning approval for info page
    planningapproval_info=PlanningApproval.objects.all().filter(id=planningapproval).first() 
    if request.method == 'POST' and request.FILES['coois']:
        # Delete coois data 
        coois_data = Coois.undeleted_objects.all().filter(product=product,created_by='Marwa')
        coois_data.delete()
        file=request.FILES['coois']
        try:
            conn = psycopg2.connect(host='localhost',dbname='mps_database',user='postgres',password='admin',port='5432')
            import_coois(file,conn,product,planningapproval)
            messages.success(request,"COOIS file uploaded successfully!") 
            return redirect('./uploadzpp')
        except Exception:
            messages.error(request,"unable to upload files,not exist or unreadable") 
 
    return render(request,'app/files/coois.html',{'planningapproval_info':planningapproval_info,'division':division,'product':product,'planningapproval':planningapproval,'coois_files':coois_files})  

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
        zpp_data = Zpp.undeleted_objects.all().filter(product=product,created_by='Marwa')
        zpp_data.delete()
        #Save file to DB
        try:
            conn = psycopg2.connect(host='localhost',dbname='mps_database',user='postgres',password='admin',port='5432')
            import_zpp(file,conn,product,planningapproval)
            messages.success(request,"ZPP file uploaded successfully!") 
            return redirect("../needs")    
        except Exception:
            messages.error(request,"unable to upload ZPP files,not exist or unreadable") 

    return render(request,'app/files/zpp.html',{'planningapproval_info':planningapproval_info,'division':division,'product':product,'planningapproval':planningapproval, 'zpp_files':zpp_files})  
    
def import_zpp(file,conn,product,planningapproval):
    #read file with pandas
    dc=pd.read_excel(file,names=['material','plan_date','element','data_element_planif','message','needs','qte_available','date_reordo','supplier','customer'])
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
    dc['data_element_planif']= dc['data_element_planif'].str.split("/").str[0]
    # delete the zeros on the left
    dc['data_element_planif']= dc['data_element_planif'].str.lstrip("0")
    
    

    # Using the StringIO method to set
    # as file object
    zpp = StringIO()
    #convert file to csv
    zpp.write(dc.to_csv(index=None , header=None,sep=';'))
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
    # name of planning approval for info page
    planningapproval_info=PlanningApproval.objects.all().filter(id=planningapproval).first()  
    # data for merge
    zpp_data=Zpp.objects.filter(created_by= 'Marwa').values('material','data_element_planif','created_by','message','date_reordo','product__Profit_center','product__division__name')
    coois_data= Coois.objects.all().filter(created_by= 'Marwa').values()
    material_data=Material.undeleted_objects.values('material','product__Profit_center','product__planning','product__division__name','created_by','workstation','AllocatedTime','Leadtime','Allocated_Time_On_Workstation','Smooth_Family')

    #Convert data to DataFrame
    df_zpp=pd.DataFrame(list(zpp_data))
    df_coois=pd.DataFrame(list(coois_data))
    df_material=pd.DataFrame(list(material_data))
    
    # rename df_material column 
    df_material=df_material.rename(columns={'product__planning':'planning','product__division__name':'division','product__Profit_center':'profit_center'})
     # rename df_zpp column 
    df_zpp=df_zpp.rename(columns={'product__division__name':'division','product__Profit_center':'profit_center'})
    
    #add column key for zpp (concatinate  material and data_element_planif and created_by  )
    df_zpp['key']=df_zpp['material'].astype(str)+df_zpp['division'].astype(str)+df_zpp['profit_center'].astype(str)+df_zpp['data_element_planif'].astype(str)+df_zpp['created_by'].astype(str)
    #add column key for coois (concatinate material, order, created_by )    
    df_coois['key']=df_coois['material'].astype(str)+df_coois['division'].astype(str)+df_coois['profit_centre'].astype(str)+df_coois['order'].astype(str)+df_coois['created_by'].astype(str)

    #add column key for material (concatinate material, created_by )  
    df_material['key']=df_material['material'].astype(str)+df_material['division'].astype(str)++df_material['profit_center'].astype(str)+df_material['created_by'].astype(str)+df_material['planning'].astype(str)
    #add column key for coois (concatinate material,division,profit_centre, created_by )    
    df_coois['key2']=df_coois['material'].astype(str)+df_coois['division'].astype(str)+df_coois['profit_centre'].astype(str)+df_coois['created_by'].astype(str)+df_coois['designation'].astype(str)
    
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
    
    return render(request,'app/Shopfloor/Shopfloor.html',{'planningapproval_info':planningapproval_info,'planningapproval':planningapproval,'records': records,'division':division,'product':product}) 

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
        df=smoothing_calculate(df,calendar_type)

        # delete key,freezed, key_start_day column
        del df['key']
        del df['freezed']
        del df['key_start_day']
        # delete index from df
        df=df.reset_index(drop=True)
        # save shofloor with version 
        save_needs(df,product,planningapproval)
        messages.success(request,"Data saved successfully!") 
        return redirect(f'../result/')

# @allowed_users(allowed_roles=["Planificateur"]) 
#  calculate smoothing end date to use in create needs      
def smoothing_calculate(df_data,calendar_type):
    # make holidays and cycle_data as global varibale to reduce access to database
    global holidays, cycle_data
    if calendar_type == 'official':
        # we use holidays in is_in_open_hours function
        holidays = HolidaysCalendar.undeleted_objects.values_list('holidaysDate',flat=True).filter( owner = 'officiel') 
        # we use cycle_data in smoothing_calculate function
        cycle_data=Cycle.undeleted_objects.values('product__division__name','profit_center','smooth_family','cycle_time','work_day').filter( owner = 'officiel') 
        # print('cycle_data', cycle_data)
    else:
        holidays = HolidaysCalendar.undeleted_objects.values_list('holidaysDate',flat=True).filter( owner = 'marwa') 
        cycle_data=Cycle.undeleted_objects.values('product__division__name','profit_center','smooth_family','cycle_time','work_day').filter( owner = 'marwa') 
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

    df_closed_false= df_data[df_data['closed']=='False']
    
    
    df_closed_false = df_closed_false.sort_values(['Smooth_Family','Ranking']).reset_index()
    del df_closed_false['index']
    # filter df_data where closed == True
    df_closed_true = df_data[df_data['closed'] =='True']
    df_closed_true=df_closed_true.reset_index()
    del df_closed_true['index']
    
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
def save_needs(df,product,planningapproval):
    conn = psycopg2.connect(host='localhost',dbname='mps_database',user='postgres',password='admin',port='5432')
    # get version_data 
    version_number = Shopfloor.objects.values('version').filter(product=product,planning_approval_id=planningapproval).order_by('-version').first()
    version = version_number['version']+1 if version_number else 1
    
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

    df.to_csv('df_shopfloor_data_after_calcul.csv')

    # Using the StringIO method to set
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


# filter by division, profit_center and panning, week to get versions
def filter(request):
    divisions_list= Division.undeleted_objects.values('name').distinct().order_by('name')
    center_profit_list= Product.undeleted_objects.values('Profit_center').distinct().order_by('Profit_center')
    planning_list= Product.undeleted_objects.values('planning').distinct().order_by('planning')
    dates= Shopfloor.objects.values('created_at__year','created_at__week').distinct()

    division= profit_center= planning=versions= date =None

    if request.method == "POST":
        division= request.POST.get('division_name')
        profit_center= request.POST.get('center_profit')
        planning= request.POST.get('planning')
        date= request.POST.get('week')
        

        year=date.split(',')[0]
        week=date.split(',')[1]

        versions = Shopfloor.objects.values('version','shared').filter(division=division,profit_centre= profit_center,designation=planning,created_at__week__gte=week, created_at__year=year).distinct().order_by('version')
        
    return render( request,'app/Shopfloor/filter.html',{'divisions_list':divisions_list,'center_profit_list':center_profit_list,'planning_list':planning_list,
    'versions':versions,
    'division':division,
    'date':date,
    'profit_center':profit_center,
    'planning':planning,
    'dates':dates
    })

# def result diplay result of shoploor data with version  
def result(request,division,product,planningapproval):
    data= versions= selected_version = None
    product_data=Product.objects.values('Profit_center','planning','division__name').filter(id =product).first()
    last_version = Shopfloor.objects.values_list('version', flat=True).filter(product=product,profit_centre=product_data['Profit_center'],designation= product_data['planning'],planning_approval_id=planningapproval).order_by('-version').first()

    try:
        data=Shopfloor.objects.all().order_by('smoothing_end_date','closed','Smooth_Family','Ranking').filter(division=product_data['division__name'],product=product,profit_centre=product_data['Profit_center'],designation= product_data['planning'],version=last_version)
    except Exception:
        messages.error(request,"Empty data here,Please fill in needs") 
        return redirect("../needs")  

    versions =Shopfloor.objects.values('version').filter(product=product,profit_centre=product_data['Profit_center'],designation= product_data['planning'],planning_approval_id=planningapproval).distinct().order_by('version')

    if request.method=='POST':
        selected_version= request.POST.get('selected_version')
        selected_version=int(selected_version)
        data=Shopfloor.objects.all().order_by('smoothing_end_date','closed','Smooth_Family','Ranking').filter(division=product_data['division__name'],product=product,profit_centre=product_data['Profit_center'],designation= product_data['planning'],version=selected_version)
    # name of planning approval for info page
    planningapproval_info=PlanningApproval.objects.all().filter(id=planningapproval).first()   

    return render(request,'app/Shopfloor/result.html',{'planningapproval_info':planningapproval_info,
    'planningapproval':planningapproval,'records':data,'division':division,'product':product,
    'versions':versions,'selected_version':selected_version,'last_version':last_version})

    # return render(request,'app/kpi.html',{'division':division,'product':product,'planningapproval':planningapproval,'version_selected':version_selected})  

# filter planning result
def filter_kpi(request,division,product,planningapproval,version):
    # last version for page_info 
    # print(version)
    version = Shopfloor.objects.values_list('version',flat=True).filter(product=product,planning_approval_id=planningapproval).order_by('-version').first()
    # name of planning approval for info page
    planningapproval_info = PlanningApproval.objects.all().filter(id=planningapproval).first()
    # list of version
    planning_versions = Shopfloor.objects.values_list('version',flat=True).filter(product=product,planning_approval_id=planningapproval).distinct().order_by('-version') 

    df_data=df_cycle=df_work_days=smooth_family_selected=material_selected=from_date=to_date =date_from= date_to=version_selected=None
    demand_prod_planning.week_count=None
    demand_prod_planning.week_count_axis_x=None
    demand_prod_planning.month_count=None
    demand_prod_planning.month_count_axis_x=None
    cycle_time_kpi.cycle_count=None
    cycle_time_kpi.week_cycle_count_axis_x=None
    cycle_time_kpi.smooth_family=None
    cycle_time_kpi.smooth_family_month=None
    cycle_time_kpi.cycle_count_month=None
    cycle_time_kpi.month_cycle_count_axis_x=None
    production_plan_kpi.date_production_week=None
    production_plan_kpi.date_production_month=None
    demand_prod_planning.work_days_count =None
    demand_prod_planning.work_days_count_month=None
    
    if request.method == "POST" :
        if 'filter_sbumit' in request.POST:
            version = version_selected = request.POST.get('version_planning')
            from_date= request.POST.get('from')
            to_date= request.POST.get('to')
        if 'update_cycle_sbumit' in request.POST:
            version_selected = request.POST.get('version_selected')
            from_date= request.POST.get('from')
            to_date= request.POST.get('to')
            #Update Cycle
            update_cycle(request,division,product,planningapproval,version_selected)

            # convert dates input(str) to datetime
        date_from = datetime.strptime(from_date,'%Y-%m-%d')
        date_to = datetime.strptime(to_date,'%Y-%m-%d')

        #  get data for version
        if version_selected:
            data=Shopfloor.objects.all().filter(product=product,planning_approval_id=planningapproval,version=version_selected)
        else:
            data=Shopfloor.objects.all().filter(product=product,planning_approval_id=planningapproval,version=version)

        cycle_data=Cycle.undeleted_objects.all().filter(division=division,product=product,owner='officiel').distinct()
        # get workday to use in calcul 
        work_days=WorkData.undeleted_objects.values('date').filter(product__division=division,product=product,owner='officiel')
        
        if not data:
                messages.error(request,"No data with selected filter!") 
                return render(request,'app/kpi.html',{'division':division,'product':product,'from_date':from_date,'to_date':to_date,'planningapproval':planningapproval,'planningapproval_info':planningapproval_info,'planning_versions':planning_versions,'version_selected':version_selected})

        # convert data to dataframe
        df_data=pd.DataFrame(data.values())
        df_cycle=pd.DataFrame(cycle_data.values())
        df_work_days=pd.DataFrame(work_days.values())
        # date
        df_data['date']=np.where((df_data['date_reordo'].isna()),(df_data['date_end_plan']),(df_data['date_reordo']))
        # call function demand_prod_planning
        demand_prod_planning(df_data,df_work_days,date_from,date_to)
        # call function demand_prod_planning
        production_plan_kpi(df_data,date_from,date_to)
        if cycle_data:
            # call function cycle_time_kpi 
            cycle_time_kpi(df_cycle,date_from,date_to)

        # for sharing kpi
        # if request.method == "POST":
        #     version= request.POST.get('version')
        #     from_date= request.POST.get('from')
        #     to_date= request.POST.get('to')
        #     data=Shopfloor.objects.all().filter(product= product,planning_approval=planningapproval)
        #     data.update(shared=False)
        #     # check if version selected
        #     data=Shopfloor.objects.all().filter(version=version_selected,product= product,planning_approval=planningapproval)
        #     data.update(shared=True)
    
    
    return render(request,'app/kpi.html',{'planningapproval_info':planningapproval_info,'planningapproval':planningapproval,
    'version_selected':version_selected,
    'version':version,
    'planning_versions':planning_versions,
    'division':division,'product':product,
    'records':df_data,
    'df_cycle':df_cycle,
    'df_work_days':df_work_days,
    'from_date':from_date,
    'to_date':to_date,
    'date_from':date_from,
    'date_to':date_to,
    'smooth_family_selected':smooth_family_selected,
    'material_selected':material_selected,
    'week_count':demand_prod_planning.week_count,
    'week_count_axis_x':demand_prod_planning.week_count_axis_x,
    'month_count':demand_prod_planning.month_count,
    'month_count_axis_x':demand_prod_planning.month_count_axis_x,
    'cycle_count':cycle_time_kpi.cycle_count,
    'week_cycle_count_axis_x':cycle_time_kpi.week_cycle_count_axis_x,
    'smooth_family': cycle_time_kpi.smooth_family,
    'cycle_count_month':cycle_time_kpi.cycle_count_month,
    'month_cycle_count_axis_x':cycle_time_kpi.month_cycle_count_axis_x,
    'smooth_family_month':cycle_time_kpi.smooth_family_month,
    'date_production_week':production_plan_kpi.date_production_week,
    'date_production_month':production_plan_kpi.date_production_month,
    'work_days_count_week': demand_prod_planning.work_days_count,
    'work_days_count_month':demand_prod_planning.work_days_count_month,
    })

# Adjust cycle time  
def update_cycle(request,division,product,planningapproval,version_selected):
    smooth_family_list=cycle_time_list=week_cycle=None
    # to use info page
    if version_selected == None:
        pass
        print('my version:',version_selected)
    else:
        version_selected = Shopfloor.objects.values_list('version',flat=True).filter(product=product,planning_approval_id=planningapproval).order_by('-version').first()
    
    if request.method == "POST":
        smooth_family_list= request.POST.getlist('smooth_family')
        cycle_time_list= request.POST.getlist('cycle_time')
        week_cycle= request.POST.getlist('week_cycle')
        # from_date= request.POST.get('from')
        # to_date= request.POST.get('to')
       
        for date ,cycle_time in dict(zip(week_cycle,cycle_time_list)).items():
            # get year and week from table 
            year=date.split('-W')[0]
            week=date.split('-W')[1]
            #get cycle type hours or days
            cycle_type_input = request.POST.get('cycle-type-'+date)

            #Get Cycle to update
            cycles=Cycle.objects.all().filter(division=division,product=product,work_day__year=year,work_day__week=week,smooth_family__in=smooth_family_list) 
            
            for cycle_to_update in cycles:
                # get startTime and endTime  
                startTime = WorkData.objects.values('startTime').filter(id=cycle_to_update.workdata_id).first()
                endTime = WorkData.objects.values('endTime').filter(id=cycle_to_update.workdata_id).first()
                # convert startTime and endTime(datetime.time) to datetime.datetime
                start_time = datetime(1, 1, 1,startTime['startTime'].hour,startTime['startTime'].minute)
                end_time = datetime(1, 1, 1,endTime['endTime'].hour,endTime['endTime'].minute)
                if cycle_type_input == 'Days':
                    cycle_to_update.cycle_time= float(cycle_time) * work_hours(start_time,end_time)
                elif cycle_type_input == 'Hours':
                    cycle_to_update.cycle_time= float(cycle_time)
                cycle_to_update.save()
                 # Get DF
        shopfloor_data=Shopfloor.objects.filter(
                                                version=version_selected,
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
        df=smoothing_calculate(df_shopfloor_data,calendar_type)
        # delete key,freezed, key_start_day column
        del df['key']
        del df['freezed']
        del df['key_start_day']
        # delete index from df
        df=df.reset_index(drop=True)
        # =>  save_needs (df, product, planningapproval)
        save_needs(df,product,planningapproval)
    # return filter_kpi(request,division,product,planningapproval,version_selected)
                
    # return render(request,'app/kpi.html',{'from_date':from_date,'to_date':to_date,'last_version':last_version,'planningapproval_info':planningapproval_info,'planningapproval':planningapproval,'division':division,'product':product,'smooth_family':smooth_family,'cycle_time_list':cycle_time_list,'week_cycle':week_cycle})   

# calculate nomber of OF and OP ( wek and month)
def demand_prod_planning(df_data,df_work_days,date_from,date_to):
    # get df between two dates
    df_data_demand_prod_interval=df_data[(df_data['date'] > date_from.date()) & (df_data['date'] <= date_to.date())]
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

    week_count=df_data_demand_prod_interval.groupby(['date_year_week','order_nature_closed'])['id'].count().unstack().fillna(0).stack().reset_index()
    # get year from date_year_week 
    week_count['year']=week_count['date_year_week'].str.split('-W').str[0].astype(int)
    # get week from date_year_week 
    week_count['week']=week_count['date_year_week'].str.split('-W').str[1].astype(int)
    # sort values with year week (to get orderd values(year, week))
    week_count=week_count.sort_values(by=['year','week']).reset_index()
    # get unique date_year_week (because value date_year_week duplicate)
    week_count_axis_x=week_count['date_year_week'].unique()
    
    ### month
    month_count=df_data_demand_prod_interval.groupby(['date_year_month','order_nature_closed'])['id'].count().unstack().fillna(0).stack().reset_index()
    month_count['year']=month_count['date_year_month'].str.split('-M').str[0].astype(int)
    month_count['week']=month_count['date_year_month'].str.split('-M').str[1].astype(int)
    month_count=month_count.sort_values(by=['year','week']).reset_index()
    month_count_axis_x=month_count['date_year_month'].unique()
    
    demand_prod_planning.week_count=week_count
    demand_prod_planning.week_count_axis_x=week_count_axis_x
    demand_prod_planning.month_count=month_count
    demand_prod_planning.month_count_axis_x=month_count_axis_x

    
    # calcul Demonstrated capacity (week and month)
    # get current_date 
    current_date = datetime.now()
    # get previous_month
    previous_month =current_date - relativedelta(months=1)
    df_prev_month = df_data[(df_data['date'] > previous_month.date()) & (df_data['date'] <= current_date.date())]

    #  calcul sum of closed in previous_month
    df_prev_month_closed=df_prev_month[df_prev_month['closed']==True]
    previous_month_closed_count=df_prev_month_closed.shape[0]

    #calcul number of work_days in previous_month
    work_days_in_previous_month = df_work_days[(df_work_days['date'] >= previous_month.date()) & (df_work_days['date'] <= current_date.date())]
    work_days_in_previous_month_count = work_days_in_previous_month.shape[0]
    

    # calcul number of work_days in period(week)
    df_work_days['date_week']=pd.to_datetime(df_work_days['date'], errors='coerce').dt.week
    df_work_days['date_year']=pd.to_datetime(df_work_days['date'], errors='coerce').dt.year
    work_days_count=df_work_days.groupby(['date_week','date_year'])['id'].count().reset_index()
    work_days_count['date_year_week']= work_days_count['date_year'].astype(str)+'-'+'W'+work_days_count['date_week'].astype(str)
    work_days_count = work_days_count[work_days_count['date_year_week'].isin(week_count_axis_x)]
    

    # calcul number of work_days in period(month)
    df_work_days['date_month']=pd.to_datetime(df_work_days['date'], errors='coerce').dt.month
    work_days_count_month=df_work_days.groupby(['date_month','date_year'])['id'].count().reset_index()
    work_days_count_month['date_year_month']= work_days_count_month['date_year'].astype(str)+'-'+'M'+work_days_count_month['date_month'].astype(str)
    work_days_count_month = work_days_count_month[work_days_count_month['date_year_month'].isin(month_count_axis_x)]
    
    
    # test if work_days_in_previous_month_count == 0
    if work_days_in_previous_month_count == 0 :
        work_days_count['result_demonstrated_capacity'] = 0
        work_days_count_month['result_demonstrated_capacity'] = 0
    else:
        work_days_count['result_demonstrated_capacity'] = work_days_count['id'] * (previous_month_closed_count / work_days_in_previous_month_count)
        work_days_count_month['result_demonstrated_capacity'] = work_days_count_month['id'] * (previous_month_closed_count / work_days_in_previous_month_count)


    demand_prod_planning.work_days_count=work_days_count
    demand_prod_planning.work_days_count_month=work_days_count_month

# Kpi cycle time per smooth family (week and month)
def cycle_time_kpi(df_data,date_from,date_to):
    
    df_cycle_time_interval = df_data[(df_data['work_day'] > date_from.date()) & (df_data['work_day'] <= date_to.date())]

    # work_day_week
    df_cycle_time_interval['work_day_week']=pd.to_datetime(df_cycle_time_interval['work_day'],errors='coerce').dt.week
    # work_day_month
    df_cycle_time_interval['work_day_month']=pd.to_datetime(df_cycle_time_interval['work_day'],errors='coerce').dt.month
    # work_day_year
    df_cycle_time_interval['work_day_year']=pd.to_datetime(df_cycle_time_interval['work_day'], errors='coerce').dt.year
    # concatenate year and week
    df_cycle_time_interval['work_year_week']=df_cycle_time_interval['work_day_year'].astype(str)+'-'+'W'+df_cycle_time_interval['work_day_week'].astype(str)
    # concatenate year and month
    df_cycle_time_interval['work_year_month']=df_cycle_time_interval['work_day_year'].astype(str)+'-'+'M'+df_cycle_time_interval['work_day_month'].astype(str)

    
    cycle_count= df_cycle_time_interval.groupby(['work_year_week','smooth_family'])['cycle_time'].mean().unstack().fillna(0).stack().reset_index()
    cycle_count['year']=cycle_count['work_year_week'].str.split('-W').str[0].astype(int)
    cycle_count['week']=cycle_count['work_year_week'].str.split('-W').str[1].astype(int)
    cycle_count=cycle_count.sort_values(by=['year','week']).reset_index()
    # cycle_count=cycle_count.rename(columns={'0':'cycle_time'})
    # cycle_count.to_csv('test2.csv') 

    week_cycle_count_axis_x=cycle_count['work_year_week'].unique()
    smooth_family= cycle_count['smooth_family'].unique()
    

    cycle_count_month= df_cycle_time_interval.groupby(['work_year_month','smooth_family'])['cycle_time'].mean().unstack().fillna(0).stack().reset_index()
    cycle_count_month['year']=cycle_count_month['work_year_month'].str.split('-M').str[0].astype(int)
    cycle_count_month['week']=cycle_count_month['work_year_month'].str.split('-M').str[1].astype(int)
    cycle_count_month=cycle_count_month.sort_values(by=['year','week']).reset_index()
    month_cycle_count_axis_x=cycle_count_month['work_year_month'].unique()
    smooth_family_month= cycle_count_month['smooth_family'].unique()
    
    ### for week 
    # list of colors
    colors_list=['#34a0a4','#023e8a','#e9c46a','#ffafcc','#2a9d8f','#e5989b','#e56b6f','#9e2a2b']
    # get colors for len smooth_family
    colors = [colors_list[color] for color in range(len(list(smooth_family)))]
    # dict of smooth_family(keys) and color (values)
    cycle_time_kpi.smooth_family=dict(zip(list(smooth_family),colors))
    cycle_time_kpi.cycle_count=cycle_count
    cycle_time_kpi.week_cycle_count_axis_x=week_cycle_count_axis_x
   
    ### for month
    colores_list_month=['#34a0a4','#023e8a','#e9c46a','#ffafcc','#2a9d8f','#e5989b','#e56b6f','#9e2a2b']
    # get colors for len smooth_family_month
    colors_month = [colores_list_month[color] for color in range(len(list(smooth_family_month)))]
    # dict of smooth_family_month(keys) and color (values)
    cycle_time_kpi.smooth_family_month=dict(zip(list(smooth_family_month),colors_month))
    cycle_time_kpi.cycle_count_month=cycle_count_month
    cycle_time_kpi.month_cycle_count_axis_x=month_cycle_count_axis_x
    

# calculate production plan (Freeze_end_date or smoothing_end_date) (week and month)
def production_plan_kpi(df_data,date_from,date_to):
    # get df between two dates
    df_production_plan_kpi_interval=df_data[(df_data['date'] > date_from.date()) & (df_data['date'] <= date_to.date())]
    # date
    df_production_plan_kpi_interval['date_production']=np.where((df_production_plan_kpi_interval['Freeze_end_date'].isna()),(df_production_plan_kpi_interval['smoothing_end_date']),(df_production_plan_kpi_interval['Freeze_end_date']))
    # replace the nan values of date_production column with date_end_plan values
    df_production_plan_kpi_interval['date_production']=np.where((df_production_plan_kpi_interval['date_production'].isna()),(df_production_plan_kpi_interval['date_end_plan']),(df_production_plan_kpi_interval['date_production']))
    # df_production_plan_kpi_interval.date_production=df_production_plan_kpi_interval.date_production.fillna(df_production_plan_kpi_interval.date_end_plan, inplace=True)
    # week of date date_production
    df_production_plan_kpi_interval['date_production_week']=pd.to_datetime(df_production_plan_kpi_interval['date_production'],errors='coerce').dt.week
    # month of date_production
    df_production_plan_kpi_interval['date_production_month']=pd.to_datetime(df_production_plan_kpi_interval['date_production'],errors='coerce').dt.month
    # year of date_production
    df_production_plan_kpi_interval['date_production_year']=pd.to_datetime(df_production_plan_kpi_interval['date_production'],errors='coerce').dt.year
    # concatenate year and week
    df_production_plan_kpi_interval['date_production_year_week']=df_production_plan_kpi_interval['date_production_year'].astype(str)+'-'+'W'+df_production_plan_kpi_interval['date_production_week'].astype(str)
    # concatenate year and month
    df_production_plan_kpi_interval['date_production_year_month']=df_production_plan_kpi_interval['date_production_year'].astype(str)+'-'+'M'+df_production_plan_kpi_interval['date_production_month'].astype(str)
    

    date_production_week=df_production_plan_kpi_interval.groupby(['date_production_year_week'])['id'].count().reset_index()
    date_production_month=df_production_plan_kpi_interval.groupby(['date_production_year_month'])['id'].count().reset_index()

   

    production_plan_kpi.date_production_week =date_production_week
    production_plan_kpi.date_production_month =date_production_month

