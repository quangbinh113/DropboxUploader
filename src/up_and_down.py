import requests
import pandas as pd
import os
import sys
import dropbox
import dropbox.files
import dropbox.sharing

class UpAndDown(object):
    """
    UpAndDown is a class that handles upload or download files to dropbox,
    Then it will get the dropbox's urls of those files and store to user local
    """
    def __init__(self, token: str=None, rootdir: str=None) -> None:
        self.token = token      
        self.rootdir = '/' + rootdir
        self.dbx = dropbox.Dropbox(self.token)

        """
        Check if the rootdir exists in dropbox, if not, create it.
        If the rootdir already exists, raise exception.
        """
        list_dir = self.dbx.files_list_folder('')
        for entry in list_dir.entries:
            if entry.name == rootdir:
                raise Exception(f'{rootdir} already exists in dropbox, please change another name.')
        try:
            # create rootdir in dropbox
            self.dbx.files_get_metadata(self.rootdir)
        except dropbox.exceptions.ApiError as e:
            print(e)


    def upload_one(self, file_dir: str=None) -> None:
        """
        Upload one file to rootdir in dropbox.
        ----------
        Args:
            file_dir: str -> The file directory of the file to upload.
        Returns:
            None
        """

        with open(file_dir, 'rb') as f:
            file_name = os.path.basename(file_dir)
            db_name = f'{self.rootdir}/{file_name}'
            self.dbx.files_upload(f.read(), f'{self.rootdir}/{file_name}')
            print(f'    Uploaded {file_name} to {self.rootdir}')
    

    def upload_all(self, local_folder: str=None) -> None:
        """
        Upload all files in local_folder to rootdir in dropbox.
        ----------
        Args:
            local_folder: str -> The local folder to upload all files from.
        Returns:
            None
        """
        if not os.path.exists(local_folder):
            print(local_folder, 'does not exist on your filesystem')
            sys.exit(1)

        print(f'Start uploading all files in {local_folder}...')
        for file in os.listdir(local_folder):
            file_dir = os.path.join(local_folder, file)
            self.upload_one(file_dir)
        
        print(f'Finished upload all files in {local_folder} folder.')

    
    def upload_urls(self, urls_contain_file_path: str=None) -> None:
        """
        Request all contents from each url in urls_contain_file_path and save to a folder in local
        Then upload all files in that folder to rootdir in dropbox.
        ----------
        Args:
            urls_contain_file_path: str -> The file path of the file containing all urls.
        Returns:
            None
        """
        # Get the directory path of the DataFrame file
        folder_name = os.path.splitext(urls_contain_file_path)[0]

        if not os.path.exists(folder_name):
            os.makedirs(folder_name)

        # Read the file into a DataFrame or CSV reader, assuming the URL is in the first column
        _, ext = os.path.splitext(urls_contain_file_path)
        if ext == '.xlsx':
            df = pd.read_excel(urls_contain_file_path)
        elif ext == '.csv':
            df = pd.read_csv(urls_contain_file_path)
        else:
            print("Unsupported file format. Use .xlsx or .csv.")
            return

        print(f"Start downloading all images from {urls_contain_file_path}...")
        for index, row in df.iterrows():
            image_name = row.iloc[1]  # Use the index to access the first column
            image_url = row.iloc[3]  # Use the index to access the second column

            # Construct the full file path for the image in the folder
            image_extension = os.path.splitext(image_url)[1]
            image_filename = f"{image_name}{image_extension}"
            image_path = os.path.join(folder_name, image_filename)

            try:
                # Send a GET request to the URL to download the image
                response = requests.get(image_url)
                if response.status_code == 200:
                    with open(image_path, 'wb') as f:
                        f.write(response.content)
                    print(f"    Downloaded: {image_filename}")
                else:
                    print(f"    Failed to download: {image_url} (Status Code: {response.status_code})")
            except Exception as e:
                print(f"Error while downloading {image_url}: {str(e)}")
        
        self.upload_all(folder_name)


    def download_one(self, file_dir: str=None) -> None:
        """
        Download one file from dropbox.
        ----------
        Args:
            file_dir: str -> The file directory of the file to download.
        Returns:
            None
        """
        file_name = os.path.basename(file_dir)
        db_name = f'{self.rootdir}/{file_name}'
        self.dbx.files_download_to_file(file_dir, db_name)
        print(f'    Downloaded {file_name} from {self.rootdir}')
    

    def download_all(self, local_folder: str=None) -> None:
        """
        Download all files in rootdir from dropbox to local_folder.
        ----------
        Args:
            local_folder: str -> The local folder to download all files to.
        Returns:
            None
        """
        if not os.path.exists(local_folder):
            os.makedirs(local_folder)

        print(f'Start downloading all files from {self.rootdir}...')
        for file in self.dbx.files_list_folder(self.rootdir).entries:
            file_dir = os.path.join(local_folder, file.name)
            self.download_one(file_dir)
        
        print(f'Finished download all files from {self.rootdir} folder.')


    def get_new_urls(self) -> pd.DataFrame:
        """
        Get all urls from dropbox_folder and save to an excel file.
        The execl file will contain 2 columns:
            -> Image_Name: The name of the image file.
            -> Image_New_URL: The new url of the image file.
        ----------
        Args:
            None
        Returns:
            pd.DataFrame -> A DataFrame containing all names and urls.
        """
        dropbox_folder = self.rootdir
        print(f'Start getting all urls from {dropbox_folder}...')
        try:
            # List files in the specified folder
            files = self.dbx.files_list_folder(dropbox_folder).entries
            assert len(files) > 0, f"Folder '{dropbox_folder}' is empty."

            # Get download links for image files in the folder
            data = {'Image_Name': [], 'Image_New_URL': []}
            for file in files:
                if isinstance(file, dropbox.files.FileMetadata):
                    file_name, file_extension = file.name.rsplit('.', 1)
                    if file_extension.lower() in ('jpg', 'jpeg', 'png', 'gif'):
                        shared_link = self.dbx.sharing_create_shared_link(file.path_display)
                        image_url = shared_link.url
                        data['Image_Name'].append(file_name)
                        data['Image_New_URL'].append(image_url)

            output = pd.DataFrame(data)
            print(f'Finished getting all urls from {dropbox_folder} folder.')
            return output

        except dropbox.exceptions.ApiError as e:
            print(f"Dropbox API error: {e}")
            return None
        
    
    def up_and_down(self, dir: str=None) -> pd.DataFrame:
        """
        Function to upload all files in dir to dropbox, 
        then get all urls from dropbox and save to dir.
        ----------
        Args:
            dir: str -> The directory to upload all files from and save all urls to.
        Returns:
            pd.DataFrame -> A DataFrame containing all names and urls.
        """
        def _is_dir(dir: str=None) -> bool:
            _, ext = os.path.splitext(dir)
            if ext == '':
                return True
            else:
                return False
        
        if not os.path.exists(dir):
            print(dir, 'does not exist on your filesystem')
            sys.exit(1)
        
        if _is_dir(dir):
            self.upload_all(dir)    
            output = self.get_new_urls()
        else:
            self.upload_urls(dir)
            output = self.get_new_urls()
        return output



if __name__ == "__main__":
    # unit test
    TOKEN = 'sl.BoPRD1evraITzyHlK0vlTrfZ9Nq3f7hc7tOfh_1Mx8ldx-cj0OMjSw3mDKaLj6ALiHkvSvPgaA1DLSwp2S8n4xREDmlG0h0yB4cfQLUCjMdBA4KaHoegAA7Jrh5jJqXB6IJaRRq2pKrdmR9zlUCB'
    loader = UpAndDown(token=TOKEN, rootdir='__test_class_final_____')

    loader.upload_one(file_dir=r"E:\Code\frelance\Change_URL\PythonDropboxUploader\small_test_file.txt")
    loader.upload_all(local_folder=r"E:\Code\frelance\Change_URL\PythonDropboxUploader\test_")
    loader.upload_urls(urls_contain_file_path=r"E:\Code\frelance\Change_URL\PythonDropboxUploader\test_\halo1.csv")
    
    data_ = loader.get_new_urls()
    data_.to_excel(r"E:\Code\frelance\Change_URL\PythonDropboxUploader\test_\test.xlsx", index=False)
    data_.to_csv(r"E:\Code\frelance\Change_URL\PythonDropboxUploader\test_\test.csv", index=False)

    # system test
    output = loader.up_and_down(dir=r"C:/Users/binh.truong/Code/change_url/DropboxUploader/test_/halo1.csv")
    output.to_excel(r"C:\Users\binh.truong\Code\change_url\DropboxUploader\test_\halo1.xlsx", index=False)