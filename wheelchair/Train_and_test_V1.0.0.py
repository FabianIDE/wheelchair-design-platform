import os
from dotenv import load_dotenv
from datetime import datetime
import math

import io
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import accuracy_score
from sklearn.metrics import f1_score
from sklearn.metrics import precision_score
from sklearn.metrics import recall_score
from sklearn.metrics import confusion_matrix
from sklearn.metrics import classification_report
import numpy
import pickle

from dcd.entities.thing import Thing

# The thing ID and access token
load_dotenv()
THING_ID = os.environ['THING_ID']
THING_TOKEN = os.environ['THING_TOKEN']

# Sitting classes
CLASSES = ["Not Sitting", "Proper Sitting", "Leaning Forward",
           "Leaning Backward", "Leaning Left", "Leaning Right"]

# Where to save the model to
MODEL_FILE_NAME = "model.pickle"

# Data collection time frame (in milliseconds)
START_TS = 1550946000000
END_TS = 1550946000000+300000

# Property ID
LABEL_PROP_NAME = "Movement"
PROPETY_HRM_NAME = "My heart rate measurement 1"
PROPETY_ORIENTATION_NAME = "Right Sports Wheel Arbeid"
PROPETY_WHEELCHAIR_NAME = "Chair base"

# Instantiate a thing with its credential
my_thing = Thing(thing_id=THING_ID, token=THING_TOKEN)

# We can fetch the details of our thing
my_thing.read()

def unix_time_millis(dt):
    epoch = datetime.utcfromtimestamp(0)
    return math.floor((dt - epoch).total_seconds() * 1000.0)

# If you just registered your Thing on the DCD Hub,
# it has only an id, a name and a type.
# print(my_thing.to_json())

prop_label = my_thing.find_or_create(LABEL_PROP_NAME, PropertyType.CLASS)
prop_orientation = my_thing.find_or_create(PROPERTY_ORIENTATION_NAME, PropertyType.THREE_DIMENSIONS)
prop_hrm = my_thing.find_or_create(PROPERTY_HRM_NAME, PropertyType.ONE)
prop_wheelchair = my_thing.find_or_create(PROPERTY_WHEELCHAIR_NAME, PropertyType.THREE_DIMENSIONS)


prop_orientation.read(START_TS, END_TS)
prop_label.read(START_TS, END_TS)


prop_orientation.align(prop_hrm)
prop_orientation_hrm = prop_orientation.merge(prop_hrm)

prop_orientation_hrm.align(prop_wheelchair)
prop_all = prop_orientation_hrm.merge(prop_wheelchair)

prop_all.align(prop_label)

data = prop_all.values
label = prop_label.values

# Split the data into training data (80%) and test data (20%)
train_data = []
train_label = []
test_data = []
test_label = []

for index in range(len(data)):
    # remove time
    data[index].pop(0)
    label[index].pop(0)
    if index%5 == 0:
        # 20% to test data
        test_data.append(data[index])
        test_label.append(label[index])
    else:
        # 80% to train data
        train_data.append(data[index])
        train_label.append(label[index])

print("nb train data: " + str(len(data)))
print("nb train labels: " + str(len(label)))

print("nb train data: " + str(len(train_data)))
print("nb train labels: " + str(len(train_label)))

print("nb test data: " + str(len(test_data)))
print("nb test labels: " + str(len(test_label)))

# Train a k-Nearest Neighbour (kNN) algorithm
neigh = KNeighborsClassifier(n_neighbors=1)
neigh.fit(train_data, train_label)

# Use the test data to evaluate the algorithm
predicted = neigh.predict(test_data)
testLabel = numpy.array(test_label)
result = accuracy_score(testLabel, predicted)
print(result)

# Report evaluation Confusion matrix
matrix = confusion_matrix(testLabel, predicted)
print(matrix)
print(precision_score(testLabel, predicted, average="macro"))
print(recall_score(testLabel, predicted, average="macro"))
print(f1_score(testLabel, predicted, average="weighted"))
print(f1_score(testLabel, predicted, average=None))

print(classification_report(test_label, predicted, target_names=CLASSES))

# Save the model in a file
with io.open(MODEL_FILE_NAME, "wb") as file:
    pickle.dump(neigh, file, protocol=2)
