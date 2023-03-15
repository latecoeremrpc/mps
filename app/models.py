from time import timezone
from django.db import models
from django.contrib.auth.models import User

# Create your models here.

## Django will not create a migration For 
# BasedModel and SoftDeleteModel
# will just extending


#BasedModel
class BaseModel(models.Model) :
    created_at = models.DateTimeField(auto_now_add=True)   
    updated_at = models.DateTimeField(auto_now=True, null=True)
    created_by= models.CharField(max_length= 30, default='Marwa')
    updated_by = models.CharField(max_length= 30,default='Marwa')
    
    class Meta :
         #Django will not create a database table for this model
         abstract = True 

#creating a custom model manager to apply the filter 
#automatically without using filter(is_delete=False) 

#SoftDeleteManager
class SoftDeleteManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_deleted=False)


#SoftDeleteModel
class SoftDeleteModel(models.Model):
    is_deleted = models.BooleanField(null= False, default=False)
    deleted_by= models.CharField(max_length= 30,null=True)
    deleted_at = models.DateTimeField(auto_now_add=True,null=True) 
    restored_at = models.DateTimeField(auto_now=True, null=True)
    restored_by = models.CharField(max_length= 30,default='Marwa',null=True)
    
    objects = models.Manager()
    undeleted_objects = SoftDeleteManager()

    def soft_delete(self):
        self.is_deleted = True
        self.save()

    def restore(self):
        self.is_deleted = False
        self.save()
    

    class Meta :
        #Django will not create a database table for this model
        abstract= True

#**************************************************************

# Division Model
class Division(BaseModel,SoftDeleteModel):
     name = models.IntegerField(unique= True)
     description = models.CharField(max_length=200,unique=True)

    # renames the instances of the Division
    # with their name
     def __str__(self):
        return str(self.id) 

#Product Model
class Product(BaseModel,SoftDeleteModel):
    program = models.CharField(max_length=200)
    has_treatement = models.BooleanField(null= False, default=False) 
    product = models.CharField(max_length=200)
    planning= models.CharField(max_length=200)
    Profit_center= models.CharField(max_length=200,null= True)
    division= models.ForeignKey(Division, on_delete=models.CASCADE)

# renames the instances of the Product
    # with their program
    def __str__(self):
        return self.product


#Material Model 
class Material(BaseModel,SoftDeleteModel):
    material= models.CharField(max_length=200)
    workstation= models.CharField(max_length=200)
    AllocatedTime =models.FloatField()
    Leadtime =models.FloatField()
    Delta_First_Def_And_StartManuf =models.FloatField(verbose_name='First Def And Start Manuf')
    Delta_Last_Def_And_End_Of_Manuf =models.FloatField(verbose_name='Last Def And End Manuf')
    Delta_Buffer_OTD=models.FloatField()
    Allocated_Time_On_Workstation =models.FloatField()
    Smooth_Family=models.CharField(max_length=50)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)

    # renames the instances of the Material
    # with their program
    def __str__(self):
        return self.material


#HolidayCalendar Model
class HolidaysCalendar(BaseModel,SoftDeleteModel):
    name= models.CharField(max_length=200, null=False)
    holidaysDate= models.DateField(null= False)
    product = models.ForeignKey(Product, on_delete=models.CASCADE,null=True) 
    owner = models.CharField(default='officiel',max_length=30)

    # renames the instances of the HolidayCalendar 
    # with their program
    def __str__(self):
        return self.name
 

#WorkData Model
class WorkData(BaseModel,SoftDeleteModel):
    startTime=models.TimeField()
    endTime=models.TimeField()  
    date=models.DateField()
    FTEhourByDay= models.FloatField()
    ExtraHour= models.FloatField()
    Absenteeism_ratio= models.FloatField()
    Unproductiveness_ratio= models.FloatField()
    Efficienty_ratio=models.FloatField()
    # cycle_time=models.FloatField()
    owner = models.CharField(default='officiel',max_length=30)
    product = models.ForeignKey(Product, on_delete=models.CASCADE,null=True)
    

    # renames the instances of the WorkData 
    # with their startTime
    #To Do: Convert strTime to string
    def __str__(self):
        return str(self.date)

#Calendar configuration traitement Model 
class CalendarConfigurationTreatement(BaseModel,SoftDeleteModel):
    Version= models.CharField(max_length=200)
    TreatementNumber =models.IntegerField(verbose_name='Treatment Number')
    EndDate=models.DateField(verbose_name='End Date')
    product = models.ForeignKey(Product, on_delete=models.CASCADE,null=True)
    
    # renames the instances of the CalendarConfigurationTreatement 
    # with their Version
    def __str__(self):
        return self.Version
    
#calendar configuration cpordo Model 
class CalendarConfigurationCpordo(BaseModel,SoftDeleteModel):
    msn=models.IntegerField() 
    first_def=models.IntegerField(verbose_name='First Def')
    last_def=models.IntegerField(verbose_name='Last Def ')
    product = models.ForeignKey(Product, on_delete=models.CASCADE,null=True)
    
    # renames the instances of the calendarConfigurationCpordo 
    # with their msn
    def __str__(self):
        return  str(self.msn)


# Planning model 
class PlanningApproval(BaseModel,SoftDeleteModel):
    name=models.CharField(max_length=200)
    product = models.ForeignKey(Product,on_delete=models.CASCADE,null=True)
    def __str__(self):
        return  str(self.name)


#Coois Model    
class Coois(BaseModel,SoftDeleteModel):
    division=models.IntegerField(null=True)
    profit_centre=models.CharField(max_length=50,null=True)
    order=models.CharField(max_length=50)
    material= models.CharField(max_length=50,null=True)
    designation=models.CharField(max_length=50,null=True)
    order_type=models.CharField(max_length=50,null=True)
    order_quantity=models.IntegerField()
    date_start_plan=models.DateField(null=True)
    date_end_plan=models.DateField(null=True)  
    fixation=models.CharField(max_length=50,null=True)
    manager=models.CharField(max_length=50,null=True)
    order_stat=models.CharField(max_length=50,null=True)
    customer_order=models.CharField(max_length=50,null=True)
    date_end_real=models.DateField(null=True)  
    entered_by=models.CharField(max_length=50,null=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE,null=True)
    planning_approval = models.ForeignKey(PlanningApproval, on_delete=models.CASCADE,null=True)

    
    # renames the instances of the Coois
    # with their designation
    def __str__(self):
        return  str(self.designation)

#Zpp Model
class Zpp(BaseModel,SoftDeleteModel):
    material= models.CharField(max_length=50,null=True)
    plan_date= models.DateField(null=True)
    element= models.CharField(max_length=50,null=True)
    data_element_planif=models.CharField(max_length=100,null=True) 
    message= models.FloatField(null=True)
    needs=models.FloatField(null=True)   
    qte_available= models.FloatField(null=True)
    date_reordo=models.DateField(null=True)
    supplier= models.CharField(max_length=50,null=True)    
    customer= models.CharField(max_length=50,null=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE,null=True)
    planning_approval = models.ForeignKey(PlanningApproval, on_delete=models.CASCADE,null=True)

    
    # renames the instances of the Zpp
    # with their element
    def __str__(self):
        return  str(self.element)      

#Shoploor Model
class Shopfloor(BaseModel,SoftDeleteModel):
    division=models.IntegerField(null=True)
    profit_centre=models.CharField(max_length=50,null=True)
    order=models.CharField(max_length=50)
    material= models.CharField(max_length=50,null=True)
    designation=models.CharField(max_length=50,null=True)
    order_type=models.CharField(max_length=50,null=True)
    order_quantity=models.IntegerField()
    date_start_plan=models.DateField(null=True)
    date_end_plan=models.DateField(null=True)  
    fixation=models.CharField(max_length=50,null=True)
    date_reordo=models.DateField(null=True)
    message= models.FloatField(null=True)
    order_stat=models.CharField(max_length=50,null=True)
    customer_order=models.CharField(max_length=50,null=True)
    date_end_real=models.DateField(null=True) 
    AllocatedTime =models.FloatField()
    Leadtime =models.FloatField()
    workstation= models.CharField(max_length=200)
    Allocated_Time_On_Workstation =models.FloatField()
    Smooth_Family=models.CharField(max_length=50)
    Ranking=models.DateField()
    Freeze_end_date=models.DateTimeField(null=True)
    Remain_to_do=models.FloatField(null=True)
    smoothing_end_date=models.DateTimeField(null=True)
    closed=models.BooleanField(null=True)
    version=models.IntegerField(null=True)
    shared=models.BooleanField(null=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True)
    planning_approval = models.ForeignKey(PlanningApproval, on_delete=models.CASCADE,null=True)

    
    # renames the instances of the Shopfloor
    # with their version
    def __str__(self):
        return  str(self.version)  

#Cycle Model
class Cycle(BaseModel,SoftDeleteModel):
    division= models.IntegerField()
    profit_center= models.CharField(max_length=200)
    work_day= models.DateField()
    smooth_family= models.CharField(max_length=100)
    cycle_time=models.FloatField(null=True)
    workdata=models.ForeignKey(WorkData,on_delete=models.CASCADE,null=True)
    owner = models.CharField(default='officiel',max_length=30)
    product = models.ForeignKey(Product, on_delete=models.CASCADE,null=True)
    version=models.IntegerField(null=True)
    planning_approval = models.ForeignKey(PlanningApproval, on_delete=models.CASCADE,null=True)
    shared=models.BooleanField(default=True,null=True)


    # renames the instances of the Cycle
    # with their profit_center
    def __str__(self):
        return  str(self.profit_center)   


#Staff Model
class Staff(BaseModel,SoftDeleteModel,User):
    function=models.CharField(max_length=50)
    division= models.ForeignKey(Division, on_delete=models.CASCADE)

    # renames the instances of the Staff
    # with their function
    def __str__(self):
        return  str(self.function)   




    
  