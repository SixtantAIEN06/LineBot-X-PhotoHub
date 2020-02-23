import os
import argparse
import xml.etree.ElementTree as ET
#from core.config import cfg
def convert_voc_annotation(data_path, data_type, anno_path, use_difficult_bbox=True):
    cfg_path="../data/classes/coco2.names"
    classes = []
    with open(cfg_path,'r') as f:
        for names in f.readlines():
            # classes.append(names.replace('\n','').replace(' ','_'))
            classes.append(names.replace('\n',''))

        print(classes)
    # file_path='/Users/User/tensorflow-yolov3/data/dataset/kangaroo-master/'+data_type+'/annots/'
    file_path=f'C:/dataset/cocodataset/2014to2017/{data_type}/Annotations/'
    filename=os.listdir(file_path)
    with open(anno_path, 'a') as f:
        for image_ind in os.listdir(file_path):
            image_ind=image_ind.replace('.xml','')
            print(image_ind)
            if image_ind=='.ipynb_checkpoints':
                continue
            image_path = os.path.join(data_path , data_type , 'JPEGImages', image_ind + '.jpg')
            annotation = image_path
            label_path = os.path.join(data_path , data_type , 'Annotations', image_ind + '.xml')
            root = ET.parse(label_path).getroot()
            objects = root.findall('object')
            img_size=root.findall('size')
            for size in img_size:
                width=float(size.find('width').text.strip())
                height=float(size.find('height').text.strip())
                print(width)
            for obj in objects:
                difficult = obj.find('difficult').text.strip()
                if (not use_difficult_bbox) and(int(difficult) == 1):
                    continue
                bbox = obj.find('bndbox')
                class_ind = classes.index(obj.find('name').text.lower().strip())
                xmin = bbox.find('xmin').text.strip()

                xmax = bbox.find('xmax').text.strip()

                ymin = bbox.find('ymin').text.strip()
                
                ymax = bbox.find('ymax').text.strip()

                annotation += ' ' + ','.join([xmin, ymin, xmax, ymax, str(class_ind)])
            print(annotation)
            f.write(annotation + "\n")
    return len(filename)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--data_path", default="C:/dataset/cocodataset/2014to2017")
    parser.add_argument("--train_annotation", default="C:/dataset/cocodataset/train.txt")
    parser.add_argument("--test_annotation",  default="C:/dataset/cocodataset/val.txt")
    flags = parser.parse_args()

    if os.path.exists(flags.train_annotation):os.remove(flags.train_annotation)
    if os.path.exists(flags.test_annotation):os.remove(flags.test_annotation)

    num1 = convert_voc_annotation(os.path.join(flags.data_path), 'train', flags.train_annotation, False)
    num3 = convert_voc_annotation(os.path.join(flags.data_path),  'val', flags.test_annotation, False)
    print('=> The number of image for train is: %d\tThe number of image for test is:%d' %(num1, num3))


