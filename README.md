# WildLens — Animal Image Classifier

A full-stack portfolio project combining:
- **Flask** — web framework / routing
- **TensorFlow** (pretrained MobileNetV2) — image classification, no training needed
- **OpenCV** — image preprocessing
- **MySQL** — user accounts + prediction history
- **Werkzeug security** — password hashing (never store plain passwords)

## How it works

1. You sign up / log in.
2. You upload a photo of an animal.
3. OpenCV reads and resizes it; the photo is fed into a pretrained TensorFlow
   model (trained on 1000 ImageNet classes — many of them animals).
4. The top 3 predictions are shown, with the best guess saved to MySQL under
   your account.
5. **Field Notes**: the app looks up the predicted species on Wikipedia
   (via its free public API) and shows a short description with a link to
   read more — so you actually learn something about what you photographed,
   not just a label. Requires an internet connection; if Wikipedia can't be
   reached, the prediction still shows, just without the description.
6. Your "Field Log" page lists every photo you've ever identified.

## 1. Install MySQL (if you haven't already)
Download from https://dev.mysql.com/downloads/installer/ and set a root password
you'll remember — you'll need it in step 3.

## 2. Create the database
In a terminal, run:
```bash
mysql -u root -p < schema.sql
```
This creates the `wildlens` database with `users` and `predictions` tables.

## 3. Set your MySQL password in the code
Open `db.py` and replace:
```python
"password": "YOUR_MYSQL_PASSWORD",
```
with your actual MySQL root password.

## 4. Install Python dependencies
It's best to use a virtual environment:
```bash
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # Mac/Linux

pip install -r requirements.txt
```

> Note: tensorflow + opencv together are a few hundred MB to download —
> this step can take a few minutes on the first run.

## 5. Run the app
```bash
python app.py
```
You'll see in the terminal:
```
Loading MobileNetV2 model (first run downloads ~14MB of weights)...
Model ready.
 * Running on http://127.0.0.1:5000
```

Open that URL in your browser, sign up, and try uploading an animal photo.

## Project structure
```
wildlens/
├── app.py              # Flask routes (signup, login, predict, history)
├── db.py                # All MySQL queries
├── model_utils.py        # OpenCV preprocessing + TensorFlow prediction
├── species_info.py       # Wikipedia lookup for predicted species
├── schema.sql            # Database tables
├── requirements.txt
├── templates/
│   ├── base.html
│   ├── index.html        # Upload + result page
│   ├── login.html
│   ├── signup.html
│   └── history.html      # Field log
└── static/
    ├── style.css
    └── uploads/           # Uploaded photos are saved here
```

## Ideas to extend this for your resume
- Add a "delete entry" button on the Field Log page (more DELETE practice)
- Show a bar chart of "most identified animals" using matplotlib or Chart.js
- Deploy it on the AWS EC2 instance you already set up, with RDS instead of local MySQL
- Swap MobileNetV2 for a model you fine-tune yourself on a small animal dataset (next-level version)
- Add an admin view that lists all users' predictions (good Django comparison exercise later)

## What to say about it on your resume / LinkedIn
> "Built WildLens, a full-stack image classification web app (Flask, TensorFlow,
> OpenCV, MySQL) with user authentication and a personal prediction history,
> deployed to AWS EC2."
