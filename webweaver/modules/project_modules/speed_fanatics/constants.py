from webweaver.config import ROOT_DIR
import os

SPEED_FANATICS_SERVER = 'http://127.0.0.1:8000'
SPEED_FANATICS_HOSTNAME = '127.0.0.1'
SPEED_FANATICS_SSH_PORT = 22

URL_RECEIVER = 'http://127.0.0.1:8000/receiving/inventory/',
URL_RECEIVER = 'http://127.0.0.1:8000/receiving/images/'
SPEED_IMAGE_DIR = os.path.join(ROOT_DIR, 'media/speed_fanatics/images')
MIN_PRICE = 3  #the minimum price we will take as a product


# IMAGE_TRANSFER_TAR_FILE_NAME = '/tmp/product_images.tar.gz'
# IMAGE_TRANSFER_REMOTE_HOST = '127.0.0.1'
# IMAGE_TRANSFER_SSH_PORT = 22
