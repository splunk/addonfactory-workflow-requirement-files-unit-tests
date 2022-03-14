import os


def return_folder_contents(input_folder):
    file_list = []
    for dirpath, dirs, files in os.walk(input_folder):
        if not os.listdir(dirpath):
            print("No files in the directory.")
            exit(1)
        for filename in files:
            fname = os.path.join(dirpath, filename)
            if fname.endswith(".log") or fname.endswith(".xml"):
                file_list.append(fname)
            else:
                print(f"invalid file extension file {filename}")
                exit(1)
    return file_list
