from itertools import cycle, groupby
from django.http import HttpResponse
from django.shortcuts import render ,redirect ,get_object_or_404
from app.models import Division,Material,HolidaysCalendar,Product,WorkData,CalendarConfigurationTreatement,CalendarConfigurationCpordo,Coois,Zpp,Shopfloor,Cycle
from app.forms import DivisionForm,MaterialForm,ProductForm,CalendarConfigurationCpordoForm,CalendarConfigurationTreatementForm 
from datetime import  date, datetime, timedelta, time, timezone
from io import StringIO
import psycopg2, pandas as pd
import numpy as np
from django.contrib import messages
from app.decorators import allowed_users





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
def delete_division(request, id):
    # fetch the object related to passed id
    obj = get_object_or_404(Division, id = id)
    # delete object
    obj.soft_delete()
    #alert message
    messages.success(request,"Division deleted successfully!")
    return redirect("../")
    

# restore object(Division) by id
def restore_division(request, id):
    # fetch the object related to passed id
    obj = get_object_or_404(Division, id = id)
    # restore object
    obj.restore() 
    #alert message
    messages.success(request,"Division restored successfully!")
    return redirect("../")
    

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


# read all objects(Material)
def read_material(request):
    # undeleted_objects object of soft delete manager
    data = Material.objects.all().order_by('id')    
    return render(request, "app/material/materials.html", {'data':data})


#update object(Material) by id
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
def delete_material(request, division ,id):
    # fetch the object related to passed id
    obj = get_object_or_404(Material, id = id)
    # delete object
    obj.soft_delete()
    #alert message
    messages.success(request,"Material deleted successfully!")
    return redirect(f'../{str(obj.product_id)}/material/')
   

# restore object(Material) by id
def restore_material(request, division ,id):
    # fetch the object related to passed id
    obj = get_object_or_404(Material, id = id)
    # restore object
    obj.restore()
    #alert message
    messages.success(request,"Material restored successfully!")
    return redirect(f'../{str(obj.product_id)}/material/')    


# find all Material for product 
def material(request ,division, product):
    #get MaterialForm
    form = MaterialForm()
    # undeleted_objects object of soft delete manager
    data = Material.objects.filter(product__pk = product ).order_by('id')    
    return render(request, "app/material/material.html", {'data':data,'division':division,'product':product,'form':form})


#******************** calendar****************************
def calendar(request,division,product):
    #get smooth family from product
    smooth_family= Material.undeleted_objects.filter(product_id = product).values('Smooth_Family').distinct().order_by('Smooth_Family')
    # print('**********')
    print(smooth_family)
    # get cycle objects
    cycle=Cycle.undeleted_objects.all().filter(product_id = product, owner = 'officiel')
    #material_data=Material.undeleted_objects.filter(product_id = product).values('Smooth_Family').distinct().order_by('Smooth_Family')
    # get product object to display in calendar
    products_data= Product.undeleted_objects.all()
    # get all work data objects to display in Calendar
    workdata = WorkData.undeleted_objects.all().filter(product_id = product, owner = 'officiel')
    # get all holiday objects to display in Calendar
    holidays = HolidaysCalendar.undeleted_objects.all().filter(product_id = product, owner = 'officiel') 
    # get cycle ifo and workdata infos to display in Calendar
    #workdata=WorkData.objects.values('cycle__cycle_time','cycle__id','id','startTime','endTime','date','FTEhourByDay','ExtraHour','Absenteeism_ratio','Unproductiveness_ratio','Efficienty_ratio').filter(product_id = product, owner = 'officiel') 
    return render(request, "app/calendar/calendar.html",{'product':product,'division':division,'holidays':holidays,'workdata':workdata,'products_data':products_data,'smooth_family': smooth_family,'cycle': cycle})


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
                    print(day)
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
    #holidays = HolidaysCalendar.undeleted_objects.all().filter(product_id = product)
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
    #return render(request,"app/calendar/calendar.html",{'product':product} )
    
#********************Custom calendar****************************

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
    #return render(request,"app/calendar/custom_calendar.html", {'product':product,'holidays':custom_holidays})

#custom calendar
def custom_calendar(request,division,product):
    #get smooth family
    smooth_family= Material.undeleted_objects.filter(product_id = product).values('Smooth_Family').distinct().order_by('Smooth_Family')
    print('**************',smooth_family)
    #  get cycle data objects
    cycle= Cycle.undeleted_objects.all().filter(product_id = product ,owner = 'marwa')
    # material_data=Material.undeleted_objects.filter(product_id = product).values('Smooth_Family').distinct().order_by('Smooth_Family')
    # get all holiday objects to display in Calendar
    holidays = HolidaysCalendar.undeleted_objects.all().filter(product_id = product , owner = 'marwa') 
    # get all work data objects to display in Calendar    
    work = WorkData.undeleted_objects.all().filter(product_id = product ,owner = 'marwa')
    return render(request,"app/calendar/custom_calendar.html",{'product':product,'division':division,'holidays':holidays,'work':work,'smooth_family': smooth_family,'cycle':cycle})
    

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
def delete_day_custom(request,division,product):  # sourcery skip: avoid-builtin-shadow
    #holidays = HolidaysCalendar.undeleted_objects.all().filter(product_id = product)
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
    #return render(request,"app/calendar/custom_calendar.html",{'product':product,'holidays':holidays} )

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
            messages.success(request," Product updated successfully!")  
        else:
            messages.error(request," try again!")        
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
def product(request ,division):
    form = ProductForm()
    # undeleted_objects object of soft delete manager
    data = Product.objects.filter(division__pk = division ).order_by('id')    
    return render(request, "app/product/product.html", {'data':data,'division':division,'form':form})

#********************work Data****************************
#create work data for calendar
def work_data(request,division,product):
    work = WorkData.undeleted_objects.all().filter(product_id = product) 
    # get list of days from dataBase to compare if exist 
    days = list(work.values_list('date',flat=True))
    # get list of product_id from database to compare if exist
    products =list(WorkData.objects.values_list('product_id',flat=True))
    # test if method post and button save-work
    if request.method=='POST' and 'save-work' in request.POST:
        # get inputs from form
        #    workdata informations
        id = request.POST.get('event-index')
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
        # convert starttime and endtime to datetime
        start_time = datetime.strptime(startTime, '%H:%M:%S')
        end_time = datetime.strptime(endTime, '%H:%M:%S')
        if start_time == end_time :
            work_hours= 24
        elif end_time > start_time:
            work_hours= ((end_time - start_time).total_seconds() / 3600)
        else:
            work_hours = ((end_time+ timedelta(days =1)) - start_time ).total_seconds() / 3600
            
        

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
                        print(end_time)
                        print(type(end_time))
                        cycle_info.cycle_time= float(value) * work_hours
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
                    for i,j in zip(smooth_family,cycle_time):
                        cycle_type_input = request.POST.get('cycle-type-'+i)
                        if cycle_type_input == 'Days':
                            # new_cycle_time= float(j) * (endTime - startTime)
                            cycle_info.cycle_time=float(value) * work_hours
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
                            new_cycle_time= float(j) * work_hours
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
                                new_cycle_time= float(j) * work_hours
                            if cycle_type_input == 'Hours':
                                new_cycle_time=j
                            cycle_data=Cycle(work_day=day,division=division,profit_center=profit_center.get('Profit_center'),smooth_family=i,cycle_time=new_cycle_time,workdata_id=data.id,product_id = product)
                            cycle_data.save()  
                return redirect("../calendar")       
        
    # return render(request,"app/calendar/calendar.html",{'product':product,'division':division, 'work':work, 'cycle_time':cycle_time})
      
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

        start_time = datetime.strptime(startTime, '%H:%M:%S')
        end_time = datetime.strptime(endTime, '%H:%M:%S')
        if start_time == end_time :
            work_hours= 24
        elif end_time > start_time:
            work_hours= ((end_time - start_time).total_seconds() / 3600)
        else:
            work_hours = ((end_time+ timedelta(days =1)) - start_time ).total_seconds() / 3600

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
                        cycle_info.cycle_time=float(value) * 24
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
                            new_cycle_time= float(j) * work_hours
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
                            new_cycle_time= float(j) * work_hours
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
                                new_cycle_time= float(j) * work_hours
                            if cycle_type_input == 'Hours':
                                new_cycle_time=j
                            cycle_data=Cycle(work_day=day,division=division,profit_center=profit_center.get('Profit_center'),smooth_family=i,cycle_time=new_cycle_time,workdata_id=data.id,owner = owner,product_id = product)
                            cycle_data.save() 
                return redirect("../customcalendar")
    return render(request,"app/calendar/custom_calendar.html",{'product':product,'division':division, 'work':work}) 

#********************** CRUD CalendarConfigurationTraitement****************************

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
    id = id = request.POST.get('id')
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
    return render(request, "app/CalendarConfigurationTraitement/home_conf_traitement.html", {'data':data,'division':division,'product':product,'form':form})


#********************** CRUD CalendarConfigurationCpOrdo****************************

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
    id = id = request.POST.get('id')
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
def delete_conf_cpordo(request,division ,id):
    # fetch the object related to passed id
    obj = get_object_or_404(CalendarConfigurationCpordo, id = id)
    # delete object
    obj.soft_delete()
    messages.success(request,"CalendarConfigurationCpordo deleted successfully!")
    return redirect(f'../{str(obj.product_id)}/configCpordo')


# restore object (CalendarConfigurationCpordo) by id
def restore_conf_cpordo(request,division ,id):
    # fetch the object related to passed id
    obj = get_object_or_404(CalendarConfigurationCpordo, id = id)
    # restore object
    obj.restore()
    messages.success(request,"CalendarConfigurationCpordo restored successfully!")
    return redirect(f'../{str(obj.product_id)}/configCpordo')
    

# find all CalendarConfigurationCpordo for product 
def config_cpordo(request,division ,product):
    #get CalendarConfigurationCpordoForm
    form = CalendarConfigurationCpordoForm()
    # undeleted_objects object of soft delete manager
    data = CalendarConfigurationCpordo.objects.filter(product__pk = product ).order_by('id')    
    return render(request, "app/CalendarConfigurationCpordo/home_conf_cpordo.html", {'data':data,'division':division,'product':product,'form':form})

#********************** Home****************************

def home_page(request):
    
    return render(request,'app/home/index.html')

#*******************copy calendar************************************
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
        profit_center =Product.undeleted_objects.filter(id=product).values('Profit_center')
        # get cycle object with product_id and workdata_id 
        cycles = Cycle.undeleted_objects.all().filter(product_id = product_copied, workdata_id=data.id, owner = 'officiel') 
        # save cycle with new value of workdata_id 
        for cycle in cycles:
            custom_cycle= Cycle(work_day=cycle.work_day,division=cycle.division,profit_center=profit_center,smooth_family=cycle.smooth_family,cycle_time=cycle.cycle_time, workdata_id=work_data.id,product_id = product)
            custom_cycle.save()  
    return redirect("../calendar")

#********************************Save uploads************************************
#upload files
def upload_files(request):  

    return render(request,'app/files/file.html')  

#save coois   
def save_coois(request):
    conn = psycopg2.connect(host='localhost',dbname='mps_database',user='postgres',password='admin',port='5432')
    try:
        #Delete coois data 
        coois_data = Coois.undeleted_objects.all().filter(created_by='Marwa')
        coois_data.delete()
        #Save file to DB
        if request.method == 'POST' and request.FILES['coois']:
            file=request.FILES['coois']
            import_coois(file,conn)
            messages.success(request,"COOIS file uploaded successfully!") 
    except Exception:
        messages.error(request,"unable to upload files,not exist or unreadable") 
        print('unable to upload files,not exist or unreadable')
    return redirect("./upload")    
        
#save zpp   
def save_zpp(request):
    conn = psycopg2.connect(host='localhost',dbname='mps_database',user='postgres',password='admin',port='5432')
    #Delete zpp data 
    zpp_data = Zpp.undeleted_objects.all().filter(created_by='Marwa')
    zpp_data.delete()
    
    #Save file to DB
    try:
        if request.method == 'POST' and request.FILES['zpp']:
            file=request.FILES['zpp']
            import_zpp(file,conn)
            messages.success(request,"ZPP file uploaded successfully!") 
         
    except Exception:
        messages.error(request,"unable to upload ZPP files,not exist or unreadable") 
        print('unable to upload files,not exist or unreadable')
    return redirect("./upload")     
    
    
#********************************Upload COOIS************************************

def import_coois(file,conn):
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
    
    # Using the StringIO method to set
    # as file object
    print(dc.head(10))
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
                
            ],

            null="",
            sep=",",

        )
    conn.commit()

#********************************Upload ZPP_MD_STOCK************************************

def import_zpp(file,conn):
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
                    
            ],

            null="",
            sep=";",
            

        )
    conn.commit()

#**********************Shopfloor*****************************************

# @allowed_users(allowed_roles=["Planificateur"])
def shopfloor(request):
    
    #Get Data from DB
    # to use in shopfloor
    zpp_data=Zpp.objects.filter(created_by= 'Marwa').values('material','data_element_planif','created_by','message','date_reordo')
    coois_data= Coois.objects.all().filter(created_by= 'Marwa').values()
    material_data=Material.undeleted_objects.values('material','product__program','product__division__name','created_by','workstation','AllocatedTime','Leadtime','Allocated_Time_On_Workstation','Smooth_Family')
    # to use in smoothing calcul
    # product_work_data=Product.objects.values('planning','workdata__date','cycle__cycle_time')

    # cycle_infos_data=Cycle.objects.values('profit_center','cycle_time','work_day')

    # print('****************')
    # print(cycle_infos_data)
    # print(cycle_infos_data.count())
    # print( product_work_data)
    # print(product_work_data.count())
    # print('****************')
    # product_work_data=Product.objects.values('planning','workdata__date')
    
    #Convert to DataFrame
    df_zpp=pd.DataFrame(list(zpp_data))
    df_coois=pd.DataFrame(list(coois_data))
    df_material=pd.DataFrame(list(material_data))
    # ,df_cycle_infos_data=pd.DataFrame(list(cycle_infos_data))
    # rename df_material column 
    df_material=df_material.rename(columns={'product__program':'program','product__division__name':'division'})
    # rename  df_product_work_data column
    # df_cycle_infos_data=df_cycle_infos_data.rename(columns={'workdata__date':'workdate','cycle__cycle_time':'cycle_time'})
    
    

    #add column key for zpp (concatinate  material and data_element_planif and created_by  )
    df_zpp['key']=df_zpp['material'].astype(str)+df_zpp['data_element_planif'].astype(str)+df_zpp['created_by'].astype(str) 
    #add column key for coois (concatinate material, order, created_by )    
    df_coois['key']=df_coois['material'].astype(str)+df_coois['order'].astype(str)+df_coois['created_by'].astype(str)

    #add column key for material (concatinate material, created_by )  
    df_material['key']=df_material['material'].astype(str)+df_material['division'].astype(str)+df_material['created_by'].astype(str) 
    #add column key for coois (concatinate material,division,profit_centre, created_by )    
    df_coois['key2']=df_coois['material'].astype(str)+df_coois['division'].astype(str)+df_coois['created_by'].astype(str)
    
    # add column key for material_work_data (concatinate material, workdate ) 
    # df_cycle_infos_data['key']= df_cycle_infos_data['profit_center'].astype(str)+df_cycle_infos_data['work_day'].astype(str)
    # print('////////////////////////')
    # print(df_cycle_infos_data['key'])
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
    # 1: for Ranking 
    df_coois['Ranking']=np.where((df_coois['date_reordo'].isna()),(pd.to_datetime(df_coois['date_end_plan'])),(pd.to_datetime(df_coois['date_reordo'])))
    # 2: for closed  :
    df_coois['closed']=np.where(df_coois['order_stat'].str.contains('TCLO|LIVR'),True,False)
    records=df_coois.sort_values(['Smooth_Family','Ranking']) 
    
    return render(request,'app/Shopfloor/Shopfloor.html',{'records': records} ) 


#******************************smooth end date*****************************************************
#calcul smooth end date(Recursive Function)
# def smooth_date_calcul(current_date,table,designation,prev_cycle=None,prev_date=None):
#     #Get cycle for current day
#     key_date=str(designation)+str(current_date).split(' ')[0]
#     #initial case treatment (when prev_date =  current_date)
#     if prev_date is None:
#         prev_date=current_date
#     # Check and get cycle
#     try:
#         # key : contains the concatenation between designation and date of the table 
#         # value : c'est la valeur de cycle time de work data 
#         for key,value in table:
#             if key_date == key:
#                 cycle=value
#         print(cycle)
#     #when cycle not found  in table return date(1900,1,1)    
#     except Exception:
#         return date(1900,1,1)
#     #stop condition to avoid the infinite loop
#     if cycle==prev_cycle:
#         return current_date
#     new_date=pd.to_datetime(str(prev_date))+timedelta(hours=cycle)
#     print('new date',new_date)
#     return   smooth_date_calcul(new_date,table,designation,cycle,current_date)


 

#calcul smooth end date(Recursive Function)
def smooth_date_calcul(current_date,table,profit_center,Smooth_Family,prev_cycle=None,prev_date=None):
    #Get cycle for current day
    print("**************")
    print(current_date)
    print(type(current_date))

    # *******************************
    # current_date = datetime.fromisoformat(current_date).astimezone(timezone.utc)
    # current_date.strftime('%Y-%m-%d %H:%M:%S')
    # print("current_date:",current_date)

    # *******************************
    key_date=str(profit_center)+str(Smooth_Family)+str(current_date).split(' ')[0]
    #initial case treatment (when prev_date =  current_date)
    if prev_date is None:
        prev_date=current_date
    # Check and get cycle
    try:
        # key : contains the concatenation between profit_center and smooth family and date of the table 
        # value :cycle time
        for key,value in table:
            if key_date == key:
                cycle=value
        print(cycle)        
    #when cycle not found  in table return date(1900,1,1)    
    except Exception:
        return date(1900,1,1)   
    #stop condition to avoid the infinite loop
    if cycle==prev_cycle:
        return current_date
    
    # ***************************************

    # get start time for current date
    start_time = WorkData.undeleted_objects.filter(date=current_date).values_list('startTime',flat=True).first()
    # get end time for current date
    end_time = WorkData.undeleted_objects.filter(date=current_date).values_list('endTime',flat=True).first()
        
    # dictionary of business_hours
    business_hours = {
    # monday = 0, tuesday = 1, ... same pattern as date.weekday()
    # "weekdays": [0, 1, 2, 3, 4],
    "from": start_time, # startTime
    "to": end_time,  # endTime
    }

    # get Holidays 
    #get product id using profit center
    holidays = HolidaysCalendar.undeleted_objects.values_list('holidaysDate',flat=True) # flat=True this will mean the returned results are single values, rather than one-tuples

    # function is_in_open_hours
    def is_in_open_hours(dt):
        # return dt.weekday() in business_hours["weekdays"] \
        #    and dt.date() not in holidays \
        #    and business_hours["from"].hour <= dt.time().hour < business_hours["to"].hour
            return  dt.date() not in holidays \
            and business_hours["from"].hour <= dt.time().hour < business_hours["to"].hour

    # function get_next_open_datetime 
    def get_next_open_datetime(dt):
        while True:
            # dt = dt + timedelta(days=1)
            # if dt.weekday() in business_hours["weekdays"] and dt.date() not in holidays:
            #     dt = datetime.combine(dt.date(), business_hours["from"])
            #     return dt
            # print('get next day')
            # print('--------------',dt.date())
            # print('get next day')
            # print('--------------',holidays)
            dt = dt + timedelta(days=1)
            # check if open date
            if dt.date() not in holidays:
                dt = datetime.combine(dt.date(), business_hours["from"])
                # print('--------------',dt)
                return dt  
    # function add hours
    def add_hours(dt, hours):
        while hours != 0:
            print('dt:',dt)
            print('hours:',hours)
            print(type(hours))
            if hours < 0:
                return dt+timedelta(hours=hours)
            # check if open hour for open date
            if is_in_open_hours(dt):
                dt = dt + timedelta(hours=1)
                hours = hours - 1
            else:
                dt = get_next_open_datetime(dt)
                # print('****************dt',dt)
        return dt

    # ***************************************

    # print(cycle)
    # new_date=pd.to_datetime(str(prev_date))+timedelta(hours=cycle)
    new_date=add_hours(prev_date, cycle)
    return   smooth_date_calcul(new_date,table,profit_center,Smooth_Family,cycle,current_date)

#******************************create_shopfloor*****************************************************
#create shopfloor
def create_shopfloor(request):
    if request.method=='POST':
        # get inputs values
        id = request.POST.getlist('index')
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
        df=pd.DataFrame(data)
        # convert freeze_end_date to datetime 
        df['Freeze_end_date'] = pd.to_datetime(df['Freeze_end_date'])
        # delete old objects of shopfloor and save new objects
        Shopfloor.objects.all().delete()

        # #Check if at least the first end date is present for each Smooth Family
        df_for_check = df[df['closed'].str.contains('False')].groupby(["Smooth_Family"], as_index=False)["Freeze_end_date"].first()
        # print(df_for_check)
        # df_for_check = df[df['closed']==False]
        # print('----------------------')
        # print(df_for_check)
        # test line by line to return the index of smooth family is not filled
        for i in range(len(df_for_check)):
            if (df_for_check.loc[i,'Freeze_end_date']==''):
                messages.error(request,'Please fill at least the first Freeze end date, for the Smooth Family: '+df_for_check.loc[i,'Smooth_Family'])
                return redirect("shopfloor")
        #result
        df=smoothing_calculate(df)
        # df.to_csv('smoothing.csv')
        # delete column from df
        del df['key']
        del df['freezed']
        del df['key_start_day']
        # delete index from df
        df=df.reset_index(drop=True)
        #Save data
        save_shopfloor(df)

        messages.success(request,"Data saved successfully!") 
        return redirect(result)
        # return render(request,'app/Shopfloor/result.html')
    
    
#******************************save_shopfloor*****************************************************    

def save_shopfloor(df):
    conn = psycopg2.connect(host='localhost',dbname='mps_database',user='postgres',password='admin',port='5432')
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

    # Using the StringIO method to set
    # as file object
    shopfloor = StringIO()

    # df.to_csv('dfSaveShopfloor.csv',index=False)

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
                    ],

            null="",
            sep=";",
        )
    conn.commit()
    
#******************************result ***********************************************************       
# @allowed_users(allowed_roles=["Planificateur"])        
# def result(request):
#     #Get Work date data
#     product_work_data=Product.undeleted_objects.values('planning','workdata__date','workdata__cycle_time')
#     df_product_work_data=pd.DataFrame(list(product_work_data))
#     df_product_work_data=df_product_work_data.rename(columns={'workdata__date':'workdate','workdata__cycle_time':'cycle_time'})
#     df_product_work_data['key']= df_product_work_data['planning'].astype(str)+df_product_work_data['workdate'].astype(str)
#     # df_product_work_data_dict_date=dict(zip(df_product_work_data.key, df_product_work_data.workdate))
#     df_product_work_data_dict_cycle=dict(zip(df_product_work_data.key, df_product_work_data.cycle_time))
#     #Get Shopfloor from DB
#     data=Shopfloor.objects.all().values()
#     df_data=pd.DataFrame(list(data))
#     df_data=df_data.sort_values('Ranking') #To add designation as sort
#     #Add col freezed to know how row is freezed
#     df_data['freezed']=np.where((df_data['Freeze_end_date'].notna()),'Freezed','not_freezed')

#     df_data['key']=df_data['designation'].astype(str)+pd.to_datetime(df_data['Freeze_end_date']).astype(str)
#     # df_data['Freeze_end_date']=pd.to_datetime(df_data['Freeze_end_date'])
#     # df_data['cycle']=df_data['key'].map(df_product_work_data_dict_cycle)
#     # df_data.insert(0,'freezed_start_date',None)
#     # df_data['freezed_start_date']=np.where((df_data['freezed']=='Freezed'),df_data['Freeze_end_date'],df_data['freezed_start_date'])
#     # df_data['freezed_start_date']=pd.to_datetime(df_data['freezed_start_date'])
#     # df_data['freezed_start_date']=df_data['Freeze_end_date']

#     df_data[['Freeze_end_date']] = df_data[['Freeze_end_date']].astype(object).where(df_data[['Freeze_end_date']].notnull(), None)
#     df_data['smoothing_end_date']=df_data['Freeze_end_date']
#     df_data.insert(0,'key_start_day','')
#     for i in range(len(df_data)-1):
#         if (df_data.loc[i+1,'freezed']=='not_freezed'):
#             df_data.loc[i+1,'smoothing_end_date'] = smooth_date_calcul(df_data.loc[i,'smoothing_end_date'],df_product_work_data_dict_cycle.items(),df_data.loc[i,'designation'])            
#     # print(df_data.loc[i+1,'smoothing_end_date'])
#     df_data=df_data.sort_values('id')
#     return render(request,'app/Shopfloor/result.html',{'records':df_data}) 



# @allowed_users(allowed_roles=["Planificateur"])        
def smoothing_calculate(df_data):
    #Get Work date data
    cycle_data=Cycle.undeleted_objects.values('profit_center','smooth_family','cycle_time','work_day') 
    #Convert to DataFrame
    df_cycle_data=pd.DataFrame(list(cycle_data))
    # concatinate profit_center and smooth_family and work_day
    df_cycle_data['key']= df_cycle_data['profit_center'].astype(str)+df_cycle_data['smooth_family'].astype(str)+df_cycle_data['work_day'].astype(str)
    # df_product_work_data_dict_date=dict(zip(df_product_work_data.key, df_product_work_data.workdate))
    df_dict_cycle=dict(zip(df_cycle_data.key, df_cycle_data.cycle_time))
    #Get Shopfloor from DB
    # data=Shopfloor.objects.all().values()
    # df_data=pd.DataFrame(list(data))
    df_data=df_data.sort_values('Ranking') #To add designation as sort
    #Add col freezed to know how row is freezed
    # df_data['freezed']=np.where((df_data['Freeze_end_date'].notna()),'Freezed','not_freezed')
    df_data['freezed']=np.where((df_data['Freeze_end_date'].notna()),'Freezed','not_freezed')
    df_data['key']=df_data['profit_centre'].astype(str)+df_data['Smooth_Family'].astype(str)+pd.to_datetime(df_data['Freeze_end_date']).astype(str)

    df_data[['Freeze_end_date']] = df_data[['Freeze_end_date']].astype(object).where(df_data[['Freeze_end_date']].notnull(), None)
    df_data['smoothing_end_date']=df_data['Freeze_end_date']
    
    
    
    # df_data.to_csv('freeze.csv')
    df_data.insert(0,'key_start_day','')
    for i in range(len(df_data)-1):
        # test if not freezed and not closed calcul smoothing
        # if (df_data.loc[i+1,'freezed']=='not_freezed') and (df_data.loc[i+1,'closed']=='False'):
        if (df_data.loc[i+1,'freezed']=='not_freezed') and (df_data.loc[i+1,'closed']== 'False'):
            print("marwa")
            df_data.loc[i+1,'smoothing_end_date'] = smooth_date_calcul(df_data.loc[i,'smoothing_end_date'],df_dict_cycle.items(),df_data.loc[i,'profit_centre'],df_data.loc[i,'Smooth_Family'])            
    # print(df_data.loc[i+1,'smoothing_end_date'])
    # df_data=df_data.sort_values('id')
    # print(df_data)
    # df_data.to_csv('result.csv')
    # delete old objects of shopfloor and save new objects
    # Shopfloor.objects.all().delete()

    # df_data.drop(['key'])
    # df_data.drop(['freezed'])
    # df_data.to_csv('df.csv',index=False)
    return df_data
    # return render(request,'app/Shopfloor/result.html',{'records':df_data}) 


# def result
def result(request):
    data=Shopfloor.objects.all().values().order_by('Smooth_Family','Ranking')
    # print("'***********'")
    # print(data)
    # df_data=pd.DataFrame(list(data))
    # df_data.to_csv('result.csv')
    return render(request,'app/Shopfloor/result.html',{'records':data}) 

#******************************Planning*****************************************************    
#calcul KPIs
def planning(request):
    #Get data
    data=Shopfloor.objects.all()
    #Convert to DF
    df_data=pd.DataFrame(data.values())
    # Program demand count per week
    #Get week from date_end_plan if date_reordo is null or Get week from date_reordo
    df_data['week_programm_demand']=np.where((df_data['date_reordo'].isna()),(pd.to_datetime(df_data['date_end_plan']).dt.week),(pd.to_datetime(df_data['date_reordo']).dt.week)).astype(int)
    df_data['year_programm_demand']=np.where((df_data['date_reordo'].isna()),(pd.to_datetime(df_data['date_end_plan']).dt.year),(pd.to_datetime(df_data['date_reordo']).dt.year)).astype(int)
    df_data['year_week_programm_demand']=df_data['year_programm_demand'].astype(str)+'_'+df_data['week_programm_demand'].astype(str)
    #Program demand count per week
    week_count=df_data.groupby('year_week_programm_demand')['id'].count().reset_index()
    print('************************************')
    print(df_data['week_programm_demand'])
    print(df_data['year_programm_demand'])
    print(df_data['year_week_programm_demand'])

    #Demonstrated_capacity count per week
    df_status=df_data[df_data['order_stat'].str.contains('TCLO|LIVR')]
    df_status['year_week_end_date']=(pd.to_datetime(df_data['date_end_plan']).dt.year).astype(str)+'_'+(pd.to_datetime(df_data['date_end_plan']).dt.week).astype(str)
    week_demonstrated_capacity_count=df_status.groupby('year_week_end_date')['id'].count().reset_index()
    
    # Production Plan count per week
    # Get week from smoothing end date if freeze end date is null or Get week from freeze end date
    df_data['week_production_plan']=np.where((df_data['Freeze_end_date'].isna()),(pd.to_datetime(df_data['smoothing_end_date']).dt.week),(pd.to_datetime(df_data['Freeze_end_date']).dt.week)).astype(int)
    # df_data['week_production_plan']=np.where((df_data['Freeze_end_date'].isna()),df_data['smoothing_end_date'],False)
    df_data['year_production_plan']=np.where((df_data['Freeze_end_date'].isna()),(pd.to_datetime(df_data['smoothing_end_date']).dt.year),(pd.to_datetime(df_data['Freeze_end_date']).dt.year)).astype(int)
    df_data['year_week_production_plan']=df_data['year_production_plan'].astype(str)+'_'+df_data['week_production_plan'].astype(str)
    week_production_plan_count=df_data.groupby('year_week_production_plan')['id'].count().reset_index()
    # df_data.to_csv('df.csv')

    #Stock count per week
    
    return render(request,'app/planning.html',{'records':df_data,'week_count':week_count,'week_demonstrated_capacity_count':week_demonstrated_capacity_count,'week_production_plan_count':week_production_plan_count})


#Test for web excel jquery
def data_table(request):
    return render(request,'app/Shopfloor/datatable.html') 

#***********************************************************************************    
