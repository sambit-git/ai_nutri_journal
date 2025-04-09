import numpy as np
import tensorflow as tf
from tensorflow.keras.preprocessing import image

class FoodClassifier:
    """Equivalent to Django's service layer"""
    def __init__(self, model_path: str, test_path: str):
        self.model = tf.keras.models.load_model(model_path)
        self.test_set = tf.keras.utils.image_dataset_from_directory(
            test_path,
            labels="inferred",
            label_mode="categorical",
            class_names=None,
            color_mode="rgb",
            batch_size=32,
            image_size=(64, 64),
            shuffle=True,
            seed=None,
            validation_split=None,
            subset=None,
            interpolation="bilinear",
            follow_links=False,
            crop_to_aspect_ratio=False
        )
        self.class_names = self.test_set.class_names
    
    def predict(self, image_path: str):
        img = image.load_img(image_path, target_size=(64, 64))
        img_array = image.img_to_array(img)
        img_array = np.expand_dims(img_array, axis=0)
        predictions = self.model.predict(img_array)
        
        return {
            "class": self.class_names[np.argmax(predictions[0])],
            "confidence": float(np.max(predictions[0]))
        }