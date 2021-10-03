import requests
import shutil
import time
def download_file(url,path_to_save):
    # local_filename = url.split('/')[-1]
    with requests.get(url, stream=True) as r:
        with open(path_to_save, 'wb') as f:
            shutil.copyfileobj(r.raw, f)
    return path_to_save

def check_version(new_version_id):
    with open('config/model_version.txt','r') as f:
        old_version_id = int(f.readline())
        new_version_id = int(new_version_id)
    if old_version_id != new_version_id:
        return False
    else: 
        return True

def write_new_version_into_file(new_version_id):
    with open('config/model_version.txt','w+') as f:
        f.writelines(str(new_version_id))

def download_config(url_config):
    name_save = "config/config_down.json"
    download_file(url_config,name_save)
    time.sleep(0.1)
    fix_required_config(name_save)



def fix_required_config(name_save):
    with open(name_save,'r') as f:
        content = f.readline()[:-1]
    with open('config/fix_rq.txt','r') as f:
        add_info = f.readline()
    with open(name_save,'w+') as f:
        f.writelines(content+add_info)

def download_model(model_config):
    name_save = "sign_detect/yolo_tpu/model/model_download.tflite"
    download_file(model_config,name_save)
