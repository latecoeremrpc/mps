from django.test import TestCase
from app.models import Division,Zpp


# models test
class DivisionTest(TestCase):
    
    def create_division(self,
                            name="",
                            description="France",
                            created_at="2022-06-21 09:15:52.709769+02",
                            updated_at="2022-06-21 09:15:52.709769+02",
                            created_by="Marwa",
                            is_deleted= True,
                            updated_by="Marwa",
                            deleted_at="2022-06-21 09:15:52.709769+02",
                            deleted_by="Marwa",          
                            
                    ): 
         
        return Division.objects.create(name=name,
                                    description=description,
                                    created_at=created_at,
                                    updated_at=updated_at,
                                    created_by=created_by,
                                    is_deleted=is_deleted,
                                    updated_by=updated_by,
                                    deleted_at=deleted_at,
                                    deleted_by=deleted_by,
                                    )

    def test__divsion_creation(self):
        w = self.create_division()
        self.assertTrue(isinstance(w,Division))
        #self.assertEqual(w.__unicode__(), w.name)

class ZppTest(TestCase):
    
    def create_zpp(self,
                           material="IS0010134M",
                            plan_date="2022-01-10",
                            element="Stock",
                            data_element_planif="A110702015",
                            message=15,
                            needs=0,
                            qte_available=1,
                            date_reordo="2022-05-04",
                            supplier="",
                            customer="C57600",
                            created_at="2022-06-21 09:15:52.709769+02",
                            updated_at="2022-06-21 09:15:52.709769+02",
                            created_by="Marwa",
                            is_deleted= True,
                            updated_by="Marwa",
                            deleted_at="2022-06-21 09:15:52.709769+02",
                            deleted_by="Marwa",          
                            
                    ): 
         
        return Zpp.objects.create(material=material,
                                   plan_date=plan_date,
                                   element=element,
                                   data_element_planif=data_element_planif,
                                   message=message,
                                   needs=needs,
                                   qte_available=qte_available,
                                   date_reordo=date_reordo,
                                   supplier=supplier,
                                   customer=customer,
                                    created_at=created_at,
                                    updated_at=updated_at,
                                    created_by=created_by,
                                    is_deleted=is_deleted,
                                    updated_by=updated_by,
                                    deleted_at=deleted_at,
                                    deleted_by=deleted_by,
                                    )

    def test__zpp_creation(self):
        w = self.create_zpp()
        self.assertTrue(isinstance(w,Zpp))
        # self.assertEqual(w.__unicode__(), w.name)        
        
        
