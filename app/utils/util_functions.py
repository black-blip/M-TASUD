class UtilFunctions():
    
    def write_file(self, filename, fileopenmode='w', file_content=""):
        with open(filename, fileopenmode) as file_to_write:
            file_to_write.write(file_content)