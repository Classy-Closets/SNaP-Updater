

#!/usr/bin/python3

"""Sample script for uploading to Sketchfab using the V3 API and the requests library."""
import bpy
from snap import sn_paths
import os
from bpy.types import Operator
from bpy.props import (StringProperty,
                       BoolProperty,
                       EnumProperty,
                       IntProperty)
from . import pm_utils
import json
from time import sleep
import random
from collections import Counter
# http://docs.python-requests.org/en/latest
import requests
from requests.exceptions import RequestException

##
# Uploading a model to Sketchfab is a two step process
#
# 1. Upload a model. If the upload is successful, the API will return
#    the model's uid in the `Location` header, and the model will be placed in the processing queue
#
# 2. Poll for the processing status
#    You can use your model id (see 1.) to poll the model processing status
#    The processing status can be one of the following:
#    - PENDING: the model is in the processing queue
#    - PROCESSING: the model is being processed
#    - SUCCESSED: the model has being sucessfully processed and can be view on sketchfab.com
#    - FAILED: the processing has failed. An error message detailing the reason for the failure
#              will be returned with the response
#
# HINTS
# - limit the rate at which you poll for the status (once every few seconds is more than enough)
##


SKETCHFAB_URL = 'https://sketchfab.com'
SKETCHFAB_API_URL = 'https://api.sketchfab.com/v3'
#API_TOKEN = 'gAAAAABl-3YLXF_ZGrKVzF-qrchlFSOTXEOtI9y6wn3bW_usSNcm3riKp0BG5z7V5_2HjWMwkRBM5sv0ojs8uT7fWbjQ0tYNw5Grmr_Ght3k-b4W8qBSMEtWVwAk-7Jpwu7x5TiTBggl'  #Iconica
API_TOKEN = 'gAAAAABl-3VVSde7nwCsmhy1srKZp6tBeJnbifG_BJ7PQ9SBELjhsbJqoV33Pzz7KwVZLLSyK5g3DdaWNy48sy69fddBYnjrQdWbdvaJh7dI54Mm9g7wH4frX3zJrqEK-wRFcM2tey2I'  #Tyler
MAX_RETRIES = 50
MAX_ERRORS = 10
RETRY_TIMEOUT = 5  # seconds

#  API key status values should be 'active', 'passive', 'closed'
API_KEYS = [
        ("gAAAAABl-3YLXF_ZGrKVzF-qrchlFSOTXEOtI9y6wn3bW_usSNcm3riKp0BG5z7V5_2HjWMwkRBM5sv0ojs8uT7fWbjQ0tYNw5Grmr_Ght3k-b4W8qBSMEtWVwAk-7Jpwu7x5TiTBggl", "passive"), # Iconica Test
        ("gAAAAABl-3VVSde7nwCsmhy1srKZp6tBeJnbifG_BJ7PQ9SBELjhsbJqoV33Pzz7KwVZLLSyK5g3DdaWNy48sy69fddBYnjrQdWbdvaJh7dI54Mm9g7wH4frX3zJrqEK-wRFcM2tey2I", "active"), # Classy 1
        ("gAAAAABmGr6YoJ-yJKeSm8F2lKPvsJQTwh3kR86pwUppsxvdk1wDLm9rLMHzf1oOIb5omP1-Kd_X4n5GF86BNx1wgmGZ-1dSzIU9YyRVf_PTOjTnvQbv_HFOP-VhXF-7jCuNUv7mOYZr", "active"), # Classy 2
    ]


def get_next_api_key(self):
    new_key = None
    room_keys = []

    for room in self.project.rooms:
        if room.prop_3d_exported_acct != "":
            room_keys.append(room.prop_3d_exported_acct)

    if len(room_keys) == 0:  # First room in project to be exported...
        # random_index = random.randint(0, len(API_KEYS)-1)
        # print("First uploaded room in project, using random key:", API_KEYS[random_index])
        # new_key, status = API_KEYS[random_index]
        api_keys_vals = [key for key, status in API_KEYS if status == 'active']
        new_key = random.choice(api_keys_vals)
    else:
        api_keys_vals = [key for key, status in API_KEYS if status == 'active']
        usage_count = Counter(room_keys)
        min_count = float('inf')
        
        # Iterate through the API keys and find the one with the minimum count
        for key in api_keys_vals:
            count = usage_count.get(key, 0)  # Get the count for the current key
            if count < min_count:
                min_count = count
                new_key = key

    print("New Key:", new_key)

    return new_key

def get_api_key_status(self, my_key):
    key_status = "closed"

    for key, status in API_KEYS:
        if key == my_key:
            print("Status of my_key:", status)
            key_status = status
    return key_status    

class SNAP_OT_Update_Room_In_Sketchfab(Operator):
    bl_idname = "project_manager.update_room_in_sketchfab"
    bl_label = "Update Room in Sketchfab"
    bl_description = ""

    project = None
    project_room = None
    api_token = ""
    is_new_token = False
    active_room: StringProperty(name="Active Room", description="Active Room", default="")
    http_method: StringProperty(name="HTTP Method", description="Http Method", default="")

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        print("starting...")
        self.project = context.window_manager.sn_project.get_project()

        for room in self.project.rooms:
            # print("project.room.name=", room.name.lower())
            if room.name.lower() == self.active_room.lower():
                # print("room match found:",room.name.lower())
                self.project_room = room
                break

        if self.project_room:
            if room.prop_3d_exported_acct != "":
                if get_api_key_status(self, room.prop_3d_exported_acct) == "closed":
                    self.api_token = get_next_api_key(self)
                    self.is_new_token = True
                else:
                    self.api_token = room.prop_3d_exported_acct
            else:
                self.api_token = get_next_api_key(self)


            # if self.http_method != "DELETE":
                # if self.project_room.prop_3d_exported_url == "":
                #     self.http_method = "POST"
                # elif self.project_room.prop_3d_exported_url != "":
                #     self.http_method = "PUT"
            if self.http_method != "DELETE":
                if self.project_room.prop_3d_exported_uid == "" or self.is_new_token == True:
                    self.http_method = "POST"
                else:
                    self.http_method = "PUT"
        
        self.process_request()

        print("finished...")
        return{'FINISHED'}


    def process_request(self):
        """
        Send http requests to sketchfab api.
        Model endpoint only accepts formData as we upload a file.
        """
        # model_file = os.path.join(self.project.dir_path, "Proposal", self.active_room.replace(" ","_") + "-3d_export.blend")
        # print("model_file=",model_file)
        # Optional parameters
        data = {
            'name': self.active_room,
            'description': self.active_room, 
            'tags': [],  # Array of tags,
            'categories': [],  # Array of categories slugs,
            'license': 'by',  # License slug,
            'private': 1,  # requires a pro account,
            'password': '',  # requires a pro account,
            'isPublished': True,  # Model will be on draft instead of published,
            'isInspectable': True,  # Allow 2D view in model inspector
        }

        print('Processing Request...')

        # if self.http_method == "DELETE":
        #     model_endpoint = f'{SKETCHFAB_API_URL}/models/{self.project_room.prop_3d_exported_uid}'
        #     payload = self.get_request_payload(data=data)
        #     print("DELETE model_endpoint=",model_endpoint)
        #     response = requests.delete(model_endpoint, **payload)
        #     if response.status_code != requests.codes.no_content:
        #         print(f'Delete failed with error: {response.json()}')
        #         # return  -- Allow code to continue even if delete fails for now, so we do clear prop_3d_exported props
        # else:

        # If we are deleting, upload placeholder model file, else upload actual model

        if self.http_method != "DELETE":
            model_file = os.path.join(self.project.dir_path, "Proposal", self.active_room.replace(" ","_") + "-3d_export.glb")
        else:
            model_file = os.path.join(sn_paths.ROOT_DIR, 'library_manager', 'empty_room.blend')
        print("model_file=",model_file)

        with open(model_file, 'rb') as file_:
            files = {'modelFile': file_}
            payload = self.get_request_payload(data=data, files=files)

            try:
                if self.http_method == "POST":
                    model_endpoint = f'{SKETCHFAB_API_URL}/models'
                    print("POST model_endpoint=",model_endpoint)
                    response = requests.post(model_endpoint, **payload)
                    if response.status_code != requests.codes.created:
                        print(f'Upload failed with error: {response.json()}')
                        return
                elif self.http_method == "PUT":
                    model_endpoint = f'{SKETCHFAB_API_URL}/models/{self.project_room.prop_3d_exported_uid}'
                    print("PUT model_endpoint=",model_endpoint)
                    response = requests.put(model_endpoint, **payload)
                    if response.status_code != requests.codes.no_content:
                        print(f'Reupload failed with error: {response.json()}')
                        return  
                elif self.http_method == "DELETE":
                    model_endpoint = f'{SKETCHFAB_API_URL}/models/{self.project_room.prop_3d_exported_uid}'
                    print("delete via PUT model_endpoint=",model_endpoint)
                    response = requests.put(model_endpoint, **payload)
                    if response.status_code != requests.codes.no_content:
                        print(f'Reupload failed with error: {response.json()}')
                        # return  -- Allow code to continue even if delete fails for now, so we do clear prop_3d_exported props
                else:
                    print("Invalid HTTP Method")
                    return
            
            except RequestException as exc:
                print(f'An error occured: {exc}')
                return


        # /// Set project room_props based on operation...

        if self.http_method == "POST":
            # model_url = response.headers['Location']
            uid = response.json()["uid"]
            model_url = SKETCHFAB_URL + "/models/" + uid
            
            self.project_room.prop_3d_exported = "True"
            self.project_room.prop_3d_exported_url = model_url
            self.project_room.prop_3d_exported_uid = uid
            self.project_room.prop_3d_exported_acct = self.api_token
                
            print("project_room.prop_3d_exported_url=", self.project_room.prop_3d_exported_url)
            print("project_room.prop_3d_exported_uid=", self.project_room.prop_3d_exported_uid)
                

            print('Upload successful. Your model is being processed.')
            print(f'Once the processing is done, the model will be available at: {model_url}')
        
        elif self.http_method == "DELETE":
            self.project_room.prop_3d_exported = ""
            self.project_room.prop_3d_exported_url = ""
            # self.project_room.prop_3d_exported_uid = ""
            # self.project_room.prop_3d_exported_acct = ""
            print("project_room.prop_3d_exported_url=", self.project_room.prop_3d_exported_url)
            print("project_room.prop_3d_exported_uid=", self.project_room.prop_3d_exported_uid)
        return 

    def get_request_payload(self, *, data=None, files=None, json_payload=False):
        """Helper method that returns the authentication token and proper content type depending on
        whether or not we use JSON payload."""
        data = data or {}
        files = files or {}
        headers = {'Authorization': f'Token {pm_utils.decode(self.api_token)}'}

        if json_payload:
            headers.update({'Content-Type': 'application/json'})
            data = json.dumps(data)

        return {'data': data, 'files': files, 'headers': headers}


class SNAP_OT_Upload_Sketchfab_Model(Operator):
    bl_idname = "project_manager.upload_sketchfab_model"
    bl_label = "Upload Model to Sketchfab"
    bl_description = ""

    project = None


    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        self.project = context.window_manager.sn_project.get_project()
        ###################################
        # Uploads, polls and patch a model
        ###################################
        print("starting...")
        # if __name__ == '__main__':
        if model_url := self.upload():
            if self.poll_processing_status(model_url):
                self.patch_model(model_url)
                self.patch_model_options(model_url)

        print("finished...")
        return{'FINISHED'}
    

    def get_request_payload(self, *, data=None, files=None, json_payload=False):
        """Helper method that returns the authentication token and proper content type depending on
        whether or not we use JSON payload."""
        data = data or {}
        files = files or {}
        headers = {'Authorization': f'Token {pm_utils.decode(API_TOKEN)}'}

        if json_payload:
            headers.update({'Content-Type': 'application/json'})
            data = json.dumps(data)

        return {'data': data, 'files': files, 'headers': headers}


    def upload(self):
        """
        POST a model to sketchfab.
        This endpoint only accepts formData as we upload a file.
        """
        model_endpoint = f'{SKETCHFAB_API_URL}/models'
        print("model_endpoint=",model_endpoint)
        # Mandatory parameters
       
        # model_file = './data/pikachu.zip'  # path to your model
        model_file = os.path.join(self.project.dir_path, "Proposal", "closet_1-3d_export.blend")
        print("model_file=",model_file)
        # Optional parameters
        data = {
            'name': 'A Bob model',
            'description': 'This is a bob model I made with love and passion',
            'tags': ['bob', 'character', 'video-games'],  # Array of tags,
            'categories': ['people'],  # Array of categories slugs,
            'license': 'by',  # License slug,
            'private': 1,  # requires a pro account,
            'password': '',  # requires a pro account,
            'isPublished': True,  # Model will be on draft instead of published,
            'isInspectable': True,  # Allow 2D view in model inspector
        }

        print('Uploading...')

        with open(model_file, 'rb') as file_:
            files = {'modelFile': file_}
            payload = self.get_request_payload(data=data, files=files)

            try:
                response = requests.post(model_endpoint, **payload)
            except RequestException as exc:
                print(f'An error occured: {exc}')
                return

        if response.status_code != requests.codes.created:
            print(f'Upload failed with error: {response.json()}')
            return

        # Should be https://api.sketchfab.com/v3/models/XXXX
        model_url = response.headers['Location']
        print('Upload successful. Your model is being processed.')
        print(f'Once the processing is done, the model will be available at: {model_url}')

        return model_url


    def poll_processing_status(self, model_url):
        """GET the model endpoint to check the processing status."""
        errors = 0
        retry = 0

        print('Start polling processing status for model')

        while (retry < MAX_RETRIES) and (errors < MAX_ERRORS):
            print(f'Try polling processing status (attempt #{retry})...')

            payload = self.get_request_payload()

            try:
                response = requests.get(model_url, **payload)
            except RequestException as exc:
                print(f'Try failed with error {exc}')
                errors += 1
                retry += 1
                continue

            result = response.json()

            if response.status_code != requests.codes.ok:
                print(f'Upload failed with error: {result["error"]}')
                errors += 1
                retry += 1
                continue

            processing_status = result['status']['processing']

            if processing_status == 'PENDING':
                print(f'Your model is in the processing queue. Will retry in {RETRY_TIMEOUT} seconds')
                retry += 1
                sleep(RETRY_TIMEOUT)
                continue
            elif processing_status == 'PROCESSING':
                print(f'Your model is still being processed. Will retry in {RETRY_TIMEOUT} seconds')
                retry += 1
                sleep(RETRY_TIMEOUT)
                continue
            elif processing_status == 'FAILED':
                print(f'Processing failed: {result["error"]}')
                return False
            elif processing_status == 'SUCCEEDED':
                print(f'Processing successful. Check your model here: {model_url}')
                return True

            retry += 1

        print('Stopped polling after too many retries or too many errors')
        return False


    def patch_model(self, model_url):
        """
        PATCH the model endpoint to update its name, description...
        Important: The call uses a JSON payload.
        """

        payload = self.get_request_payload(data={'name': 'A super Bob model'}, json_payload=True)

        try:
            response = requests.patch(model_url, **payload)
        except RequestException as exc:
            print(f'An error occured: {exc}')
        else:
            if response.status_code == requests.codes.no_content:
                print('PATCH model successful.')
            else:
                print(f'PATCH model failed with error: {response.content}')


    def patch_model_options(self, model_url):
        """PATCH the model options endpoint to update the model background, shading, orienration."""
        data = {
            'shading': 'shadeless',
            'background': '{"color": "#FFFFFF"}',
            # For axis/angle rotation:
            'orientation': '{"axis": [1, 1, 0], "angle": 34}',
            # Or for 4x4 matrix rotation:
            # 'orientation': '{"matrix": [1, 0, 0, 0, 0, -1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1]}'
        }
        payload = self.get_request_payload(data=data, json_payload=True)
        try:
            response = requests.patch(f'{model_url}/options', **payload)
        except RequestException as exc:
            print(f'An error occured: {exc}')
        else:
            if response.status_code == requests.codes.no_content:
                print('PATCH options successful.')
            else:
                print(f'PATCH options failed with error: {response.content}')


classes = (
    SNAP_OT_Update_Room_In_Sketchfab,
    SNAP_OT_Upload_Sketchfab_Model,
   
)

register, unregister = bpy.utils.register_classes_factory(classes)