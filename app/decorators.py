from django.http import HttpResponse
from django.contrib.auth.models import User

def allowed_users(allowed_roles=[]):
    def decorator(view_func):
        
        def wrapper_func (request, *args, **kwargs):
            username="l0005082"
            user=User.objects.filter(username=username).first()
            if not user :
                return HttpResponse("user not exist")
            if user.is_active == False :
                return HttpResponse("user not active")
            if user.groups.exists():
                group = user.groups.all()[0].name 
                if group in allowed_roles :
                    return view_func(request, *args, **kwargs)
                else: 
                    return HttpResponse("user not allowed")
            else:
                return HttpResponse("user has no group")
                       
        return wrapper_func

    return decorator