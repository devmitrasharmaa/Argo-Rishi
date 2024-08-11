import numpy as np
import tensorflow as tf
from tensorflow.keras.preprocessing.image import load_img, img_to_array
import matplotlib.pyplot as plt
import cv2

# Load the model (assuming you have the model saved at 'trained_plant_disease_model.keras')
cnn = tf.keras.models.load_model('trained_plant_disease_model.keras')

# Function to process image and predict disease
def predict_disease(image_path):
    # Load and preprocess the image
    img = cv2.imread(image_path)
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    
    # Preprocess image for model prediction
    image = load_img(image_path, target_size=(128, 128))
    input_arr = img_to_array(image)
    input_arr = np.array([input_arr])  # Convert single image to a batch

    # Make predictions
    predictions = cnn.predict(input_arr)
    result_index = np.argmax(predictions)
    
    # Load class names
    validation_set = tf.keras.utils.image_dataset_from_directory(
        'valid', labels="inferred", label_mode="categorical",
        image_size=(128, 128), batch_size=32, shuffle=True)
    class_name = validation_set.class_names

    # Get the disease name
    model_prediction = class_name[result_index]

    return model_prediction, img_rgb
