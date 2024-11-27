import os
import shutil
def exec(dir_path):
    # Check if the directory exists
    print(f'Create directory: {dir_path}')
    if os.path.exists(dir_path):
        # If it exists, remove all its contents
        for filename in os.listdir(dir_path):
            file_path = os.path.join(dir_path, filename)
            try:
                # ディレクトリの場合も削除する
                if os.path.isfile(file_path):
                    os.remove(file_path)
                    
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
                    
                print(f'Deleted {file_path}')
            except Exception as e:
                print(f'Failed to delete {file_path}. Reason: {e}')
    else:
        # If it doesn't exist, create the directory
        os.makedirs(dir_path)
