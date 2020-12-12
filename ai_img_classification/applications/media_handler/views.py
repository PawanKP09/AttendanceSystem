import base64
import cv2
import datetime
import face_recognition
import json
import numpy as np
import os
import pathlib
import pickle
import requests
from time import sleep
import urllib.request
import xlwt
from django.core.files.base import ContentFile
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import HttpResponse,StreamingHttpResponse,HttpResponseServerError,JsonResponse
from django.shortcuts import render
from django.views import View
from applications.accounts.models import User, UserImages, Logs
from applications.media_handler.classifier_train import face_encoder_mul


url = "http://127.0.0.1:8080/backend/process/"

class IndexView(View):
    def get(self,request):
        print("Loading the encoded faces from the saved file!!!")
        # Load face encodings from saved files.
        # with open('dataset_faces_v2.1.dat', 'rb') as f:
        #     all_face_encodings = pickle.load(f)
        get_encodings = requests.get("http://127.0.0.1:8080/backend/user-encodes")
        data = get_encodings.json()
        print(data)
        if "data" in data.keys():
            alert = data["data"]
            return JsonResponse({"success": alert})
        if "message" in data.keys():
            alert = data["message"]
            return JsonResponse({"success":alert})
        # faces = data["data"]
        # print(faces)

        # Grab the list of names and the list of encodings
        # known_face_names = list(all_face_encodings.keys())
        # known_face_encodings = np.array(list(all_face_encodings.values()))
        known_face_names = data["names"]
        print(known_face_names)
        encodings = eval(data["encodings"])
        known_face_encodings = list(np.asarray(encodings["array"]))
        print(known_face_encodings)
        print("Loaded the saved encodes and labels from the database file!!!")
        sleep(2)

        print("Initiating the predictions!!!")
        sleep(2)

        ## Print Texts
        # when no face detected in the frame.
        no_face = "No face(s) detected in the frame!!!"
        # When known face is detected in the frame.
        known_face = "Known face(s) detected in the frame!!!"
        # When unknown face is detected in the frame.
        unknown_face = "Unknow face(s) detected in the frame!!!"

        # Initializing a camera object for live input feed.

        ## Uncomment the below lines to use the IPCAM feed
        URL = "http://192.168.43.1:8080/shot.jpg"
        cap = cv2.VideoCapture(URL)

        # Reading the WebCam directly
        # cap = cv2.VideoCapture(0)

        # while True:
        while (cap.isOpened()):
            ret, frame = cap.read()
            ## Uncomment the below lines to stream the Live feed from the IPCAM
            img_arr = np.array(bytearray(urllib.request.urlopen(URL).read()), dtype=np.uint8)
            frame = cv2.imdecode(img_arr, -1)

            # * ---------- Encode the Input feed fromt he camera --------- *
            # Load picture fromt he live feed
            face_picture = frame
            cv2.imshow("Live Feed", face_picture)
            sleep(1)
            if cv2.waitKey(1) & 0xff == ord('q'):
                break

            # Detect faces
            face_locations = face_recognition.face_locations(face_picture)

            # Checking if there are any faces detected in the frame.
            if len(face_locations) == 0:
                print("\r", end='')
                print("{}".format(no_face), end="", sep=" ", flush=True)


            elif len(face_locations) > 1:
                print("Multiple Faces detected")

            else:
                # Encode faces from the live input
                face_encodings = face_recognition.face_encodings(face_picture, face_locations)
                # Show the live input from the camera.
                # cv2.imshow("Live Feed", face_picture)
                # Quit if   is pressed.5q
                # if cv2.waitKey(1) & 0xff==ord('q'):
                # break

                # Loop in all detected faces
                for face_encoding in face_encodings:

                    # See if the face is a match for the known face (that we saved in the precedent step)
                    matches = face_recognition.compare_faces(known_face_encodings, face_encoding)

                    if True in matches:
                        # print("Known face in the frame")
                        print("\r", end='')
                        print("{}".format(known_face), end="", sep=" ", flush=True)

                        # winsound.Beep(frequency, duration)

                        # check the known face with the smallest distance to the new face
                        face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)

                        # Take the best one
                        best_match_index = np.argmin(face_distances)

                        # if we have a match:
                        if matches[best_match_index]:

                            # Give the detected face the name of the employee that match
                            name = known_face_names[best_match_index]
                            print("")
                            print("Hi " + str(name) + " Welcome to UST GLobal!!!")
                            headers = {'Content-type': 'application/json',
                                       'Accept': 'text/plain'}
                            post_data = {"name": str(name)}
                            print(post_data)

                            check = requests.post(url, data=json.dumps(post_data),
                                                  headers=headers)
                            print(check)
                            # engine.say("Hello " + str(name) +", welcome to UST Global")
                            # engine.runAndWait()
                            # winsound.Beep(frequency, duration)

                            # Write the recognized face name from the database
                            cv2.putText(face_picture, str(name), (30, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
                            cv2.imshow("Predicted Feed", face_picture)

                            if cv2.waitKey(1) & 0xff == ord('q'):
                                break
                    # When there are no faces found in the input frame.
                    else:
                        print("\r", end='')
                        print("{}".format(unknown_face), end="", sep=" ", flush=True)
                        # engine.say("Unauthorized, to access the premises")
                        # engine.say("Access Denied")
                        # engine.runAndWait()
                        # winsound.Beep(frequency, duration)

        cap.release()
        cv2.destroyAllWindows()

        return JsonResponse({"start":"inference will start soon"})


class DashboardView(View):
    def get(self,request):
        # url = 'http://127.0.0.1:8080/backend/dashboard'
        date = None
        if request.GET.get("date") and request.GET.get("search"):
            q = self.request.GET.get('date')
            search = self.request.GET.get('search')
            date = datetime.datetime.strptime(q, "%Y-%m-%d").date()
            # PARAMS = {'date': date,"search":search}
            today = date
        elif request.GET.get("date"):
            q = self.request.GET.get('date')
            date = datetime.datetime.strptime(q, "%Y-%m-%d").date()
            # PARAMS = {'date': date}
            today = date
        elif request.GET.get("search"):
            search = self.request.GET.get('search')
            today = datetime.datetime.today().date()
            # PARAMS = {'search': q,"date":today}
        else:
            today = datetime.datetime.today().date()
            # PARAMS = {'date':today}
        # query = requests.get(url,params=PARAMS)
        # data = query.json()
        # users = data["users"]
        # trained = data["trained"]
        # if self.request.GET.get("date"):
        #     q = self.request.GET.get('date')
        #     date = datetime.datetime.strptime(q, "%Y-%m-%d").date()
        #     logs = Logs.objects.filter(date__date=date)
        #     # logs_request_with_date = requests.get('http://127.0.0.1:8080/backend/dashboard')
        #     todays_user = logs.values_list("user_obj", flat=True)
        #     today = date
        # else:
        #     today = datetime.datetime.today().date()
        #     logs = Logs.objects.filter(date__date=today)
        #     todays_user = logs.values_list("user_obj", flat=True)
        if 'search' in request.GET:
            search = search
            logs = Logs.objects.filter(Q(user_obj__first_name__contains=search) | Q(user_obj__Uid__contains=search),
                                       date__date=today)
            users = list(User.objects.filter(Q(first_name__contains=search) | Q(Uid__contains=search)).values())
        else:
            logs = Logs.objects.filter(date__date=today)
            users = list(User.objects.values())
        print(logs)
        # for log in logs:
        #     print(type(log.in_time))
        #     log.in_time = datetime.datetime.strptime(log.in_time,'%H:%M:%S')
        #     log.out_time = datetime.datetime.strptime(log.out_time,'%H:%M:%S')
        todays_user = []
        for user in users:
            if user["is_superuser"]:
                del user
        for log in logs:
            todays_user.append(log.user_obj.username)
        print(todays_user)
        print(users)
        for user in users:
            if user["username"] in todays_user:
                for log in logs:
                    if log.user_obj.username == user["username"]:
                        user.update({"in_time": log.in_time})
                        user.update({"out_time": log.out_time})
                        user.update({"total_hours": log.total_hours})
                        user.update({"status": "present"})
            else:
                for log in logs:
                    if log.user_obj.username == user["username"]:
                        user.update({"in_time": "NA"})
                        user.update({"out_time": "NA"})
                        user.update({"total_hours": "NA"})
                        user.update({"status": "absent"})


        # todays_user = logs.values_list("user_obj", flat=
        path = 'dataset_faces_v2.1.dat'
        trained_users = []
        my_file = pathlib.Path("dataset_faces_v2.1.dat")
        known_face_names = []
        if my_file.is_file():
            print("file_exist")
            with open(path, 'rb') as f:
                all_face_encodings = pickle.load(f)
                known_face_names = list(all_face_encodings.keys())
                print(known_face_names)
        if len(known_face_names) > 0:
            for user in users:
                if user["first_name"] in known_face_names:
                    trained_users.append(user["first_name"])
        else:
            trained_users = []
        print(trained_users,"CCCCCCCCCCCCCCCCCC")
        return render(self.request,"landing.html",{'logs':logs, "today": today,"users":users,
                                                   "todays_user": todays_user, "trained": trained_users})

    # def post(self,request):
    #     if self.request.FILES["upload_file"]:
    #         name = self.request.FILES["upload_file"].name
    #         data = {}
    #         if not name.endswith((".zip",".jar")):
    #             data["result"]="please upload a zip file"
    #             return HttpResponse(json.dumps(data), content_type="application/json")
    #         queryset = Attachment.objects.filter(user=self.request.user)
    #         queryset.delete()
    #         d = "media/"+ request.user.first_name + "/extracts/"
    #         if os.path.exists(d):
    #             shutil.rmtree(d)
    #         obj = Attachment()
    #         obj.attachment = self.request.FILES["upload_file"]
    #         obj.user = self.request.user
    #         obj.save()
    #         url = obj.attachment.path
    #         filenames = get_filenames(self.request.user.first_name,url)
    #         created_obj = Attachment.objects.filter(user=self.request.user).last()
    #         lowest_dirs = list()
    #
    #         for root, dirs, files in os.walk(d):
    #             if not dirs:
    #                 lowest_dirs.append(root)
    #             for file in files:
    #                 if file.endswith((".png",".jpg",".jpeg",".JPG",".JPEG",".PNG")):
    #                     pass
    #                 else:
    #                     obj.delete()
    #                     shutil.rmtree(d)
    #                     data["result"] = "Please upload only image files"
    #                     return HttpResponse(json.dumps(data), content_type="application/json")
    #         filename = name.split(".")[0]
    #         path_1 = "media/" + request.user.first_name + "/extracts/"+ filename + "\\train"
    #         path_2 = "media/" + request.user.first_name + "/extracts/"+ filename + "\\validation"
    #         print(path_1,path_2)
    #         # dir_1 = [name for name in os.listdir("media/"+ request.user.first_name + "/extracts/")]
    #         # dir_2 = [sub for sub in os.listdir("media/"+ request.user.first_name + "/extracts/" + dir_1[0])]
    #         # dir_3 = [sub for sub in os.listdir("media/"+ request.user.first_name + "/extracts/" + dir_1[0] + "/" + dir_2[0])]
    #         # dir_4 = [sub for sub in os.listdir("media/" + request.user.first_name + "/extracts/" + dir_1[0] + "/" + dir_2[0] + '/' + dir_3[0])]
    #         # dir_5 = [sub for sub in os.listdir("media/" + request.user.first_name + "/extracts/" + dir_1[0] + "/" + dir_2[0] + '/' + dir_3[0] + '/' + dir_4[0])]
    #         # dir_6 = [sub for sub in os.listdir("media/" + request.user.first_name + "/extracts/" + dir_1[0] + "/" + dir_2[0] + '/' + dir_3[0] + '/' + dir_4[1])]
    #         if not os.path.exists(path_1) or not os.path.exists(path_2):
    #             obj.delete()
    #             shutil.rmtree(d)
    #             data["result"] = "We need labels with in folders named train and validation.Kindly rename your folders"
    #             return HttpResponse(json.dumps(data), content_type="application/json")
    #         image_labels = [name for name in os.listdir(path_1)
    #                         if os.path.isdir(os.path.join(path_1, name))]
    #         image_labels.sort()
    #         print(image_labels,"ccccccccccccccccccccccccccccc")
    #         if len(image_labels) == 0:
    #             obj.delete()
    #             shutil.rmtree(d)
    #             data["result"] = "Please upload dataset with standard directory structure."
    #             return HttpResponse(json.dumps(data), content_type="application/json")
    #         if os.path.isdir(path_2):
    #             print("Standard format eval dir found")
    #             if path_2 is not None:
    #                 eval_image_labels = [name for name in os.listdir(path_2)
    #                                      if os.path.isdir(os.path.join(path_2, name))]
    #                 eval_image_labels.sort()
    #                 if len(eval_image_labels) == 0:
    #                     obj.delete()
    #                     shutil.rmtree(d)
    #                     data["result"] = "Please upload dataset with standard directory structure."
    #                     return HttpResponse(json.dumps(data), content_type="application/json")
    #                 # If the labels in the train_dir and eval_dir do not match, exit!
    #                 if image_labels != eval_image_labels:
    #                     obj.delete()
    #                     shutil.rmtree(d)
    #                     data["result"] = "The labels within validation directory should be identical to train directory"
    #                     return HttpResponse(json.dumps(data), content_type="application/json")
    #
    #         path = settings.MEDIA_ROOT
    #         constant_path_black = lowest_dirs[0]
    #         constant_path_good = lowest_dirs[1]
    #         # return render(self.request,"steps.html",{"black":dir_5,"good":dir_6,"black_path":constant_path_black,"good_path":constant_path_good})
    #         data['result'] = "success"
    #         data["black"] = os.listdir(lowest_dirs[0])
    #         data["good"] = os.listdir(lowest_dirs[1])
    #         data["black_path"] = constant_path_black
    #         data["good_path"] = constant_path_good
    #         return HttpResponse(json.dumps(data),content_type="application/json")

#old training script
# class TrainView(View):
#     def get(self,request):
#         # return render(self.request,"stepwizard.html")
#         path_1 = "media/" + request.user.first_name + "/vad_model/"
#         path_2 = "media/" + request.user.first_name + "/vad_prd_model/"
#         if os.path.isdir(path_1):
#             shutil.rmtree(path_1,ignore_errors=True)
#         if os.path.isdir(path_2):
#             shutil.rmtree(path_2,ignore_errors=True)
#         start_time = time.time()
#         filename = self.request.GET.get("filename").split('.')[0]
#         print(filename)
#         user = self.request.user.first_name
#         epoch = self.request.GET.get("epoch")
#         batch = self.request.GET.get("batch")
#         print(epoch)
#         print(batch)
#         training = train1_model(user,epoch,batch,filename)
#         if training:
#             data = {}
#             obj = Attachment.objects.filter(user=self.request.user).last()
#             download_path = obj.export_dir.url
#             data['url'] = download_path
#             # data['task_id'] = training.task_id
#             data['result'] = "success"
#             data['text'] = "Your Model file is ready for download"
#             end_time = time.time()
#             print("Total execution time: {} seconds".format(
#                 end_time - start_time))
#
#             return HttpResponse(json.dumps(data),
#                                 content_type="application/json")
#         else:
#             user = self.request.user
#             try:
#                 obj = Attachment.objects.filter(user=user).last()
#                 obj.delete()
#             except:
#                 pass
#             data = {}
#             data['error'] = "An error Occured.Please upload the file and try again"
#             return HttpResponse(json.dumps(data),content_type="application/json")

    # def post(self,request):
    #     # flag = self.request.POST["flag"]
    #     # if flag:
    #     user = self.request.user.first_name
    #     training = train_model(user)
    #     if training:
    #         data = {}
    #         data['result'] = "success"
    #         return HttpResponse(json.dumps(data),content_type="application/json")
    #     else:
    #         user = self.request.user
    #         try:
    #             obj = Attachment.objects.filter(user=user).last()
    #             obj.delete()
    #         except:
    #             pass
    #         data = {}
    #         data['error'] = "An error Occured.Please upload the file and try again"
    #         return HttpResponse(json.dumps(data),content_type="application/json")


class TrainView(View):
    def get(self, request):
        value = face_encoder_mul()
        return JsonResponse({"success": value})


class UserLogView(View):
        def get(self, *args, **kwargs):
            # users = User.objects.all()
            # PARAMS = {'id':kwargs["id"]}
            # url = "http://127.0.0.1:8080/backend/user-log"
            # query = requests.get(url, params=PARAMS)
            # data = query.json()
            id = kwargs["id"]
            created = None
            print(id)
            user_logs = Logs.objects.filter(user_obj__id=id)
            images = UserImages.objects.filter(user_obj__id=id)
            user_images = []
            # for image in images:
            #     pictures = {}
            #     pictures["url"] = "http://127.0.0.1:8000" + image.image.url
            #     pictures["name"] = image.image.name.rsplit('/', 1)[1]
            #     user_images.append(pictures)
            user = User.objects.get(id=id)
            all_user_dates = []
            for log in user_logs:
                all_user_dates.append(log.date.replace(tzinfo=None).date())
            print(user.date_joined)
            created = user.date_joined.replace(tzinfo=None)
            date_times = []
            today = datetime.datetime.today()
            day_count = (today - created).days + 1
            print(day_count)
            for i in range(0, day_count):
                date_times.append(today - datetime.timedelta(days=i))
            dates = []
            for date in date_times:
                dates.append(date.date())
            user_logs_list = []
            if len(user_logs) > 0:
                for date in dates:
                    datas = {}
                    if date in all_user_dates:
                            obj = Logs.objects.get(user_obj__id=id, date__date=date)
                            datas["in_time"] = obj.in_time
                            datas["out_time"] = obj.out_time
                            datas["total_hour"] = obj.total_hours
                            datas['status'] = "present"
                            datas["user-id"] = obj.user_obj.id
                            datas['date'] = date
                            datas["name"] = obj.user_obj.first_name
                            datas["uid"] = obj.user_obj.Uid
                            user_logs_list.append(datas)
                    else:
                            user = User.objects.get(id=id)
                            datas["in_time"] = "NA"
                            datas["out_time"] = "NA"
                            datas["total_hour"] = "NA"
                            datas['status'] = "absent"
                            datas["user-id"] = id
                            datas['date'] = date
                            datas["name"] = user.first_name
                            datas["uid"] = user.Uid
                            user_logs_list.append(datas)

            else:
                print("else_statement")
                created = user.date_joined.replace(tzinfo=None)
                today = datetime.datetime.today()
                day_count = (today - created).days + 1
                for date in (created + datetime.timedelta(n) for n in range(day_count)):
                    datas = {}
                    user = User.objects.get(id=id)
                    datas["in_time"] = "NA"
                    datas["out_time"] = "NA"
                    datas["total_hour"] = "NA"
                    datas['status'] = "absent"
                    datas["user_id"] = id
                    datas['date'] = date.date()
                    datas["name"] = user.first_name
                    datas["uid"] = user.Uid
                    user_logs_list.append(datas)
            page_number = self.request.GET.get('page')
            paginator = Paginator(user_logs_list, 10)
            page_obj = paginator.get_page(page_number)
            return render(self.request, "user-log-detail.html", {"user_logs": user_logs, "images": images, 'page_obj': page_obj,"user":user,"created":created})


class UploadImagesView(View):
    def get(self, request):
        return render(self.request,"upload_image.html")

    def post(self, request):
            data = {}
            name = request.POST.get("name")
            uid = request.POST.get("uid")
            if User.objects.filter(first_name=name).exists():
                data['result'] = "A user with that name already exist"
                return HttpResponse(json.dumps(data), content_type="application/json")
            user = User()
            length = len(request.FILES.getlist("upload_imgs[]"))
            if length < 4:
                data['result'] = "We need a minimum of 4 images to train"
                return HttpResponse(json.dumps(data), content_type="application/json")
            if name and uid:
                user.first_name = name
                user.username = name + "@ust-global.com"
                user.Uid = uid
                # user.save()
                for file in request.FILES.getlist("upload_imgs[]"):
                    ext = file.name.split('.')[1]
                    file.name = name + "." + ext
                    image_obj = UserImages()
                    user.save()
                    image_obj.user_obj = user
                    image_obj.image = file
                    image_obj.image.name = file.name
                    image_obj.save()
                data['result'] = "success"
                return HttpResponse(json.dumps(data), content_type="application/json")
            else:
                data['result'] = "Both fields are mandatory"
                return HttpResponse(json.dumps(data), content_type="application/json")


class CaptureView(View):
    def get(self, request):
        # url = 'http://127.0.0.1:8080/backend/user-images'
        images = UserImages.objects.all()
        return render(self.request,"capture.html", {"images": images})

    def post(self, request):
        data1 = {}
        name = request.POST.get("name")
        print(name)
        if User.objects.filter(first_name=name).exists():
            data1['result'] = "A user with that name already exist"
            return HttpResponse(json.dumps(data1), content_type="application/json")
        uid = request.POST.get("uid")
        length = len(request.POST.getlist("filename[]"))
        if length < 4:
            data1['result'] = "We need a minimum of 4 images to train"
            return HttpResponse(json.dumps(data1), content_type="application/json")
        if name and uid:
            user = User()
            user.first_name = name
            user.username = name + "@ust-global.com"
            user.Uid = uid
            user.save()
            for item in request.POST.getlist("filename[]"):
                format, imgstr = item.split(';base64,')
                ext = format.split('/')[-1]
                data = ContentFile(base64.b64decode(imgstr),
                                   name=name + "." + ext)  # You can save this as file instance.
                image_object = UserImages()
                image_object.image = data
                image_object.user_obj = user
                image_object.save()
            data1['result'] = "success"
            return HttpResponse(json.dumps(data1), content_type="application/json")
        else:
            data1['result'] = "Both fields are mandatory"
            return HttpResponse(json.dumps(data1), content_type="application/json")


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
        return JsonResponse({"success":"user deleted successfully"})

def export_data(self,request):
    print(request)
    response = HttpResponse(content_type='application/ms-excel')
    if request.GET.get("date"):
        date = request.GET.get("date")
        response['Content-Disposition'] = 'attachment; filename='+date+".xls"
    else:
        today = datetime.datetime.today().date().strftime("%d/%m/%Y")
        response['Content-Disposition'] = 'attachment; filename='+today+".xls"
    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('Users')

    # Sheet header, first row
    row_num = 0

    font_style = xlwt.XFStyle()
    font_style.font.bold = True
    font_style.num_format_str = 'dd/mm/yyyy'

    columns = ['Name', 'Uid', 'Attendence Status',"In-Time","Out-Time","Total Hours" ]

    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], font_style)

    # Sheet body, remaining rows
    font_style = xlwt.XFStyle()
    font_style.num_format_str = 'dd/mm/yyyy'

    url = 'http://127.0.0.1:8080/backend/dashboard'
    if request.GET.get("date") and request.GET.get("search"):
        q = self.request.GET.get('date')
        search = self.request.GET.get('search')
        date = datetime.datetime.strptime(q, "%Y-%m-%d").date()
        # PARAMS = {'date': date,"search":search}
        today = date
    elif request.GET.get("date"):
        q = self.request.GET.get('date')
        date = datetime.datetime.strptime(q, "%Y-%m-%d").date()
        # PARAMS = {'date': date}
        today = date
    elif request.GET.get("search"):
        search = self.request.GET.get('search')
        today = datetime.datetime.today().date()
        # PARAMS = {'search': q,"date":today}
    else:
        today = datetime.datetime.today().date()
    if search:
        logs = Logs.objects.filter(Q(user_obj__first_name__contains=search) | Q(user_obj__Uid__contains=search),
                                   date__date=today)
        users = list(User.objects.filter(Q(first_name__contains=search) | Q(Uid__contains=search)).values())
    else:
        logs = Logs.objects.filter(date__date=today)
        users = list(User.objects.values())
    # for log in logs:
    #     print(type(log.in_time))
    #     log.in_time = datetime.datetime.strptime(log.in_time,'%H:%M:%S')
    #     log.out_time = datetime.datetime.strptime(log.out_time,'%H:%M:%S')
    todays_user = []
    for user in users:
        if user["is_superuser"]:
            del user
    for log in logs:
        todays_user.append(log.user_obj.username)
    for user in users:
        if user["username"] in todays_user:
            for log in logs:
                if log.user_obj.username == user["username"]:
                    user.update({"in_time": log.in_time})
                    user.update({"out_time": log.out_time})
                    user.update({"total_hours": log.total_hours})
                    user.update({"status": "present"})
        else:
            for log in logs:
                if log.user_obj.username == user["username"]:
                    user.update({"in_time": "NA"})
                    user.update({"out_time": "NA"})
                    user.update({"total_hours": "NA"})
                    user.update({"status": "absent"})

    entries = ('email', 'username', 'password','id',"is_staff","is_superuser","is_active",'created','updated','timestampmodel_ptr_id',
               'last_login','profile_image','date_joined',"last_name")
    users = [{k: v for k, v in d.items() if k not in entries} for d in users]
    users = [tuple(user.values()) for user in users]
    print(users)

    # rows = ProductIn.objects.all().values_list('part_name', 'part_description', 'count')
    for user in users:
        row_num += 1
        for col_num in range(len(user)):
            ws.write(row_num, col_num, user[col_num], font_style)

    wb.save(response)
    return response

