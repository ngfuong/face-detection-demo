# Features
* Display device webcam.
* Detect faces in webcam output.
* Recognize (= Detect + Identify) faces in `images` folder.
* Capture image from webcam to add to recognization model.

# Installation
Clone repository. Cloning can take a while because of the model weights in `models\weights`
```
git clone https://github.com/ngfuong/face-detection-demo.git
```
Create virtual environment and install packages
```
python -m venv .env
.env\Scripts\activate # For Windows
pip install -r requirements.txt
```
Run application
```
python main.py
```