# Speed-Detection-System
The repo use python to provide a GUI that allows users to import a video and set the speed limits. Once the video is imported, the system tracks the moving objects in the video and estimates their speed. If the speed of an object exceeds the speed limits, the system alerts the user.

![result](https://github.com/chunbaobao/Speed-Detection-System/blob/main/demo/result.png)
## Requirements
- PyQt5
- OpenCV
- NumPy

## Installation
Use the package manager conda to install the requirements:
```
git clone https://github.com/chunbaobao/Speed-Detection-System
conda env create -f environment.yml
```

## Usage
To use this system, run the following command:
```
conda activate newcv
cd ./scr
python main.py
```
clike the "导入视频" to import the video you want to detect, and then click the "开始检测" button to start detecting.
