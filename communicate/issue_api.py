import requests

import binascii
import os

url = "https://avc-api.azurewebsites.net/api/issue"
def encode_multipart_formdata(fields):
    boundary = binascii.hexlify(os.urandom(16)).decode('ascii')

    body = (
        "".join("--%s\r\n"
                "Content-Disposition: form-data; name=\"%s\"\r\n"
                "\r\n"
                "%s\r\n" % (boundary, field, value)
                for field, value in fields.items()) +
        "--%s--\r\n" % boundary
    )

    content_type = "multipart/form-data; boundary=%s" % boundary

    return body, content_type

from requests_toolbelt.multipart.encoder import MultipartEncoder
def send_issue(typeId,carId,location,des_issue,f):
    typeId = str(typeId)
    carId = str(carId)
    location = str(location)
    m = MultipartEncoder(
        fields={
            "TypeId": typeId,
            "CarId":carId,
            "Location": location,
            "Description":des_issue,
            "image":(f.name,f,'image/jpeg')
            }
        )
    headers = {'Content-Type':m.content_type}    
    response = requests.post(url,headers=headers, data = m)
    return response    

# with open('test.jpg','rb') as f:
#     response = send_issue(1, 1, 'location', 'des_issue',f)
#     print(response)
#     print(response.content)
#     print(response.status_code)


