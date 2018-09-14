from keras import Sequential, preprocessing
from keras.layers import SimpleRNN, Dense
import numpy as np


## Builds and trains the neural network with the given training data
# @param A 3D array
# @return The neural network classifier, pass this to classify
def build_model(train_data, train_labels):
    print("Reading training data...")
    # all_data = train_data
    # X = []
    # for x in all_data:
    #     X.append(x[:-1])
    # # X = all_data[:,:-1]
    # Y = all_data[:,-1]
    #Xlist = []
    #for x in train_data:
    #    Xlist.append(np.array(x))
    #X = np.array(Xlist)
    X = preprocessing.sequence.pad_sequences(train_data, value=False, padding='post', maxlen=13)
    #X = np.array(train_data)
    #print(X)
    Y = np.array(train_labels)
    batch_size = len(X)
    print(X.shape)

    print("Building RNN...")
    model = Sequential()
    model.add(SimpleRNN(1, activation="relu", input_shape=(X.shape[1], X.shape[2])))
    model.add(Dense(1, activation='sigmoid'))
    model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])

    print("Training...")
    model.fit(X, Y, epochs=100, batch_size=10, verbose=0)
    #print("Model: ")
    #print(model.summary())
    return model


## Evaluate the given model on a test set
# @param model The model to be evaluated
# @param test_data A CSV with the test data
# @param train_labels A CSV with the test labels
# @return Prints and returns the accuracy of the model on the test data
# def evaluate(model, test_data, test_labels):
#     scores = model.evaluate(test_data, test_labels)
#     print("Test data accuracy: {}".format(scores[1] * 100))
#     return scores


## Classfy a single sample
# @param model The model to be used
# @param predcit_data A numpy array with the sample to be classified
# @return A 0 or 1 for which class was predicted
def classify(model, predict_data):
    longest=13
    # Keras wants a list of numpy arrays
    padding = longest-len(predict_data)
    X = np.pad(predict_data,[(0,padding),(0,0)],mode="constant")
    X = np.expand_dims(X, axis=0)
    #print("Predicting on {}".format(X))
    prediction = model.predict(X, verbose=0)
    #print("The prediction is: {}".format(np.round(prediction[0])))
    return np.round(prediction[0])
