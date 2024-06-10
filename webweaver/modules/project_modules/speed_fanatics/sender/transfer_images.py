import asyncio
import getpass
import hashlib
import logging
import os
import paramiko
import requests
from scp import SCPClient
import tarfile
from typing import Any

from webweaver.config import DEBUG
from webweaver.modules.project_modules.speed_fanatics.constants import (
    SPEED_IMAGE_DIR, 
    SPEED_FANATICS_SERVER, 
    SPEED_FANATICS_HOSTNAME,
    SPEED_FANATICS_SSH_PORT
)
from webweaver.modules.project_modules.speed_fanatics.models import (
    Supplier,
    ProductImage
)
from webweaver.modules.project_modules.speed_fanatics.sender.sender_base import SenderBase


logger = logging.getLogger('sending')
# logging.basicConfig(level=logging.DEBUG) # use this if SSH client bugging out


# Constants
IMAGE_TRANSFER_TAR_FILE_NAME = 'product_images.tar.gz'
IMAGE_TRANSFER_REMOTE_HOST = SPEED_FANATICS_HOSTNAME
IMAGE_TRANSFER_SSH_PORT = SPEED_FANATICS_SSH_PORT
SSH_KEY_PATH = "/home/baga/.ssh/image_transfer_key"
LOCAL_TARFILE_DIR = "/home/baga/webweaver/webweaver"
REMOTE_TARFILE_DIR = '/home/baga/speed_fanatics_store/speed_fanatics/tmp'
REMOTE_CONFIRM_ROUTE = f"{SPEED_FANATICS_SERVER}/receiving/images/confirm/"


class ImageSender(SenderBase):

    REMOTE_HOST             = IMAGE_TRANSFER_REMOTE_HOST
    PORT                    = IMAGE_TRANSFER_SSH_PORT  # port 22 by default
    TARFILE_NAME            = IMAGE_TRANSFER_TAR_FILE_NAME
    SSH_KEY_PATH            = SSH_KEY_PATH
    LOCAL_TARFILE_DIR       = LOCAL_TARFILE_DIR
    REMOTE_TARFILE_DIR      = REMOTE_TARFILE_DIR
    REMOTE_CONFIRM_ROUTE    = REMOTE_CONFIRM_ROUTE

    def __init__(self):
        self.ssh_client:paramiko.SSHClient = None
        self.username = None
        self.suppliers:list[Supplier] = []
        self.product_images:list[ProductImage] = []
        self.LOCAL_TARFILE_PATH = f"{self.LOCAL_TARFILE_DIR}/{self.TARFILE_NAME}"
        self.REMOTE_TARFILE_PATH = f"{self.REMOTE_TARFILE_DIR}/{self.TARFILE_NAME}"

    @classmethod
    async def send_data(cls):
        """This is essentially the main() function that runs when this module is loaded as a script."""
        await cls._db_connect()
        image_sender = cls()
        image_sender.suppliers = await image_sender._suppliers()
        image_sender.product_images = await image_sender._product_images()
        image_sender._create_tar_file()
        image_sender.username = image_sender._get_user()
        image_sender.ssh_client = image_sender._ssh_client()
        image_sender.transfer_file()
        image_sender.send_request_confirming_transfer()        
        # upon successful response, should then delete tar file and set product images to is_image_sent=True


    async def _suppliers(self) -> list[Supplier]:
        return await Supplier.filter(is_active=True)


    async def _product_images(self) -> list[ProductImage]:
        supplier_ids = [supplier.id for supplier in self.suppliers]
        return await ProductImage.filter(
            is_image_sent=False, 
            product__supplier__id__in=supplier_ids
        ).prefetch_related('product__supplier')


    def _file_name_to_product_name_mapping(self) -> dict[str, str]:
        """Maps image file name to product name. So receiver know which file to which product."""
        d = {}
        for product_image in self.product_images:
            print(product_image.file_name)
            d[product_image.file_name] = product_image.product.product_name 
        return d


    def _unserialized_data(self) -> dict[str, Any]:
        """Create the dict to be passed as JSON data to the receiver."""
        sha1 = self._calculate_sha1()
        file_name_to_product_name = self._file_name_to_product_name_mapping()
        return {
            'sha1' :sha1,
            'file_name_to_product_name': file_name_to_product_name,
        }

    def send_request_confirming_transfer(self):
        """Sends HTTP POST request to self.REMOTE_CONFIRM_ROUTE. This will then allow the receiver app to make the changes to it's
        own file system with regards to the product images.
        """
        try:
            res = requests.post(url=self.REMOTE_CONFIRM_ROUTE, json=self._unserialized_data())
        except Exception as e:
            msg = f"Exception type `{e.__class__.__name__}` raised when making POST request to `{self.REMOTE_CONFIRM_ROUTE}. Exception: {e}`"
            logger.error(msg, exc_info=True)
            raise
        if not res.ok:
            msg = f"`{res.status_code}` HTTP Status code received from route `{self.REMOTE_CONFIRM_ROUTE}`"
            logger.error(msg)


    def _calculate_sha1(self) -> str:
        """Get SHA-1 hash of the tar file or return an empty string"""
        sha1 = hashlib.sha1()
        try:
            with open(self.LOCAL_TARFILE_PATH, 'rb') as f:
                while chunk := f.read(8192):
                    sha1.update(chunk)
            return sha1.hexdigest()
        except Exception as e:
            msg = f"Exception type `{e.__class__.__name__}` raised during calculation of SHA-1 hash of local tarfile at path: `{self.LOCAL_TARFILE_PATH}`. {e}"
            logger.error(msg, exc_info=True)
            return ""

    def _delete_tar_file_if_exists(self):
        if os.path.exists(self.LOCAL_TARFILE_PATH):
            logger.info(f"Tar archive `{self.LOCAL_TARFILE_PATH}` already exists. Deleting...")
            os.remove(self.LOCAL_TARFILE_PATH)


    def _create_tar_file(self) -> tarfile.TarFile:
        """Pass this function a list of file paths and it will compress them into a tar arcive"""
        self._delete_tar_file_if_exists()
        logger.info(f"Compressing `{len(self.product_images)}` image files from `{len(self.suppliers)}` suppliers....")
        with tarfile.open(self.LOCAL_TARFILE_PATH, "w:gz") as tar:
            for product_image in self.product_images:
                tar.add(
                    name=f"{SPEED_IMAGE_DIR}/{product_image.file_name}",
                    arcname=product_image.file_name,
                )
        logger.info(f"Created tar archive at `{self.LOCAL_TARFILE_PATH}`")
        return tar

    def _get_user(self) -> str:
        if DEBUG:
            return 'baga'
        else:
            return input("Username: ")
    

    def _get_password(self) -> str:
        return getpass.getpass("Password: ")

    def transfer_file(self):
        """Use SCP to transfer the .tar.gz file to the remote host."""
        logger.info('Starting file transfer')
        try:
            with SCPClient(self.ssh_client.get_transport()) as scp:
                scp.put(files=[self.LOCAL_TARFILE_PATH], remote_path=self.REMOTE_TARFILE_PATH)
        except Exception as e:
            msg = f"SCP Client failed to put() due to the following error: {e}"
            logger.error(msg, exc_info=True)
            raise
        else:
            logger.info("File transfer complete. Created file on remote host SCP.")
            logger.info(f"Created file: {self.username}@{self.REMOTE_TARFILE_PATH}")

    def _ssh_client(self) -> paramiko.SSHClient:
        ssh_client = paramiko.SSHClient()
        # ssh_client.load_system_host_keys(filename=self.SSH_KEY_PATH)
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        pkey = paramiko.RSAKey.from_private_key_file(filename=self.SSH_KEY_PATH)
        try:
            ssh_client.connect(
                hostname=self.REMOTE_HOST,
                port=self.PORT,
                username=self.username,
                pkey=pkey,
                look_for_keys=False,  # Do not look for keys in the default SSH directory
                allow_agent=False     # Do not use keys from the SSH agent
            )
            return ssh_client
        except Exception as e:
            msg = f"paramiko SSH client failed to connect to the remote host `{self.REMOTE_HOST}` due to the following error: {e}"
            logger.error(msg, exc_info=True)
            raise



if __name__ == '__main__':
    asyncio.run(ImageSender.send_data())

