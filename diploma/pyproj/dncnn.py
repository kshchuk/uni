import os
import tensorflow as tf
from tensorflow.keras.layers import Input, Conv2D, BatchNormalization, Activation, Add, Lambda
from tensorflow.keras.models import Model
from tensorflow.keras.callbacks import ModelCheckpoint, ReduceLROnPlateau, EarlyStopping

def build_dncnn(input_shape, depth=17, num_filters=64):
    """
    Build a DnCNN model.

    Args:
        input_shape (tuple): Shape of the input image, e.g., (height, width, channels).
        depth (int): Total number of convolutional layers (default is 17).
        num_filters (int): Number of filters for intermediate layers.

    Returns:
        model (tf.keras.Model): The constructed DnCNN model.
    """
    # Define the input layer
    inputs = Input(shape=input_shape)

    # First convolutional layer with ReLU activation
    x = Conv2D(num_filters, (3, 3), padding='same', activation='relu')(inputs)

    # Intermediate layers: Conv2D -> BatchNormalization -> ReLU
    for i in range(1, depth - 1):
        x = Conv2D(num_filters, (3, 3), padding='same')(x)
        x = BatchNormalization()(x)
        x = Activation('relu')(x)

    # Final convolutional layer: output has the same number of channels as the input
    x = Conv2D(input_shape[-1], (3, 3), padding='same')(x)

    # Residual learning: subtract the predicted noise from the input image
    outputs = Add()([inputs, Lambda(lambda t: -t)(x)])

    # Build and return the model
    model = Model(inputs=inputs, outputs=outputs)
    return model

def get_callbacks(model_save_path):
    """
    Define a set of callbacks for training.

    Returns:
        list: List of Keras callbacks.
    """
    checkpoint = ModelCheckpoint(model_save_path, monitor='val_loss', verbose=1,
                                 save_best_only=True, mode='min')
    reduce_lr = ReduceLROnPlateau(monitor='val_loss', factor=0.5, patience=5,
                                  min_lr=1e-7, verbose=1)
    early_stop = EarlyStopping(monitor='val_loss', patience=10, verbose=1)
    return [checkpoint, reduce_lr, early_stop]

def train_dncnn(model, train_dataset, val_dataset, epochs=50, batch_size=32, model_save_path='dncnn_best_model.h5'):
    """
    Train the DnCNN model.

    Args:
        model (tf.keras.Model): The DnCNN model.
        train_dataset (tf.data.Dataset): Dataset for training (yields (noisy_image, clean_image) pairs).
        val_dataset (tf.data.Dataset): Dataset for validation.
        epochs (int): Number of training epochs.
        batch_size (int): Batch size for training.
        model_save_path (str): File path to save the best model.

    Returns:
        history: Training history.
    """
    model.compile(optimizer=tf.keras.optimizers.Adam(learning_rate=1e-4),
                  loss='mse',
                  metrics=[tf.keras.metrics.MeanAbsoluteError()])

    callbacks = get_callbacks(model_save_path)

    history = model.fit(train_dataset,
                        validation_data=val_dataset,
                        epochs=epochs,
                        callbacks=callbacks)
    return history

def load_image(path, target_size=(640, 640), grayscale=False):
    image = tf.io.read_file(path)
    if grayscale:
        image = tf.image.decode_jpeg(image, channels=1)
    else:
        image = tf.image.decode_jpeg(image, channels=3)
    image = tf.image.convert_image_dtype(image, tf.float32)
    image = tf.image.resize(image, target_size)
    return image


def create_dataset(subset, image_size=(640,640), grayscale=False, cache_file=None):
    """
    Args:
        subset (str): 'train', 'val' або 'test'.
        image_size (tuple): Розмір зображення для ресайзу.
        grayscale (bool): Чи завантажувати зображення в градаціях сірого.
        cache_file (str): Шлях до файлу для кешування на диску (якщо None, кешування в пам’яті).

    Returns:
        tf.data.Dataset: Датасет з парами (noisy_image, clean_image).
    """
    if subset == "train":
        subset_dir = "VisDrone2019-DET-train"
    elif subset == "val":
        subset_dir = "VisDrone2019-DET-val"
    elif subset == "test":
        subset_dir = "VisDrone2019-DET-test-dev"
    else:
        raise ValueError("Невідома підмножина. Використовуйте 'train', 'val' або 'test'.")

    clean_dir = os.path.join("dataset", "images", subset_dir, "images")
    noisy_dir = os.path.join("dataset_noisy", subset_dir, "images")

    # Список файлів із чистими зображеннями
    clean_files = tf.data.Dataset.list_files(os.path.join(clean_dir, "*.jpg"))

    def load_pair(clean_path):
        # Отримуємо ім'я файлу з шляху
        filename = tf.strings.split(clean_path, os.sep)[-1]
        noisy_path = tf.strings.join([noisy_dir, "/", filename])
        clean_image = load_image(clean_path, target_size=image_size, grayscale=grayscale)
        noisy_image = load_image(noisy_path, target_size=image_size, grayscale=grayscale)
        return noisy_image, clean_image

    # Паралельне завантаження та обробка зображень
    dataset = clean_files.map(load_pair, num_parallel_calls=tf.data.AUTOTUNE)

    # Якщо dataset невеликий і вміщається в оперативній пам'яті, можна кешувати у пам'яті.
    # Якщо даних багато, використовуйте кешування на диску, вказавши шлях до файлу (cache_file).
    if cache_file:
        dataset = dataset.cache(cache_file)
    else:
        dataset = dataset.cache()

    return dataset


# Основна частина коду
if __name__ == '__main__':
    # Визначаємо форму вхідного зображення (наприклад, 64x64 у градаціях сірого)
    input_shape = (640, 640, 3)

    # Будуємо модель DnCNN
    dncnn_model = build_dncnn(input_shape=input_shape, depth=17, num_filters=64)
    dncnn_model.summary()

    # Створюємо датасети для тренування та валідації за структурою директорій
    train_dataset = create_dataset("train", image_size=(640, 640), grayscale=False, cache_file="tdrddadssin_cache.tfdata")
    val_dataset = create_dataset("val", image_size=(640, 640), grayscale=False)

    # Налаштовуємо батчування, перемішування та попереднє завантаження
    batch_size = 8
    train_dataset = train_dataset.shuffle(train_dataset.cardinality()).batch(batch_size).prefetch(tf.data.AUTOTUNE)
    val_dataset = val_dataset.batch(batch_size).prefetch(tf.data.AUTOTUNE)

    # Навчаємо модельs
    history = train_dncnn(dncnn_model, train_dataset, val_dataset,
                          epochs=50, batch_size=batch_size,
                          model_save_path='dncnn_best_model.h5')

