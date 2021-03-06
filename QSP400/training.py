from QSP400 import dataPro as data
import numpy as np
from keras.models import Sequential
from keras.regularizers import l2
from keras.layers import LSTM, Dense, Dropout, Activation, initializers, GRU, SimpleRNN,ConvLSTM2D
from keras import optimizers
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
import matplotlib.pyplot as plt
from keras.layers import Conv1D, GlobalAveragePooling1D, MaxPooling1D,BatchNormalization, Activation, Flatten
from keras.layers import Conv2D, MaxPooling2D,Embedding,Bidirectional,LeakyReLU
from sklearn.metrics import roc_curve, auc
import numpy as np
# ac,label=data.ac()
ac_p,label=data.deal()
aac=data.fe()
ctd=data.CTD()
gaac=data.gaac()
X=np.concatenate((aac,gaac,ac_p),axis=1)# X=ac,ctd,kmer

# print(X)
def calculate_performace(test_num, pred_y, labels):
    tp = 0
    fp = 0
    tn = 0
    fn = 0
    for index in range(test_num):
        if labels[index] == 1:
            if labels[index] == pred_y[index]:
                tp = tp + 1
            else:
                fn = fn + 1
        else:
            if labels[index] == pred_y[index]:
                tn = tn + 1
            else:
                fp = fp + 1
    print('tp:',tp,'fn:',fn,'tn:',tn,'fp:',fp)
    acc = float(tp + tn) / test_num
    precision = float(tp) / (tp + fp)
    sensitivity = float(tp) / (tp + fn)
    specificity = float(tn) / (tn + fp)
    MCC = float(tp * tn - fp * fn) / (np.sqrt((tp + fp) * (tp + fn) * (tn + fp) * (tn + fn)))
    return acc, precision, sensitivity, specificity, MCC
    # return acc


def transfer_label_from_prob(proba):
    label = [1 if val >= 0.6 else 0 for val in proba]
    return label


def plot_roc_curve(labels, probality, legend_text, auc_tag=True):
    # fpr2, tpr2, thresholds = roc_curve(labels, pred_y)
    fpr, tpr, thresholds = roc_curve(labels, probality)  # probas_[:, 1])
    roc_auc = auc(fpr, tpr)
    if auc_tag:
        rects1 = plt.plot(fpr, tpr, label=legend_text + ' (AUC=%6.3f) ' % roc_auc)
    else:
        rects1 = plt.plot(fpr, tpr, label=legend_text)

# define parameters
batch_size =32
epochs = 20
all_labels=[]
all_prob = {}
all_prob[0] = []
label=np.array(label)
num_cross_val=5
all_performance_lstm = []
# print("___",len(label[label==1]),len(label[label==0]))
def do_model():
    for fold in range(num_cross_val):
        # x_train, x_test, y_train, y_test = train_test_split(X, label, test_size=0.2, random_state=10)
        # x_train, x_test, y_train, y_test = train_test_split(X, label, test_size=0.2, random_state=10)
        x_train = np.array([x for i, x in enumerate(X) if i % num_cross_val != fold])
        x_test = np.array([x for i, x in enumerate(X) if i % num_cross_val == fold])
        y_train = np.array([x for i, x in enumerate(label) if i % num_cross_val != fold])
        y_test = np.array([x for i, x in enumerate(label) if i % num_cross_val == fold])
        x_train = x_train.reshape((x_train.shape[0], x_train.shape[1], 1))
        x_test = x_test.reshape((x_test.shape[0], x_test.shape[1], 1))
        y_train = np.array(y_train)
        y_test = np.array(y_test)
        y_train = y_train.reshape((y_train.shape[0], 1))
        y_test = y_test.reshape((y_test.shape[0], 1))
        real_labels = []

        for val in y_test:
            if val == 1:
                real_labels.append(1)
            else:
                real_labels.append(0)

        train_label_new = []
        for val in y_train:
            if val == 1:
                train_label_new.append(1)
            else:
                train_label_new.append(0)
        global    all_labels
        global    all_prob
        all_labels = all_labels + real_labels
        print("**", type(x_train))
        print(x_train.shape, y_train.shape)
        model = Sequential()
        model.add(Conv1D(8, kernel_size=3, strides=1, padding='same', input_shape=(37, 1)))
        model.add(BatchNormalization())
        model.add(Activation('relu'))
        model.add(Conv1D(8, kernel_size=3, strides=1, padding='same'))
        model.add(Conv1D(16, kernel_size=3, strides=1, padding='valid'))
        model.add(Dropout(0.2))
        model.add(Conv1D(8, kernel_size=3, strides=1, padding='same'))
        model.add(Conv1D(16, kernel_size=3, strides=1, padding='valid'))
        # model.add(BatchNormalization())
        # model.add(Dropout(0.1))
        model.add(Activation('relu'))
        model.add(Conv1D(16, kernel_size=3, strides=1, padding='same'))
        model.add(Conv1D(32, kernel_size=3, strides=1, padding='valid'))
        model.add(BatchNormalization())
        model.add(Conv1D(32, kernel_size=3, strides=1, padding='same'))
        model.add(Conv1D(64, kernel_size=3, strides=1, padding='same'))
        model.add(Activation('relu'))
        # model.add(Flatten())
        model.add(Dropout(0.2))
        # model.add(LSTM(32, return_sequences=True))
        model.add(Bidirectional(LSTM(32, return_sequences=True)))
        # model.add(Dropout(0.2))
        model.add(Flatten())
        # model.add(Dense(512, kernel_initializer='he_normal', activation='relu', W_regularizer=l2(0.01)))
        # model.add(Dense(128, kernel_initializer='he_normal', activation='relu', W_regularizer=l2(0.01)))
        # model.add(Dense(64, kernel_initializer='he_normal', activation='relu', W_regularizer=l2(0.01)))
        # model.add(Dense(16, kernel_initializer='he_normal', activation='relu', W_regularizer=l2(0.01)))
        model.add(Dense(1, kernel_initializer='normal', activation='sigmoid'))

        opt = optimizers.Adam(lr=0.001)  # 0.01
        model.compile(optimizer=opt, loss='binary_crossentropy', metrics=['accuracy'])
        model.summary()

        print("Train...")
        model.fit(x_train, y_train, batch_size=batch_size, epochs=epochs)
        # json_string = model.to_json()
        # open('model_architecture_1.json', 'w').write(json_string)
        # yaml_string = model.to_yaml()
        # open('model_arthitecture_2.yaml', 'w').write(yaml_string)
        lstm_proba = model.predict_proba(x_test)
        # print(lstm_proba)
        # print(y_test)
        all_prob[0] = all_prob[0] + [val for val in lstm_proba]
        y_pred_xgb = transfer_label_from_prob(lstm_proba)
        # acc=calculate_performace(len(real_labels), y_pred_xgb, real_labels)
        acc, precision, sensitivity, specificity, MCC = calculate_performace(len(y_test), y_pred_xgb, y_test)
        # print(acc)
        print(acc, precision, sensitivity, specificity, MCC)

        all_performance_lstm.append([acc, precision, sensitivity, specificity, MCC])
        print(all_performance_lstm)
        print('---' * 50)
    return  model
model=do_model()
yaml_string = model.to_yaml()
open('model_arthitecture_2.yaml', 'w').write(yaml_string)
    # background = x_train[np.random.choice(x_train.shape[0], 100, replace=False)]
    #
    # # explain predictions of the model on three images
    # e = shap.DeepExplainer(model, background)
    # # ...or pass tensors directly
    # # e = shap.DeepExplainer((model.layers[0].input, model.layers[-1].output), background)
    # shap_values = e.shap_values(x_test[1:5])

print('mean performance of QSP')
print(np.mean(np.array(all_performance_lstm), axis=0))
print('---' * 50)
plot_roc_curve(all_labels, all_prob[0], 'proposed method')
plt.plot([0, 1], [0, 1], 'k--')
plt.xlim([-0.05, 1])
plt.ylim([0, 1.05])
plt.xlabel('False Positive Rate')
plt.ylabel('True Positive Rate')
plt.title('ROC')
plt.legend(loc="lower right")
# plt.savefig(save_fig_dir + selected + '_' + class_type + '.png')
plt.show()
import keras.backend as K

K.clear_session()

