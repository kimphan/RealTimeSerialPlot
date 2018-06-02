import os


class FileManager:
    def __init__(self):
        super(FileManager).__init__()

    @staticmethod
    def create_dir(path):
        os.makedirs(path)

    @staticmethod
    def check_path(path=None):
        if path is not None:
            return os.path.isdir(path)
        return False

    def create_file(self,path,fname):
        if not self.check_path(path):
            self.create_dir(path)
        return open(os.path.join(path, fname+'.csv'),'a')
