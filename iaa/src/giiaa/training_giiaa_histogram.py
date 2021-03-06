"""
Training script for distribution-based GIIAA, based on the NIMA paper from Google.
"""

from iaa.src.giiaa.base_module_giiaa import *
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.callbacks import ModelCheckpoint, TensorBoard
from tensorflow.keras import backend as K
import pandas as pd
import os


AVA_DATAFRAME_PATH = "../../data/ava/giiaa_metadata/dataframe_AVA_giiaa-hist_train.csv"

LOG_PATH = "../../data/ava/giiaa_metadata/giiaa-hist_logs"
MODELS_PATH = "../../models/giiaa/"
MODEL_NAME_TAG = 'giiaa-hist_200k_base-'
BASE_MODEL_NAME = "InceptionResNetV2"

N_CLASSES = 10
BATCH_SIZE = 96
DROPOUT_RATE = 0.75
USE_MULTIPROCESSING = False
N_WORKERS = 1

EPOCHS_DENSE = 5
LEARNING_RATE_DENSE = 0.001
DECAY_DENSE = 0

EPOCHS_ALL = 9
LEARNING_RATE_ALL = 0.00003
DECAY_ALL = 0.000023


if __name__ == "__main__":

    nima = NimaModule(BASE_MODEL_NAME, N_CLASSES, LEARNING_RATE_DENSE, DECAY_DENSE, DROPOUT_RATE)
    nima.build()

    dataframe = pd.read_csv(AVA_DATAFRAME_PATH, converters={'label': eval})

    data_generator = ImageDataGenerator(
        rescale=1.0 / 255,
        validation_split=0.2
    )

    train_generator = data_generator.flow_from_dataframe(
        dataframe=dataframe,
        x_col='id',
        y_col=['label'],
        class_mode='multi_output',
        target_size=(224, 224),
        color_mode='rgb',
        batch_size=BATCH_SIZE,
        subset='training'
    )

    validation_generator = data_generator.flow_from_dataframe(
        dataframe=dataframe,
        x_col='id',
        y_col=['label'],
        class_mode='multi_output',
        target_size=(224, 224),
        color_mode='rgb',
        batch_size=BATCH_SIZE,
        subset='validation',
    )

    tensorboard = TensorBoard(
        log_dir=LOG_PATH, update_freq='batch'
    )

    model_save_name = (MODEL_NAME_TAG + BASE_MODEL_NAME.lower() + '_{val_loss:.3f}.hdf5')
    model_file_path = os.path.join(MODELS_PATH, model_save_name)
    model_checkpointer = ModelCheckpoint(
        filepath=model_file_path,
        monitor='val_loss',
        verbose=1,
        save_best_only=True,
        save_weights_only=False,
    )

    for layer in nima.base_model.layers:
        layer.trainable = False

    nima.compile()
    nima.nima_model.summary()

    nima.nima_model.fit_generator(
        generator=train_generator,
        steps_per_epoch=train_generator.samples // train_generator.batch_size,
        validation_data=validation_generator,
        validation_steps=validation_generator.samples // validation_generator.batch_size,
        epochs=EPOCHS_DENSE,
        use_multiprocessing=USE_MULTIPROCESSING,
        workers=N_WORKERS,
        verbose=1,
        max_queue_size=30,
        callbacks=[tensorboard, model_checkpointer]
    )

    for layer in nima.base_model.layers:
        layer.trainable = True

    nima.compile()
    nima.nima_model.summary()

    nima.nima_model.fit_generator(
        generator=train_generator,
        steps_per_epoch=train_generator.samples // train_generator.batch_size,
        validation_data=validation_generator,
        validation_steps=validation_generator.samples // validation_generator.batch_size,
        epochs=EPOCHS_DENSE + EPOCHS_ALL,
        initial_epoch=EPOCHS_DENSE,
        use_multiprocessing=USE_MULTIPROCESSING,
        workers=N_WORKERS,
        verbose=1,
        max_queue_size=30,
        callbacks=[tensorboard, model_checkpointer],
    )

    K.clear_session()




