import logging
import os
from pyunsplash import PyUnsplash
import urllib.request
import ssl
from werkzeug.utils import secure_filename
from tqdm import tqdm
from PIL import Image

ssl._create_default_https_context = ssl._create_unverified_context

api_key = os.environ.get("UNSPLASH_ACCESS_KEY")
print(api_key)

# instantiate PyUnsplash object
py_un = PyUnsplash(api_key=api_key)

full_photo_dir='assets/photo_assets/images/fulls/'
thumb_photo_dir='assets/photo_assets/images/thumbs/'
md_files_dir='_photos/'

if os.path.exists(md_files_dir):
    os.system("rm -rf "+md_files_dir)
    os.makedirs(md_files_dir)


def crop_resize(image, size, ratio):
    # crop to ratio, center
    w, h = image.size
    if w > ratio * h: # width is larger then necessary
        x, y = (w - ratio * h) // 2, 0
    else: # ratio*height >= width (height is larger)
        x, y = 0, (h - w / ratio) // 2
    image = image.crop((x, y, w - x, h - y))

    # resize
    if image.size > size: # don't stretch smaller images
        image.thumbnail(size, Image.ANTIALIAS)
    return image

this_user = py_un.user('mariganeshkumar', w=100, h=100)
page=0
while True:
    page=page+1
    photos = this_user.photos(per_page=10,page=page)
    photos_in_page=0
    for photo in tqdm(photos.entries):
        photos_in_page += 1
        photo.refresh()
        photo_filename=secure_filename(photo.id+'.jpg')
        full_photo_path = full_photo_dir+photo_filename
        thumb_photo_path = thumb_photo_dir+photo_filename
        if not os.path.exists(full_photo_path):
            urllib.request.urlretrieve(photo.body['urls']['full'],full_photo_path)
        if not os.path.exists(thumb_photo_path):
            image = crop_resize(Image.open(full_photo_path), (480,300), 1.6)
            image.save(thumb_photo_path)

        description = photo.body['description'] if photo.body['description']!= None else ""
        title = photo.body['location']['title'] if photo.body['location']['title']!=None else ""
        md_file_name =  secure_filename(title+"_"+str(photo.id)+".md")
        print(md_file_name)  
        #print(photo.id, photo.body['description'],  photo.body['urls']['full'], photo.body['urls']['thumb'], photo.body['location']['title'])
        #print(photo.link_download)
        with open(md_files_dir+md_file_name,"w") as f:
            f.write("---\n")
            if title != "":
                f.write("title: "+title+"\n")
            else:
                f.write("title: "+photo.id+"\n")
            f.write("image: /"+full_photo_path+"\n")
            f.write("thumbnail: /"+thumb_photo_path+"\n")
            f.write("caption: "+description+"\n")
            f.write("---\n")
        
    if photos_in_page <10:
        break