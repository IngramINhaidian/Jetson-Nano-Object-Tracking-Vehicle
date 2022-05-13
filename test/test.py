import xml.etree.ElementTree as ET
import os
   
sorce = 'C:/Users/Runping/Desktop/bishe/object-track/test/cola/label'  # 文件夹路径
# sorce = "C:\Users\Runping\Desktop\bishe\object-track\test\cola\label"
dir = os.listdir(sorce)

for i in range(len(dir)):
    tree = ET.parse(sorce + '/' + dir[i])
    rect = {}
    line = ""
    root = tree.getroot()
    # 路径信息
    for name in root.iter('path'):
        rect['path'] = name.text
    for ob in root.iter('object'):

        for bndbox in ob.iter('bndbox'):
            # for l in bndbox:
            #     print(l.text)
            # 坐标信息
            for xmin in bndbox.iter('xmin'):
                rect['xmin'] = xmin.text
            for ymin in bndbox.iter('ymin'):
                rect['ymin'] = ymin.text
            for xmax in bndbox.iter('xmax'):
                rect['xmax'] = xmax.text
            for ymax in bndbox.iter('ymax'):
                rect['ymax'] = ymax.text
            print(rect['xmin'] + ' ' + rect['ymin'] + ' ' + rect['xmax'] + ' ' + rect['ymax'])
            line = rect['xmin'] + ' ' + rect['ymin'] + ' ' + rect['xmax'] + ' ' + rect['ymax'] + " "
            # 文本信息
            for t in ob.iter('name'):
                print(t.text)

detections = darknet.detect_image(pack[0], pack[1], darknet_image, thresh=.25)
for label, confidence, bbox in detections:
    if label == "bottle":
        x, y, w, h = bbox
        center_x
        center_y

