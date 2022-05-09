import os
import subprocess

command_path = r"T:\public\NoamCam\ffmpeg\ffmpeg\bin"
path = r"T:\public\NoamCamCodeCurrent\ninthofmay\Server\Video\64_00_6a_42_4a_b1_2022_05_09"

def extract_audio(videos_paths,output):
    command = f"ffmpeg -i \"concat:{videos_paths}\" -c copy {path}\\connected.avi"
    subprocess.call(command,shell=True)


if __name__ == '__main__':

    os.chdir(command_path)

    files = ""
    for file in os.listdir(path):
        if file.endswith(".avi"):
            files += (f"{path}\\{file}" + "|")

    if files.endswith("|"):
        files = files[:-1]

    # print(files)

    # os.system(f"ffmpeg -i \"concat:{files}\" -c copy {path}\\connected.avi")
    # print(f"ffmpeg -i \"concat:{files}\" -c copy {path}\\connected.avi")

    extract_audio(files, f'{path}\\connected.avi')
