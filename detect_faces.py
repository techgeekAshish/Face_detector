import numpy as np
import cv2
from keras.models import Model, Sequential
from keras.layers import Input, Convolution2D, ZeroPadding2D, MaxPooling2D, Flatten, Dense, Dropout, Activation
from PIL import Image
from keras.preprocessing.image import load_img, save_img, img_to_array
from keras.applications.imagenet_utils import preprocess_input
from keras.preprocessing import image
import matplotlib.pyplot as plt
from os import listdir

# -----------------------

color = (67, 67, 67)
face_cascade = cv2.CascadeClassifier('D:/Ashish/face_detection/haarcascade_frontalface_default.xml')

def preprocess_image(image_path):
    img = load_img(image_path, target_size=(224, 224))
    img = img_to_array(img)
    img = np.expand_dims(img, axis=0)
    # preprocess_input normalizes input in scale of [-1, +1]. You must apply same normalization in prediction.
    # Ref: https://github.com/keras-team/keras-applications/blob/master/keras_applications/imagenet_utils.py (Line 45)
    img = preprocess_input(img)
    return img

def loadVggFaceModel():
    model = Sequential()
    model.add(ZeroPadding2D((1, 1), input_shape=(224, 224, 3)))
    model.add(Convolution2D(64, (3, 3), activation='relu'))
    model.add(ZeroPadding2D((1, 1)))
    model.add(Convolution2D(64, (3, 3), activation='relu'))
    model.add(MaxPooling2D((2, 2), strides=(2, 2)))

    model.add(ZeroPadding2D((1, 1)))
    model.add(Convolution2D(128, (3, 3), activation='relu'))
    model.add(ZeroPadding2D((1, 1)))
    model.add(Convolution2D(128, (3, 3), activation='relu'))
    model.add(MaxPooling2D((2, 2), strides=(2, 2)))

    model.add(ZeroPadding2D((1, 1)))
    model.add(Convolution2D(256, (3, 3), activation='relu'))
    model.add(ZeroPadding2D((1, 1)))
    model.add(Convolution2D(256, (3, 3), activation='relu'))
    model.add(ZeroPadding2D((1, 1)))
    model.add(Convolution2D(256, (3, 3), activation='relu'))
    model.add(MaxPooling2D((2, 2), strides=(2, 2)))

    model.add(ZeroPadding2D((1, 1)))
    model.add(Convolution2D(512, (3, 3), activation='relu'))
    model.add(ZeroPadding2D((1, 1)))
    model.add(Convolution2D(512, (3, 3), activation='relu'))
    model.add(ZeroPadding2D((1, 1)))
    model.add(Convolution2D(512, (3, 3), activation='relu'))
    model.add(MaxPooling2D((2, 2), strides=(2, 2)))

    model.add(ZeroPadding2D((1, 1)))
    model.add(Convolution2D(512, (3, 3), activation='relu'))
    model.add(ZeroPadding2D((1, 1)))
    model.add(Convolution2D(512, (3, 3), activation='relu'))
    model.add(ZeroPadding2D((1, 1)))
    model.add(Convolution2D(512, (3, 3), activation='relu'))
    model.add(MaxPooling2D((2, 2), strides=(2, 2)))

    model.add(Convolution2D(4096, (7, 7), activation='relu'))
    model.add(Dropout(0.5))
    model.add(Convolution2D(4096, (1, 1), activation='relu'))
    model.add(Dropout(0.5))
    model.add(Convolution2D(2622, (1, 1)))
    model.add(Flatten())
    model.add(Activation('softmax'))
    # you can download pretrained weights from https://drive.google.com/file/d/1CPSeum3HpopfomUEK1gybeuIVoeJT_Eo/view?usp=sharing
    from keras.models import model_from_json
    model.load_weights('D:/Ashish/face_detection/vgg_face_weights.h5')
    vgg_face_descriptor = Model(inputs=model.layers[0].input, outputs=model.layers[-2].output)
    return vgg_face_descriptor

model = loadVggFaceModel()

# ------------------------

# put your employee pictures in this path as name_of_employee.jpg
employee_pictures = "D:/Ashish/face_detection/database/"
employees = dict()
for file in listdir(employee_pictures):
    employee, extension = file.split(".")
    employees[employee] = model.predict(preprocess_image('D:/Ashish/face_detection/database/%s.jpg' % (employee)))[0, :]
print("employee representations retrieved successfully")

def findCosineSimilarity(source_representation, test_representation):
    a = np.matmul(np.transpose(source_representation), test_representation)
    b = np.sum(np.multiply(source_representation, source_representation))
    c = np.sum(np.multiply(test_representation, test_representation))
    return 1 - (a / (np.sqrt(b) * np.sqrt(c)))

# ------------------------

cap = cv2.VideoCapture(0)  # webcam
# cap = cv2.VideoCapture('C:/Users/IS96273/Desktop/zuckerberg.mp4') #video

while (True):
    ret, img = cap.read()
    # img = cv2.resize(img, (640, 360))
    faces = face_cascade.detectMultiScale(img, 1.3, 5)

    for (top, right, bottom, left) in faces:
        if bottom > 130:
            detected_face = img[int(right):int(right + left), int(top):int(top + bottom)]  # crop detected face
            detected_face = cv2.resize(detected_face, (224, 224))  # resize to 224x224
            img_pixels = image.img_to_array(detected_face)
            img_pixels = np.expand_dims(img_pixels, axis=0)
            img_pixels /= 127.5
            img_pixels -= 1
            captured_representation = model.predict(img_pixels)[0, :]
            found = 0
            for i in employees:
                employee_name = i
                representation = employees[i]
                similarity = findCosineSimilarity(representation, captured_representation)
                if (similarity < 0.30):
                    cv2.putText(img, employee_name, (int(top + bottom + 15), int(right - 12)), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)
                    found = 1
                    break

            # connect face and text
            cv2.line(img, (int((top + top + bottom) / 2), right + 15), (top + bottom, right - 20), color, 1)
            cv2.line(img, (top + bottom, right - 20), (top + bottom + 10, right - 20), color, 1)
            if (found == 0):  # if found image is not in employee database
                cv2.putText(img, 'Face did not match from database', (int(top + bottom + 15), int(right - 12)), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)

    cv2.imshow('img', img)
    if cv2.waitKey(1) & 0xFF == ord('q'):  # press q to quit
        break

# kill open cv things
cap.release()
cv2.destroyAllWindows()
