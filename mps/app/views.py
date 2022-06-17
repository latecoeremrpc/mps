from django.shortcuts import render ,redirect ,get_object_or_404
from app.models import Division,Material,HolidaysCalendar,Product,WorkData,CalendarConfigurationTreatement,CalendarConfigurationCpordo,Coois,Zpp,Shopfloor
from app.forms import DivisionForm,MaterialForm,ProductForm,CalendarConfigurationCpordoForm,CalendarConfigurationTreatementForm 
from datetime import  datetime, timedelta
from io import StringIO
import psycopg2, pandas as pd
import numpy as np
from django.contrib import messages


# Create your views here.
#Comment Houssem
#Comment Marwa
#*********************CRUD Division************************

# add new object(Division)
def create_division(request):
    form = DivisionForm(request.POST)
    if request.method == "POST" :
        if form.is_valid():
            messages.success(request,"Division created successfully!")
            form.save()
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
            messages.success(request,"Division updated successfully!")
            form.save()
        else:
            messages.error(request,"try again!")
                
    return redirect("./")


# delete object(Division) by id
def delete_division(request, id):
    # fetch the object related to passed id
    obj = get_object_or_404(Division, id = id)
    #alert message
    messages.success(request,"Division deleted successfully!")
    # delete object
    obj.soft_delete()
    return redirect("../")
    

# restore object(Division) by id
def restore_division(request, id):
    # fetch the object related to passed id
    obj = get_object_or_404(Division, id = id)
    #alert message
    messages.success(request,"Division restored successfully!")
    # restore object
    obj.restore() 
    return redirect("../")
    

#*********************CRUD Material************************

# add new object(Material)
def create_material(request,division,product):
    form = MaterialForm(request.POST)
    if request.method == "POST":
        if form.is_valid():
            instance=form.save(commit=False)
            instance.product_id=product
            messages.success(request," Material created successfully!")
            instance.save()
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
            messages.success(request,"Material updated successfully!")
            form.save()
        else:
            messages.error(request,"try again!")    
    return redirect(f'./{str(obj.product_id)}/material/')
    

# delete object (Material) by id
def delete_material(request, division ,id):
    # fetch the object related to passed id
    obj = get_object_or_404(Material, id = id)
    #alert message
    messages.success(request,"Material deleted successfully!")
    # delete object
    obj.soft_delete()
    return redirect(f'../{str(obj.product_id)}/material/')
   

# restore object(Material) by id
def restore_material(request, division ,id):
    # fetch the object related to passed id
    obj = get_object_or_404(Material, id = id)
    #alert message
    messages.success(request,"Material restored successfully!")
    # restore object
    obj.restore()
    return redirect(f'../{str(obj.product_id)}/material/')    


# find all Material for product 
def material(request ,division, product):
    #get MaterialForm
    form = MaterialForm()
    # undeleted_objects object of soft delete manager
    data = Material.objects.filter(product__pk = product ).order_by('id')    
    return render(request, "app/material/material.html", {'data':data,'division':division,'product':product,'form':form})


#********************Create Holidays calendar****************************
def calendar(request,division,product):
    # get all work data objects to display in Calendar(for copy calendar)
    products_data= Product.undeleted_objects.all()
    # get all work data objects to display in Calendar
    work = WorkData.undeleted_objects.all().filter(product_id = product, owner = 'officiel') 
    # get all holiday objects to display in Calendar
    holidays = HolidaysCalendar.undeleted_objects.all().filter(product_id = product, owner = 'officiel' ) 
    return render(request, "app/calendar/calendar.html",{'product':product,'division':division,'holidays':holidays,'work':work,'products_data':products_data})


# create calendar for product 
def create_calendar(request,division,product):
    #get list of days from work data 
    #workDays = list(WorkData.objects.values_list('date',flat=True))
    #print(workDays)
    # get list of days from dataBase to compare if exist 
    days = list(HolidaysCalendar.objects.values_list('holidaysDate',flat=True))
    print(days)
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
                    exist_day =HolidaysCalendar.undeleted_objects.all().filter(holidaysDate = startDate) 
                    exist_day.delete()
                    data = HolidaysCalendar(name=name,holidaysDate=startDate,product_id =product)
                    data.save()
                else:
                    exist_on_days = WorkData.undeleted_objects.all().filter(date = startDate) 
                    exist_on_days.delete()
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
                        exist_day =HolidaysCalendar.undeleted_objects.all().filter(holidaysDate = day) 
                        exist_day.delete()
                        data = HolidaysCalendar(name=name,holidaysDate=day,product_id =product)
                        data.save()
                    else :
                        exist_on_days = WorkData.undeleted_objects.all().filter(date = day) 
                        exist_on_days.delete()
                        data = HolidaysCalendar(name=name,holidaysDate=day,product_id =product)
                        data.save()
    return redirect("../calendar")


# delete day (holiday or work)
def delete_day(request,division,product): 
    #holidays = HolidaysCalendar.undeleted_objects.all().filter(product_id = product)
    if request.method =="POST"  and 'delete' in request.POST:
        # get id value from form
        id = request.POST.get('date_id')
        date_type = request.POST.get('date_type')
        model = WorkData if date_type=='Work Day' else HolidaysCalendar
        obj = get_object_or_404(model, id = id)
        # delete object
        obj.soft_delete()
        # redirect to calendar 
    return redirect("../calendar")
    #return render(request,"app/calendar/calendar.html",{'product':product} )
    
#********************Custom calendar****************************

#duplicate calendar
def duplicate_calendar(request,division,product):
    #Delete custom holidays
    custom_holidays = HolidaysCalendar.undeleted_objects.all().filter(product_id = product,owner = 'marwa')
    custom_holidays.delete()
    #Delete custom work
    work = WorkData.undeleted_objects.all().filter(product_id = product,owner = 'marwa')
    work.delete()
    #save data for loop holidays
    holidays = HolidaysCalendar.undeleted_objects.all().filter(product_id = product)
    for data in holidays:
        custom_holidays = HolidaysCalendar(name=data.name,holidaysDate=data.holidaysDate,product_id =data.product_id,owner = 'marwa')
        custom_holidays.save()
    #save data for loop work
    work = WorkData.undeleted_objects.all().filter(product_id = product)
    for data in work:
        custom_work_data = WorkData(date=data.date,startTime=data.startTime,endTime=data.endTime,FTEhourByDay=data.FTEhourByDay,ExtraHour=data.ExtraHour,Absenteeism_ratio=data.Absenteeism_ratio,Unproductiveness_ratio=data.Unproductiveness_ratio,Efficienty_ratio=data.Efficienty_ratio,cycle_time=data.cycle_time,product_id =data.product_id,owner = 'marwa')
        custom_work_data.save()  
    #custom_holidays = HolidayCalendar.undeleted_objects.all().filter(product_id = product,owner = 'marwa')
    #call function create new holiday object
    custom_calendar(request,division,product)
    #call function create new work data object 
    custom_work(request,division,product)
    return redirect("../customcalendar")
    #return render(request,"app/calendar/custom_calendar.html", {'product':product,'holidays':custom_holidays})



def custom_calendar(request,division,product):
    # get all holiday objects to display in Calendar
    holidays = HolidaysCalendar.undeleted_objects.all().filter(product_id = product ,owner = 'marwa') 
    # get all work data objects to display in Calendar    
    work = WorkData.undeleted_objects.all().filter(product_id = product ,owner = 'marwa')
    return render(request,"app/calendar/custom_calendar.html",{'product':product,'division':division,'holidays':holidays,'work':work})
    

#custom calendar
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
                    exist_day =HolidaysCalendar.undeleted_objects.all().filter(holidaysDate = startDate, owner = 'marwa') 
                    exist_day.delete()
                    data = HolidaysCalendar(name=name,holidaysDate=startDate,product_id =product, owner = owner)
                    data.save()
                else:
                    exist_on_days = WorkData.undeleted_objects.all().filter(date = startDate, owner = 'marwa') 
                    exist_on_days.delete()
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
                        exist_day =HolidaysCalendar.undeleted_objects.all().filter(holidaysDate = day, owner = 'marwa') 
                        exist_day.delete()
                        data = HolidaysCalendar(name=name,holidaysDate=day,product_id =product, owner = owner)
                        data.save()   
                    else :
                        exist_on_days = WorkData.undeleted_objects.all().filter(date = day, owner = 'marwa') 
                        exist_on_days.delete()
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
         messages.success(request," Product created successfully!")
         instance.save()
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
            messages.success(request," Product updated successfully!")  
            form.save()
        else:
            messages.error(request," try again!")        
    return redirect(f'./{str(obj.division_id)}/product/')
    


# delete object(Product) by id
def delete_product(request, id):
    # fetch the object related to passed id
    obj = get_object_or_404(Product, id = id)
    messages.success(request," Product deleted successfully!")  
    # delete object
    obj.soft_delete()
    return redirect(f'../{str(obj.division_id)}/product/')
    


# restore object(Product) by id
def restore_product(request, id):
    # fetch the object related to passed id
    obj = get_object_or_404(Product, id = id)
    messages.success(request," Product restored successfully!")  
    # restore object
    obj.restore()
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

    if request.method=='POST' and 'save-work' in request.POST:
        # get inputs from form
        id = request.POST.get('event-index')
        startTime = request.POST.get('start-time')
        endTime = request.POST.get('end-time')
        fte = request.POST.get('fte')
        extraHours = request.POST.get('extra-hours')
        AbsenteeismRatio = request.POST.get('Absenteeism-ratio')
        UnproductivenessRatio = request.POST.get('Unproductiveness-ratio')
        EfficientyRatio = request.POST.get('Efficienty-ratio')
        cycle_time = request.POST.get('cycle-time')
        time = request.POST.get('cycle')
        startDate = request.POST.get('event-start-date')
        endDate = request.POST.get('event-end-date')
        print('*************')
        print(time)
        print(cycle_time)
        if time == 'Days':
            cycle_time = 24 * float(cycle_time)
            print(cycle_time)
        

        # If id exist Update Object if not create new one
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
                return redirect("../calendar")
        # create new object         
        else :
            # add one day in database
            if startDate == endDate:
                startDate= datetime.strptime(startDate,'%m/%d/%Y')
                endDate= datetime.strptime(endDate,'%m/%d/%Y')
                # check if day and product_id exists in DB don't save else save
                if (startDate.strftime('%Y-%m-%d') in [day.strftime('%Y-%m-%d') for day in days] ) and (int(product) in products):
                    exist_day =WorkData.undeleted_objects.all().filter(date = startDate) 
                    exist_day.delete()
                    data = WorkData(date=startDate,startTime=startTime,endTime=endTime,FTEhourByDay=fte,ExtraHour=extraHours,Absenteeism_ratio=AbsenteeismRatio,Unproductiveness_ratio=UnproductivenessRatio, Efficienty_ratio=EfficientyRatio,cycle_time=cycle_time,product_id =product)
                    data.save()
                    return redirect("../calendar")
                else:
                    exist_off_days = HolidaysCalendar.undeleted_objects.all().filter(holidaysDate= startDate) 
                    exist_off_days.delete()
                    data = WorkData(date=startDate,startTime=startTime,endTime=endTime,FTEhourByDay=fte,ExtraHour=extraHours,Absenteeism_ratio=AbsenteeismRatio,Unproductiveness_ratio=UnproductivenessRatio, Efficienty_ratio=EfficientyRatio,cycle_time=cycle_time,product_id =product)
                    data.save()
                    return redirect("../calendar")
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
                        exist_days = WorkData.undeleted_objects.all().filter(date = day) 
                        exist_days.delete()
                        data = WorkData(date=day,startTime=startTime,endTime=endTime,FTEhourByDay=fte,ExtraHour=extraHours,Absenteeism_ratio=AbsenteeismRatio,Unproductiveness_ratio=UnproductivenessRatio, Efficienty_ratio=EfficientyRatio,cycle_time=cycle_time,product_id =product)
                        data.save()     
                    else :
                        #replace holidays with work data
                        #get holidays 
                        exist_off_days = HolidaysCalendar.undeleted_objects.all().filter(holidaysDate = day) 
                        #delete exist_off_days
                        exist_off_days.delete()
                        #save work data
                        data = WorkData(date=day,startTime=startTime,endTime=endTime,FTEhourByDay=fte,ExtraHour=extraHours,Absenteeism_ratio=AbsenteeismRatio,Unproductiveness_ratio=UnproductivenessRatio, Efficienty_ratio=EfficientyRatio,cycle_time=cycle_time,product_id =product)
                        data.save()
                return redirect("../calendar")       
        
    return render(request,"app/calendar/calendar.html",{'product':product,'division':division, 'work':work})
      

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
        id = request.POST.get('event-index')
        owner = request.POST.get('owner')
        startTime = request.POST.get('start-time')
        endTime = request.POST.get('end-time')
        fte = request.POST.get('fte')
        extraHours = request.POST.get('extra-hours')
        AbsenteeismRatio = request.POST.get('Absenteeism-ratio')
        UnproductivenessRatio = request.POST.get('Unproductiveness-ratio')
        EfficientyRatio = request.POST.get('Efficienty-ratio')
        cycle_time = request.POST.get('cycle-time')
        time = request.POST.get('cycle')
        startDate = request.POST.get('event-start-date')
        endDate = request.POST.get('event-end-date')
        print('*************')
        print(time)
        print(cycle_time)
        if time == 'Days':
            cycle_time = 24 * float(cycle_time)
            print(cycle_time)
        # If id exist Update Object if not create new one
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
                
                #To complete all filed
                work_day.save()
                return redirect("../customcalendar")
        # create new object         
        else : 
            # add one day in database
            if startDate == endDate:
                startDate= datetime.strptime(startDate,'%m/%d/%Y')
                endDate= datetime.strptime(endDate,'%m/%d/%Y')
                    # check if day and product_id exists in DB don't save else save
                if (startDate.strftime('%Y-%m-%d') in [day.strftime('%Y-%m-%d') for day in days] ) and (int(product) in products):
                    exist_day =WorkData.undeleted_objects.all().filter(date = startDate, owner = 'marwa') 
                    exist_day.delete()
                    data = WorkData(date=startDate,startTime=startTime,endTime=endTime,FTEhourByDay=fte,ExtraHour=extraHours,Absenteeism_ratio=AbsenteeismRatio,Unproductiveness_ratio=UnproductivenessRatio, Efficienty_ratio=EfficientyRatio,cycle_time=cycle_time,product_id =product,owner = owner)
                    data.save()
                    return redirect("../customcalendar")
                else:
                    #replace holiday with workdata
                    exist_off_days = HolidaysCalendar.undeleted_objects.all().filter(holidaysDate= startDate, owner = 'marwa') 
                    #delete holidays
                    exist_off_days.delete()
                    #save data work object
                    data = WorkData(date=startDate,startTime=startTime,endTime=endTime,FTEhourByDay=fte,ExtraHour=extraHours,Absenteeism_ratio=AbsenteeismRatio,Unproductiveness_ratio=UnproductivenessRatio, Efficienty_ratio=EfficientyRatio,cycle_time=cycle_time,product_id =product,owner = owner)
                    data.save()
                    return redirect("../customcalendar")
            # add list of days in database       
            else: 
                startDate=datetime.strptime(startDate,'%m/%d/%Y')
                endDate=datetime.strptime(endDate,'%m/%d/%Y')
                print(startDate)
                print(endDate)
                delta= endDate-startDate
                day=""
                for i in range(delta.days+1):
                    day= startDate + timedelta(days=i)
                    # check if day and product_id exists in DB don't save else save
                    if (day.strftime('%Y-%m-%d') in [day.strftime('%Y-%m-%d') for day in days]) and (int(product) in products):
                        exist_days = WorkData.undeleted_objects.all().filter(date = day, owner = 'marwa') 
                        exist_days.delete()
                        data = WorkData(date=day,startTime=startTime,endTime=endTime,FTEhourByDay=fte,ExtraHour=extraHours,Absenteeism_ratio=AbsenteeismRatio,Unproductiveness_ratio=UnproductivenessRatio, Efficienty_ratio=EfficientyRatio,cycle_time=cycle_time,product_id =product,owner = owner)
                        data.save()
                    else :
                        #replace holidays with work data
                        #get holidays 
                        exist_off_days = HolidaysCalendar.undeleted_objects.all().filter(holidaysDate = day, owner = 'marwa') 
                        #delete exist_off_days
                        exist_off_days.delete()
                        #save work data
                        data = WorkData(date=day,startTime=startTime,endTime=endTime,FTEhourByDay=fte,ExtraHour=extraHours,Absenteeism_ratio=AbsenteeismRatio,Unproductiveness_ratio=UnproductivenessRatio, Efficienty_ratio=EfficientyRatio,cycle_time=cycle_time,product_id =product,owner = owner)
                        data.save()
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
        messages.success(request,"CalendarConfigurationTraitement created successfully!")
        instance.save()
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
            messages.success(request,"CalendarConfigurationTraitement updated successfully!")   
            form.save()
        else:
          messages.error(request,"try again !")           
    return redirect(f'./{str(obj.product_id)}/configTrait')
    

# delete object (CalendarConfigurationTraitement) by id
def delete_conf_trait(request, division ,id):
    # fetch the object related to passed id
    obj = get_object_or_404(CalendarConfigurationTreatement, id = id)
    messages.success(request,"CalendarConfigurationTraitement deleted successfully!")   
    # delete object
    obj.soft_delete()
    return redirect(f'../{str(obj.product_id)}/configTrait')
    


# restore object (CalendarConfigurationTraitement) by id
def restore_conf_trait(request, division ,id):
    # fetch the object related to passed id
    obj = get_object_or_404(CalendarConfigurationTreatement, id = id)
    messages.success(request,"CalendarConfigurationTraitement restored successfully!")   
    # restore object
    obj.restore()
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
            messages.success(request,"CalendarConfigurationCpordo created successfully!")
            instance.save()
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
            messages.success(request,"CalendarConfigurationCpordo updated successfully!")
            form.save()
        else:
            messages.error(request,"try again!")    
    return redirect(f'./{str(obj.product_id)}/configCpordo')
    

# delete object (CalendarConfigurationCpordo) by id
def delete_conf_cpordo(request,division ,id):
    # fetch the object related to passed id
    obj = get_object_or_404(CalendarConfigurationCpordo, id = id)
    messages.success(request,"CalendarConfigurationCpordo deleted successfully!")
    # delete object
    obj.soft_delete()
    return redirect(f'../{str(obj.product_id)}/configCpordo')


# restore object (CalendarConfigurationCpordo) by id
def restore_conf_cpordo(request,division ,id):
    # fetch the object related to passed id
    obj = get_object_or_404(CalendarConfigurationCpordo, id = id)
    messages.success(request,"CalendarConfigurationCpordo restored successfully!")
    # restore object
    obj.restore()
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
    holidays_data = HolidaysCalendar.undeleted_objects.all().filter(product_id = product)
    holidays_data.delete()
    #Delete work
    work_data = WorkData.undeleted_objects.all().filter(product_id = product)
    work_data.delete() 
    #get product copied id 
    product_copied= request.POST.get('product_copied')
    #get holiday object with product id
    holidays_data = HolidaysCalendar.undeleted_objects.all().filter(product_id = product_copied, owner = 'officiel')
    #save holiday object in DB
    for data in holidays_data:
        holidays = HolidaysCalendar(name=data.name,holidaysDate=data.holidaysDate,product_id = product)
        holidays.save()
    #get work data object with product id 
    work_data = WorkData.undeleted_objects.all().filter(product_id = product_copied ,owner = 'officiel')
    #save workdata object in DB
    for data in work_data:
        work_data = WorkData(date=data.date,startTime=data.startTime,endTime=data.endTime,FTEhourByDay=data.FTEhourByDay,ExtraHour=data.ExtraHour,Absenteeism_ratio=data.Absenteeism_ratio,Unproductiveness_ratio=data.Unproductiveness_ratio,Efficienty_ratio=data.Efficienty_ratio,cycle_time=data.cycle_time,product_id = product)
        work_data.save() 
    return redirect("../calendar")

#********************************Save uploads************************************
#upload files
def upload_files(request):  

    return render(request,'app/files/file.html')  

#save coois   
def save_coois(request):
    conn = psycopg2.connect(host='localhost',dbname='MPS',user='postgres',password='AdminMPS',port='5432')
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
    conn = psycopg2.connect(host='localhost',dbname='MPS',user='postgres',password='AdminMPS',port='5432')
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
        messages.error(request,"unable to upload files,not exist or unreadable") 
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
    print(dc)
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
    
    
    print(dc)
    # Using the StringIO method to set
    # as file object
    print(dc.head(10))
    zpp = StringIO()
    #convert file to csv
    zpp.write(dc.to_csv(index=None , header=None))
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
            sep=",",
            

        )
    conn.commit()

#**********************Shopfloor****************************

def shopfloor(request):
    
    #Get Data from DB
    zpp_data=Zpp.objects.filter(created_by= 'Marwa').values('material','data_element_planif','created_by','message','date_reordo')
    coois_data= Coois.objects.all().filter(created_by= 'Marwa').values()
    material_data=Material.objects.values('material','product__program','product__division__name','created_by','workstation','AllocatedTime','Leadtime','Allocated_Time_On_Workstation','Smooth_Family')
    product_work_data=Product.objects.values('planning','workdata__date','workdata__cycle_time')
    print(product_work_data)

    #Convert to DataFrame
    df_zpp=pd.DataFrame(list(zpp_data))
    df_coois=pd.DataFrame(list(coois_data))
    df_material=pd.DataFrame(list(material_data))
    df_material=df_material.rename(columns={'product__program':'program','product__division__name':'division'})
    df_product_work_data=pd.DataFrame(list(product_work_data))
    df_product_work_data=df_product_work_data.rename(columns={'workdata__date':'workdate','workdata__cycle_time':'cycle_time'})
    
    

    #add column key for zpp (concatinate  material and data_element_planif and created_by  )
    df_zpp['key']=df_zpp['material'].astype(str)+df_zpp['data_element_planif'].astype(str)+df_zpp['created_by'].astype(str) 
    #add column key for coois (concatinate material, order, created_by )    
    df_coois['key']=df_coois['material'].astype(str)+df_coois['order'].astype(str)+df_coois['created_by'].astype(str)
    
    
    #add column key for material (concatinate material, created_by )  
    df_material['key']=df_material['material'].astype(str)+df_material['division'].astype(str)+df_material['created_by'].astype(str) 
    #add column key for coois (concatinate material,division,profit_centre, created_by )    
    df_coois['key2']=df_coois['material'].astype(str)+df_coois['division'].astype(str)+df_coois['created_by'].astype(str)
    # add column key for material_work_data (concatinate material, workdate ) 
    df_product_work_data['key']= df_product_work_data['planning'].astype(str)+df_product_work_data['workdate'].astype(str)
 
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
    
    #convert df_product_work_data to dict
    df_product_work_data_dict_date=dict(zip(df_product_work_data.key, df_product_work_data.workdate))
    df_product_work_data_dict_cycle=dict(zip(df_product_work_data.key, df_product_work_data.cycle_time))
    
    
    
    records=df_coois
    #**************************************
    file=r'C:\Users\LENOVO\Documents\Mps_Files\df_shopfloor.xlsx'
    df_data=pd.read_excel(file)
    df_data=df_data.sort_values('Ranking')
    
    df_data['freezed']=np.where((df_data['Freeze_end_date'].notna()),'Freezed','not_freezed')
    #df_data['Freeze_end_date_prev']=df_data['Freeze_end_date'].ffill()
    df_data['key']=df_data['designation'].astype(str)+pd.to_datetime(df_data['Freeze_end_date']).astype(str)
    df_data['Freeze_end_date']=pd.to_datetime(df_data['Freeze_end_date'])
    #Merge
    df_data['cycle']=df_data['key'].map(df_product_work_data_dict_cycle)
    #insert in df_date freezed_start_date
    df_data.insert(0,'freezed_start_date',None)
    # df_data['freezed_start_date']=np.where((df_data['freezed']=='Freezed'),df_data['Freeze_end_date'],df_data['freezed_start_date'])
    df_data['freezed_start_date']=pd.to_datetime(df_data['freezed_start_date'])
    # df_data['freezed_start_date']=df_data['Freeze_end_date']
    df_data.insert(0,'key_start_day','')
    print('+++++++++++++++++++')
    print(df_data)
    
    
    for i in range(1, 15):
        print('*****************')
        print(i)
        print(df_data.loc[i, 'Freeze_end_date'])
    #     df_data.loc[i, 'freezed_start_date'] =np.where((df_data.loc[i,'freezed']=='not_freezed'),(pd.to_datetime(str(df_data.loc[i-1, 'Freeze_end_date'])) + timedelta(hours=int(df_data.loc[i-1, 'cycle']))),df_data.loc[i, 'freezed_start_date'])
    #     df_data.loc[i, 'key_start_day']=str(df_data.loc[i,'designation'])+str(df_data.loc[i,'freezed_start_date']).split(' ')[0]

    #     for key,value in df_product_work_data_dict_cycle.items():
    #         if df_data.loc[i,'key_start_day'] == key:
    #             df_data.loc[i,'cycle']=value
    #             if int(df_data.loc[i-1, 'cycle']) == int(df_data.loc[i, 'cycle']):
    #                 df_data.loc[i, 'freezed_start_date'] =np.where((df_data.loc[i,'freezed']=='not_freezed'),(pd.to_datetime(str(df_data.loc[i-1, 'Freeze_end_date']))),df_data.loc[i, 'freezed_start_date'])
    #             else:
    #                 df_data.loc[i, 'freezed_start_date'] =np.where((df_data.loc[i,'freezed']=='not_freezed'),(pd.to_datetime(str(df_data.loc[i-1, 'Freeze_end_date'])) + timedelta(hours=int(df_data.loc[i, 'cycle']))),df_data.loc[i, 'freezed_start_date'])


    # df_data.loc[i, 'Freeze_end_date']=np.where((df_data.loc[i,'freezed']=='not_freezed'),(df_data.loc[i, 'freezed_start_date'] + timedelta(hours=int(df_data.loc[i, 'cycle']))),df_data.loc[i, 'Freeze_end_date'])
    # # df_data.loc[i, 'Freeze_end_date']=np.datetime64(df_data.loc[i, 'Freeze_end_date'])
    # print(str(df_data.loc[i,'freezed_start_date']).split(' ')[0])
    
   
    
    #************************************************************
    
    return render(request,'app/Shopfloor/Shopfloor.html',{'records': records} )    

def data_table(request):
    return render(request,'app/Shopfloor/datatable.html')    
     

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
        Freeze_end_date = request.POST.getlist('Freeze end date')
        Remain_to_do = request.POST.getlist('Remain to do')
        print('*************',len(Freeze_end_date[0]))
        # if  len(Freeze_end_date[0]) > 0:
        data=Shopfloor.objects.all().delete()
        
        if  Freeze_end_date[0]!= '':     
            
              #save all informations from table 
            for i in range(len(id)):
                if date_start_plan[i] != '':
                    #convert date_start_plan to datetime 
                    date_start_plan [i]= datetime.strptime( date_start_plan[i],'%d/%m/%Y')
                else:
                    date_start_plan [i]=None
                if date_end_plan[i] != '' :
                    date_end_plan [i]=datetime.strptime( date_end_plan[i],'%d/%m/%Y')
                else:
                    date_end_plan [i]=None
                if date_reordo[i] != '':
                    date_reordo [i]= datetime.strptime( date_reordo[i],'%d/%m/%Y')
                else:
                    date_reordo [i]=None
                if date_end_real[i] != '':    
                    date_end_real [i]=datetime.strptime(date_end_real[i],'%d/%m/%Y')
                else:
                    date_end_real [i]=None
                if Freeze_end_date[i] != '':
                    Freeze_end_date [i]= datetime.strptime(Freeze_end_date[i],'%Y-%m-%d')
                else:
                    Freeze_end_date [i]=None
                    
                if Remain_to_do[i]=='':
                    Remain_to_do [i]=None
                
            

        
                data =Shopfloor(division=division[i],profit_centre=profit_centre[i],order=order[i],material=material[i],
                                designation=designation[i],order_type=order_type[i],order_quantity=order_quantity[i],
                                date_start_plan= date_start_plan[i],date_end_plan = date_end_plan[i],
                                fixation=fixation[i],date_reordo=date_reordo [i] ,message=message[i],order_stat=order_stat[i],
                                customer_order=customer_order[i],date_end_real= date_end_real[i],AllocatedTime=AllocatedTime[i],
                                Leadtime=Leadtime[i],workstation=workstation[i],Allocated_Time_On_Workstation=Allocated_Time_On_Workstation[i],
                                Smooth_Family=Smooth_Family[i],Ranking=Ranking[i],Freeze_end_date=Freeze_end_date[i],Remain_to_do=Remain_to_do[i])
                
                # try:
                #         if Freeze_end_date[0] != None:
                #             data.save()
                #             messages.success(request,"data saved successfully!") 
                # except Exception:
                #     messages.error(request,"fill in the first box of Freeze end date please!")               
                data.save()
            data=Shopfloor.objects.all().values()
            df_data=pd.DataFrame(list(data))
            #df_data.to_csv('df_shopfloor.csv')
            messages.success(request,"Data saved successfully!") 
        else:
             messages.error(request,"Fill in the first box of Freeze end date please!")  
        
                   
                
    return redirect("../")       
        
        
        
    