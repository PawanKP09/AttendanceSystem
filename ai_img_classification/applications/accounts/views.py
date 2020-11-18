import datetime
import json
import numpy as np
import os
import pathlib
import pickle
from django.contrib.auth import authenticate, login
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.http import HttpResponse,JsonResponse
from django.shortcuts import redirect
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views import View
from .models import User, Logs

def validateEmail(email):
    try:
        validate_email(email)
        return True
    except ValidationError:
        return False

# Create your views here.
class SignUpView(View):

    def get(self,request):
        return render(self.request,'signup.html')

    def post(self,request):
        if self.request.POST['first_name']  and self.request.POST['email'] and self.request.POST['password']:
            user = User()
            user.first_name = self.request.POST['first_name']
            user.last_name = self.request.POST['last_name']
            email = validateEmail(self.request.POST["email"])
            if email == True:
                user.email = self.request.POST["email"].lower()
                user.username = user.email
            else:
                data = {}
                data['result'] = "Please enter a valid email address"
                return HttpResponse(json.dumps(data),
                                    content_type="application/json")
            user.set_password(self.request.POST['password'])
            users = list(User.objects.values_list("email",flat=True))
            if not user.email in users:
                user.save()
                data = {}
                data['result'] = "success"
                login(self.request,user)
                return HttpResponse(json.dumps(data),
                                    content_type="application/json")
            else:
                data = {}
                data['result'] = "User already exist.Please login"
                return HttpResponse(json.dumps(data),content_type="application/json")
        else:
            data = {}
            data['result'] = "Both fields are mandatory"
            return HttpResponse(json.dumps(data),
                                content_type="application/json")



class LoginView(View):

    def get(self,request):
        return render(self.request,"login.html")

    def post(self,request):
            username = self.request.POST['username']
            password = self.request.POST['password']
            if username and password:
                user = authenticate(username=username, password=password)
            else:
                data = {}
                data['result'] = "please fill both fields"
                return HttpResponse(json.dumps(data),
                                    content_type="application/json")
            if user:
                login(self.request, user)
                data = {}
                data['result'] = "success"
                return HttpResponse(json.dumps(data),
                                    content_type="application/json")
            else:
                data = {}
                data['result'] = "invalid credentials"
                return HttpResponse(json.dumps(data),
                                    content_type="application/json")


class LogoutView(View):

    @method_decorator(login_required)
    def get(self, *args, **kwargs):
        logout(self.request)
        return redirect('/accounts/login/')


# @csrf_exempt
# def process(request):
#     body_unicode = request.body.decode('utf-8')
#     body = json.loads(body_unicode)
#     content = body['name']
#     times = []
#     times.append(datetime.datetime.now().time())
#     date = datetime.datetime.today().date()
#     user = User.objects.get(first_name=content)
#     logs = Logs.objects.filter(date__date=date)
#     try:
#         log_obj = Logs.objects.get(user_obj=user,date=date)
#         if log_obj.in_time:
#             log_obj.out_time = times[0]
#             s1 = log_obj.in_time.strftime("%H:%M:%S")
#             s2 = log_obj.out_time.strftime("%H:%M:%S")
#             FMT = '%H:%M:%S'
#             tdelta = datetime.datetime.strptime(s2, FMT) - datetime.datetime.strptime(s1, FMT)
#             log_obj.total_hours = tdelta
#             log_obj.date = date
#             log_obj.user_obj = user
#             log_obj.save()
#         else:
#             log_obj.in_time = times[0]
#             log_obj.out_time = times[0]
#             log_obj.date = date
#             log_obj.user_obj = user
#             log_obj.save()
#     except:
#         log_obj = Logs()
#         log_obj.in_time = times[0]
#         log_obj.out_time = times.pop()
#         log_obj.date = date
#         log_obj.user_obj = user
#         log_obj.save()
#     return HttpResponse('This is a post only view')


class DeleteUserView(View):
    def get(self,request):
        id = self.request.GET.get("id")
        user = User.objects.get(id=id)
        name = user.first_name
        my_file = pathlib.Path("dataset_faces_v2.1.dat")
        if my_file.is_file():
            with open('dataset_faces_v2.1.dat', 'rb') as f:
                known_face_encodings = pickle.load(f)
                if name in list(known_face_encodings.keys()):
                    known_face_encodings.pop(name)
                else:
                    pass
            # with open("dataset_faces_v2.1.dat", "wb") as file:
            #     pickle.dump(known_face_encodings, file)
        user.delete()
        return JsonResponse({"success": "user deleted successfully"})


class NumpyArrayEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return json.JSONEncoder.default(self, obj)


class UserEncodesView(View):
    def get(self,request):
        my_file = pathlib.Path("dataset_faces_v2.1.dat")
        if my_file.is_file():
            print("file_exist")
            path = 'dataset_faces_v2.1.dat'
            if os.path.getsize(path) > 0:
                with open(path, 'rb') as f:
                    all_face_encodings = pickle.load(f)
                    known_face_names = list(all_face_encodings.keys())
                    if len(known_face_names) == 0:
                        return JsonResponse({"message": "we have no trained faces for inference"})
                    else:
                        known_face_encodings = list(all_face_encodings.values())
                        data = {"array": known_face_encodings}
                        encodedNumpyData = json.dumps(data, cls=NumpyArrayEncoder)  # use dump() to write array into file
                        return JsonResponse({"names":known_face_names,"encodings":encodedNumpyData})
        else:
            return JsonResponse({"data":"false"})


@csrf_exempt
def process(request):
    body_unicode = request.body.decode('utf-8')
    body = json.loads(body_unicode)
    content = body['name']
    times = []
    times.append(datetime.datetime.now().time().replace(microsecond=0))
    date = datetime.datetime.today()
    user = User.objects.get(first_name=content)
    # logs = Logs.objects.filter(date__date=date)
    try:
        log_obj = Logs.objects.get(user_obj=user,date__date=date)
        if log_obj.in_time:
            log_obj.out_time = times[0]
            s1 = log_obj.in_time.strftime("%H:%M:%S")
            s2 = log_obj.out_time.strftime("%H:%M:%S")
            FMT = '%H:%M:%S'
            tdelta = datetime.datetime.strptime(s2, FMT) - datetime.datetime.strptime(s1, FMT)
            log_obj.total_hours = tdelta
            log_obj.date = date
            log_obj.user_obj = user
            log_obj.save()
        else:
            log_obj.in_time = times[0]
            log_obj.out_time = times[0]
            log_obj.date = date
            log_obj.user_obj = user
            log_obj.save()
    except:
        log_obj = Logs()
        log_obj.in_time = times[0]
        log_obj.out_time = times.pop()
        log_obj.date = date
        log_obj.user_obj = user
        log_obj.save()
    return HttpResponse('This is a post only view')