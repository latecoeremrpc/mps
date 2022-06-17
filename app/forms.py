from django import forms
from app.models import Division,Material,Product,CalendarConfigurationTreatement,CalendarConfigurationCpordo



# creating a form for Division
class DivisionForm(forms.ModelForm):
 
    # create meta class
    class Meta:
        # specify model to be used
        model = Division
 
        # specify fields to be used 
        fields = [
            "name",
            "description",
           
        ] 
        
         
# creating a form for Prodcut
class ProductForm(forms.ModelForm):
    # create meta class
    class Meta:
        # specify model to be used
        model = Product
 
        # specify fields to be used 
        fields = [
            "program",
            "product",
            "planning",
            "has_treatement",
        ]  



# creating a form for Material
class MaterialForm(forms.ModelForm):
 
    # create meta class
    class Meta:
        # specify model to be used
        model = Material
 
        # specify fields to be used 
        fields = [
            "material",
            "workstation",
            "AllocatedTime",
            "Leadtime",
            "Delta_First_Def_And_StartManuf",
            "Delta_Last_Def_And_End_Of_Manuf",
            "Delta_Buffer_OTD",
            "Allocated_Time_On_Workstation",
            "Smooth_Family",   
 
        ] 

# creating a form for CalendarConfigurationTraitement
class CalendarConfigurationTreatementForm(forms.ModelForm):
    # create meta class
    class Meta:
        # specify model to be used
        model = CalendarConfigurationTreatement
 
        # specify fields to be used 
        fields = [
            "Version",
            "TreatementNumber",
            "EndDate",    
        ]  
        
# creating a form for CalendarConfigurationCpordot
class CalendarConfigurationCpordoForm(forms.ModelForm):
    # create meta class
    class Meta:
        # specify model to be used
        model = CalendarConfigurationCpordo
 
        # specify fields to be used 
        fields = [
            "msn",
            "first_def",
            "last_def",     
        ]          