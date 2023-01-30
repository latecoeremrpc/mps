from django.urls import path
from app import views

urlpatterns = [
    
    #url for Home 
    path('home/',views.home_page,name='home'),
    
    #urls for CRUD Division
    path('division/',views.read_division,name='division'),
    path('create/',views.create_division,name='create'),
    path('division/update',views.update_division,name='update'),
    path('division/<id>/delete',views.delete_division,name='delete'),
    path('division/<id>/restore',views.restore_division,name='restore'),

     #urls for CRUD product
    path('division/<division>/product/',views.product,name='product'),
    path('division/<division>/createproduct',views.create_product,name='createproduct'),
    path('division/updateproduct',views.update_product,name='updateproduct'),
    path('division/<id>/deleteproduct',views.delete_product,name='deleteproduct'),
    path('division/<id>/restoreproduct',views.restore_product,name='restoreproduct'),

    #urls for CRUD Material
    path('division/<division>/product/<product>/material/',views.material,name='material'),
    path('division/<division>/product/<product>/creatematerial',views.create_material,name='creatematerial'),
    path('division/<division>/product/updatematerial',views.update_material,name='updatematerial'),
    path('division/<division>/product/<id>/deletematerial',views.delete_material,name='deletematerial'),
    path('division/<division>/product/<id>/restoremateriale',views.restore_material,name='restoremateriale'),
    

    #urls for Calendar
    path('division/<division>/product/<product>/calendar/',views.calendar,name='calendar'),
    path('division/<division>/product/<product>/createcalendar/',views.create_calendar,name='createcalendar'),
    path('division/<division>/product/<product>/deleteday/',views.delete_day,name='deleteday'),

    #urls for Duplicate Calendar
    path('division/<division>/product/<product>/duplicatecalendar/',views.duplicate_calendar,name='duplicatecalendar'),

    #urls for copy calendar from product
    path('division/<division>/product/<product>/copycalendar/',views.copy_calendar,name='copycalendar'), 
    
    #urls for Custom Calendar
    path('division/<division>/product/<product>/customcalendar/',views.custom_calendar,name='customcalendar'),
    path('division/<division>/product/<product>/createcustomcalendar/',views.create_custom_calendar,name='createcustomcalendar'),
    path('division/<division>/product/<product>/deletedaycustom/',views.delete_day_custom,name='deletedaycustom'),
    

    #url for work data
    path('division/<division>/product/<product>/workdata/',views.work_data,name='workdata'),
    
    #url for custom work data
    path('division/<division>/product/<product>/customwork/',views.custom_work,name='customwork'),
    
    #urls for CRUD CalendarConfigurationTraitement
    path('division/<division>/product/<product>/configTrait/',views.config_trait,name='configTrait'),
    path('division/<division>/product/<product>/createconfigTrait',views.create_conf_trait,name='createconfigTrait'),
    path('division/<division>/product/updateconfigTrait',views.update_conf_trait,name='updateconfigTrait'),
    path('division/<division>/product/<id>/deleteconfigTrait',views.delete_conf_trait,name='deleteconfigTrait'),
    path('division/<division>/product/<id>/restoreconfigTrait',views.restore_conf_trait,name='restoreconfigTrait'),
    
    
    #urls for CRUD CalendarConfigurationCpordo
    path('division/<division>/product/<product>/configCpordo/',views.config_cpordo,name='configCpordo'),
    path('division/<division>/product/<product>/createconfigCpordo',views.create_conf_cpordo,name='createconfigCpordo'),
    path('division/<division>/product/updateconfigCpordo',views.update_conf_cpordo,name='updateconfigCpordo'),
    path('division/<division>/product/<id>/deleteconfigCpordo',views.delete_conf_cpordo,name='deleteconfigCpordo'),
    path('division/<division>/product/<id>/restoreconfigCpordo',views.restore_conf_cpordo,name='restoreconfigCpordo'),
    
    #urls for upload files
    path('division/<division>/product/<product>/planningapproval/<planningapproval>/files/uploadcoois',views.upload_coois,name='uploadcoois'),
    path('division/<division>/product/<product>/planningapproval/<planningapproval>/files/uploadzpp',views.upload_zpp,name='uploadzpp'), 
    #urls for shopfloor
    path('division/<division>/product/<product>/allplanning/',views.all_planning,name='allplanning'),
    path('division/<division>/product/<product>/newplanning/',views.new_planning,name='newplanning'),
    path('division/<division>/product/<product>/planningapproval/<planningapproval>/needs/',views.needs,name='needs'),
    path('division/<division>/product/<product>/planningapproval/<planningapproval>/createneeds/',views.create_needs,name='createneeds'), 
    path('division/<division>/product/<product>/planningapproval/<planningapproval>/result/',views.result,name='result'),
    # path('shopfloor/filter/',views.filter,name='filter'),
    # path('division/<division>/product/<product>/planningapproval/<planningapproval>/kpi/shared/',views.result_sharing,name='sharing'),

    # urls for planning 
    # path('division/<division>/product/<product>/planningapproval/<planningapproval>/version/<version>/kpi/',views.filter_kpi,name='kpi'),
    path('division/<division>/product/<product>/planningapproval/<planningapproval>/kpi/',views.filter_kpi,name='kpi'),
    # path('division/<division>/product/<product>/planningapproval/<planningapproval>/kpiversion/',views.version_selected,name='kpiversion'),
    # path('division/<division>/product/<product>/planningapproval/<planningapproval>/version/<version_selected>/updatecycle',views.update_cycle,name='newcycle'), 
    # path('division/<division>/product/<product>/planningapproval/<planningapproval>/updatecycle',views.update_cycle,name='newcycle'), 


     
    
     
    
    
   
]
