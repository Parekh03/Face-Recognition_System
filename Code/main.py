# importing the necessary dependencies
import tkinter as tk
from tkinter import ttk
import cv2
import time
import numpy as np
import face_recognition
import firebase_admin
from firebase_admin import credentials, db, storage
import os
import pickle
import io
from PIL import Image, ImageTk
from datetime import datetime, timedelta
from urllib.request import urlopen
import sys

# Class to handle new user registration
class new_user:

    # Constructor
    def __init__(self, root, db, bucket, knownEncodings, studentNames):
        self.root = root
        self.db = db
        self.bucket = bucket
        self.knownEncodings = knownEncodings
        self.studentNames = studentNames
        self.get_user_data()

    # Function to put text with some background color - used while capturing new user picture
    def put_text_with_background(self, frame, text, position, font, font_scale, text_color, bg_color, thickness):
        (text_width, text_height), baseline = cv2.getTextSize(text, font, font_scale, thickness)
        x, y = position
        cv2.rectangle(frame, (x, y - text_height - baseline), (x + text_width, y + baseline), bg_color, -1)
        cv2.putText(frame, text, (x, y), font, font_scale, text_color, thickness, cv2.LINE_AA)

    # Function to display tkinter window for new user data collection
    def get_user_data(self):

        new_user_window = tk.Toplevel(root)
        new_user_window.title("User Data Collection")
        new_user_window.geometry("500x400")

        # Apply a modern theme
        style = ttk.Style(new_user_window)
        style.theme_use('clam')

        # Set styles
        style.configure('TFrame')
        style.configure('TLabel', font=('Helvetica', 16), foreground='#333')
        style.configure('TButton', font=('Helvetica', 14), padding=10, background='#4CAF50', foreground='#FFFFFF')
        style.map('TButton', background=[('active', '#4CAF50'), ('!active', '#4CAF50')],
                  foreground=[('active', '#FFFFFF'), ('!active', '#FFFFFF')])

        # Define styles
        form_frame = ttk.Frame(new_user_window, padding="40 100 40 100", style="TFrame")
        form_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

        # Add a heading
        heading_label = ttk.Label(new_user_window, text="New User Data Collection", font=('Helvetica', 18, 'bold'),
                                  foreground='#000080')
        heading_label.pack(pady=(20, 20))

        name_label = ttk.Label(form_frame, text="Name:", style="TLabel")
        name_label.grid(row=0, column=0, sticky="W")
        name_entry = ttk.Entry(form_frame, width=30, style="TEntry")
        name_entry.grid(row=0, column=1, pady=10)

        age_label = ttk.Label(form_frame, text="Age:", style="TLabel")
        age_label.grid(row=1, column=0, pady=10, sticky="W")
        age_entry = ttk.Entry(form_frame, width=30, style="TEntry")
        age_entry.grid(row=1, column=1, pady=10)

        gender_label = ttk.Label(form_frame, text="Gender:", style="TLabel")
        gender_label.grid(row=2, column=0, pady=10, sticky="W")
        gender_entry = ttk.Entry(form_frame, width=30, style="TEntry")
        gender_entry.grid(row=2, column=1, pady=10)

        submit_button = ttk.Button(form_frame, text="Submit and Proceed",
                                   command=lambda: self.submit_and_proceed(new_user_window, name_entry.get(),
                                                                           age_entry.get(), gender_entry.get()),
                                   style="TButton")
        submit_button.grid(row=3, column=0, columnspan=2, pady=(20, 50))

        # Add the small text below the submit button
        wait_label = ttk.Label(form_frame, text="Please wait for a few seconds after submitting", style="TLabel")
        wait_label.grid(row=4, column=0, columnspan=2, pady=(0, 10))

        new_user_window.mainloop()

    # Function to add the new user data into the database, and proceed with capturing of picture
    def submit_and_proceed(self, window, name, age, gender):
        window.destroy()

        cap = cv2.VideoCapture(0)
        cap.set(3, 640)
        cap.set(4, 480)
        start_time = time.time()

        user_data = {
            name: {
                "Age": age,
                "Gender": gender,
                "Date": datetime.now().strftime("%Y-%m-%d"),
                "Time": datetime.now().strftime("%H:%M:%S")
            }
        }

        ref = db.reference(f"Students")
        for key, value in user_data.items():
            ref.child(key).set(value)

        while True:
            ret, frame = cap.read()

            # Display text on the frame with background
            display_frame = frame.copy()
            self.put_text_with_background(display_frame, "Press 'c' to capture. Press 'q' to quit.", (70, 40),
                                          cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), (0, 0, 0), 2)

            # Center the window before displaying it
            self.center_window("Capture", 640, 480)
            cv2.imshow("Capture", display_frame)

            key = cv2.waitKey(1) & 0xFF
            if key == ord('q') or key==ord('Q'):
                cap.release()
                cv2.destroyAllWindows()
                root.destroy()
                sys.exit("Thank you.")

            elif key == ord('c') or key == ord('C'):
                # Resize and convert frame to RGB
                frameS = cv2.resize(frame, (216, 216))
                frameRGB = cv2.cvtColor(frameS, cv2.COLOR_BGR2RGB)

                # Convert RGB frame to PIL Image
                pil_img = Image.fromarray(frameRGB)

                # Save PIL Image to a byte stream
                img_byte_arr = io.BytesIO()
                pil_img.save(img_byte_arr, format='PNG')
                img_byte_arr.seek(0)

                # Upload the byte stream to Firebase Storage
                blob = bucket.blob(f'images/{name}.png')
                blob.upload_from_file(img_byte_arr, content_type='image/png')

                # Update the time in the database
                ref = db.reference(f'Students/{name}')
                ref.child('Date').set(datetime.now().strftime("%Y-%m-%d"))
                ref.child('Time').set(datetime.now().strftime("%H:%M:%S"))

                # Get the face encoding and update the pickle file
                encodings = face_recognition.face_encodings(frameRGB)
                if (encodings):
                    encoding = encodings[0]

                    # Check if the name already exists in the encoding file
                    if name in studentNames:
                        index = studentNames.index(name)
                        knownEncodings[index] = encoding
                        print(f"Encoding for {name} updated.")
                    else:
                        knownEncodings.append(encoding)
                        studentNames.append(name)
                        print(f"Encoding for {name} added.")

                    with open("Encodings.p", "wb") as file:
                        pickle.dump([knownEncodings, studentNames], file)

                else:
                    print("No face found in the image.")
                break

        cap.release()
        cv2.destroyAllWindows()
        self.proceed_with_recognition()

    # Function to ask user for consent to proceed with recognition.
    # if yes --> instantiate existing user class which will display window for recognition
    # if no --> Exit the program
    def proceed_with_recognition(self):

        # Create confirmation window
        confirmation_window = tk.Tk()
        confirmation_window.title("Face Recognition Confirmation")
        confirmation_window.geometry("400x150")

        # Apply a modern theme
        style = ttk.Style(confirmation_window)
        style.theme_use('clam')

        # Set styles
        style.configure('TFrame', background='#f0f0f0')
        style.configure('TLabel', font=('Helvetica', 16), foreground='#333')
        style.configure('TButton', font=('Helvetica', 14), padding=10, background='#4CAF50', foreground='#FFFFFF')
        style.map('TButton', background=[('active', '#4CAF50'), ('!active', '#4CAF50')],
                  foreground=[('active', '#FFFFFF'), ('!active', '#FFFFFF')])

        # Label asking for confirmation
        confirmation_label = ttk.Label(confirmation_window, text="Proceed with face recognition now?", style='TLabel')
        confirmation_label.pack(pady=(20, 10))

        # Yes button to proceed
        yes_button = ttk.Button(confirmation_window, text="Yes",
                                command=lambda: existing_user(root, db, bucket, knownEncodings, studentNames),
                                style='TButton')
        yes_button.pack(side=tk.LEFT, padx=(10, 5))

        # No button to exit
        no_button = ttk.Button(confirmation_window, text="No", command=lambda: sys.exit("Thank you."), style='TButton')
        no_button.pack(side=tk.RIGHT, padx=(5, 10))

        confirmation_window.mainloop()  # Wait for user input

    # Function to bring the window at the center of the screen for better user experience
    def center_window(self, window_name, width, height):
        # Create a Tkinter root window and hide it
        root = tk.Tk()
        root.withdraw()

        # Get screen width and height
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()

        # Calculate the position to center the window
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2

        # Set the OpenCV window position
        cv2.namedWindow(window_name)
        cv2.moveWindow(window_name, x, y)


# Class to handle existing users
class existing_user:

    # Constructor
    def __init__(self, root, db, bucket, knownEncodings, studentNames):
        self.root = root
        self.db = db
        self.bucket = bucket
        self.knownEncodings = knownEncodings
        self.studentNames = studentNames
        self.recognize_face()

    # Function to display the window at the center of the screen for better user experience
    def center_window(self, window_name, width, height):
        # Create a Tkinter root window and hide it
        root = tk.Tk()
        root.withdraw()

        # Get screen width and height
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()

        # Calculate the position to center the window
        x = (screen_width - width) // 4
        y = (screen_height - height) // 4

        # Set the OpenCV window position
        cv2.namedWindow(window_name)
        cv2.moveWindow(window_name, x, y)

    # function for recognition
    def recognize_face(self):
        cap = cv2.VideoCapture(0)

        if not cap.isOpened():
            print("Error : Could not open video device.")
            return

        cap.set(3, 640)
        cap.set(4, 480)

        # Displaying the template/background
        imgBackground = cv2.imread("./resources/background2.png")

        # Getting the modes images from the resources directory and storing them into list
        MODES_DIR = "./resources/modes"
        modesList = [cv2.imread(os.path.join(MODES_DIR, image)) for image in os.listdir(MODES_DIR)]

        # Loading the encoding file
        print("Loading the encoding file...")

        with open("Encodings.p", "rb") as file:
            knownEncodingsWithNames = pickle.load(file)

        # Unpacking the knownEncodingsWithNames
        knownEncodings, studentName = knownEncodingsWithNames

        print(studentName)
        print("Encoding file loaded.")
        modeType = 0

        start_time = time.time()

        # Some helper variables
        recognized_once = False
        recognition_counter = None
        details_text = ""

        # start the loop
        while True:
            ret, frame = cap.read()

            # Reducing the size of the image for quick computation
            frameS = cv2.resize(frame, (0, 0), None, 0.25, 0.25)

            # Color scale conversion
            frameS = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # Start face recognition after pressing r
            key = cv2.waitKey(1)
            if key & 0xFF == ord('r'):

                # Perform recognition only if it has not been performed before
                # This ensures that we perform recognition only once after r is pressed
                if not recognized_once:
                    # Restore the original imgBackground to remove previous text
                    imgBackground = cv2.imread("./resources/background2.png")

                    # Find the location of face/faces and get their encodings
                    faceLocations = face_recognition.face_locations(frameS)
                    faceEncodings = face_recognition.face_encodings(frameS, faceLocations)

                    for faceEncoding, faceLocation in zip(faceEncodings, faceLocations):
                        matches = face_recognition.compare_faces(knownEncodings, faceEncoding)
                        faceDistance = face_recognition.face_distance(knownEncodings, faceEncoding)
                        matchIndex = np.argmin(faceDistance)

                        if matches[matchIndex]:
                            recognized_face_name = studentName[matchIndex]
                            print(f"Recognized : {recognized_face_name}")


                            modeType = 2  # switch to modeType 2 after recognition
                            recognition_counter = time.time()  # start counter
                            start_time = time.time()  # reset timer

                            # Set the recognized_once as True, since recognition has been performed once
                            recognized_once = True

                            # updating the last time in the database
                            ref = db.reference(f"Students/{recognized_face_name}")
                            ref.child("Date").set(datetime.now().strftime("%Y-%m-%d"))
                            ref.child("Time").set(datetime.now().strftime("%H:%M:%S"))

                            # if the face is recognized, then make changes in the details mode image
                            # set the recognized person's face and details in that image
                            blob = bucket.get_blob(
                                f'images/{recognized_face_name}.png')
                            try:
                                image_url = blob.generate_signed_url(timedelta(seconds=300), method='GET')

                                # Download the image from the URL
                                resp = urlopen(image_url)
                                image_data = np.asarray(bytearray(resp.read()), dtype="uint8")
                                user_image = cv2.imdecode(image_data, cv2.IMREAD_COLOR)

                                # Resize the user's image to fit the specified coordinates in the details image
                                user_image = cv2.resize(user_image, (215, 213))

                                # Ensure the dimensions match exactly
                                target_height, target_width = 213, 215
                                user_image_resized = cv2.resize(user_image, (target_width, target_height))

                                # Overlay the user's image onto the details image
                                modesList[1][133:133 + target_height, 100:100 + target_width] = user_image_resized

                                student_details = db.reference(f"Students/{recognized_face_name}").get()

                                name_text = f"Name : {recognized_face_name}"
                                age_text = f"Age : {student_details['Age']}"
                                gender_text = f"Gender : {student_details['Gender']}"
                                date_text = f"Date : {student_details['Date']}"
                                time_text = f"Time : {student_details['Time']}"

                                cv2.putText(modesList[1], name_text, (90, 415),
                                            cv2.FONT_HERSHEY_SIMPLEX, 0.70, (0, 0, 0), 2)

                                cv2.putText(modesList[1], age_text, (90, 445),
                                            cv2.FONT_HERSHEY_SIMPLEX, 0.70, (0, 0, 0), 2)

                                cv2.putText(modesList[1], gender_text, (90, 475),
                                            cv2.FONT_HERSHEY_SIMPLEX, 0.70, (0, 0, 0), 2)

                                cv2.putText(modesList[1], date_text, (90, 505),
                                            cv2.FONT_HERSHEY_SIMPLEX, 0.70, (0, 0, 0), 2)

                                cv2.putText(modesList[1], time_text, (90, 535),
                                            cv2.FONT_HERSHEY_SIMPLEX, 0.70, (0, 0, 0), 2)


                                # text for quitting
                                cv2.putText(modesList[1], "Recognition done!. You can quit now.", (10, 600),
                                            cv2.FONT_HERSHEY_SIMPLEX, 0.65, (0, 0, 255), 2)


                            except Exception as e:
                                print(f"Error fetching image: {e}")
                            break

            else:
                cv2.putText(imgBackground, "Press r to initiate recognition. Press q to quit.", (70, 695), cv2.FONT_HERSHEY_SIMPLEX, 0.80, (0, 0, 255), 2)

            imgBackground[162:162 + 480, 55:55 + 640] = frame
            imgBackground[44:44 + 633, 808: 808 + 414] = modesList[modeType]

            # If recognition has been done once, and time elapsed since recognition is greater than 6 seconds then switch to mode 1
            if recognized_once and time.time() - recognition_counter > 6:
                modeType = 1

            # If recognition has been done once, and currently mode is 2, and not 1 then display the below
            if recognized_once and modeType == 2 and modeType != 1:
                cv2.putText(modesList[2], "Loading your data...", (85, 450),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.80, (0, 255, 0), 2)

            # Center the window before displaying it
            self.center_window("Face Attendance", 640, 480)
            cv2.imshow("Face Attendance", imgBackground)

            # Whenever q is pressed, break out of the loop
            if (key & 0xFF == ord('q')) or (key & 0xFF == ord('Q')):
                break

        cap.release()
        cv2.destroyAllWindows()
        root.destroy()
        sys.exit("Thank you")

if __name__ == "__main__":
    # Initialize Firebase app
    cred = credentials.Certificate(".//serviceAccountKey.json")
    firebase_admin.initialize_app(cred, {
        'databaseURL': "https://facerecognition-726fb-default-rtdb.firebaseio.com",
        "storageBucket": "facerecognition-726fb.appspot.com"
    })

    ref = db.reference("Students")
    bucket = storage.bucket()

    # Loading existing encodings if they exist
    if os.path.exists("Encodings.p"):
        with open("Encodings.p", "rb") as file:
            knownEncodingsWithNames = pickle.load(file)
        knownEncodings, studentNames = knownEncodingsWithNames
    else:
        knownEncodings = []
        studentNames = []

    # Creating the main application window
    root = tk.Tk()
    root.title("Face Recognition Attendance System")
    root.geometry("700x400")

    # Apply a modern theme
    style = ttk.Style(root)
    style.theme_use('clam')

    # Set styles
    style.configure('TFrame')
    style.configure('TLabel', font=('Helvetica', 18), foreground='#333')
    style.configure('TButton', font=('Helvetica', 16), padding=10, background='#4CAF50', foreground='#FFFFFF')
    style.map('TButton', background=[('active', '#4CAF50'), ('!active', '#4CAF50')],
              foreground=[('active', '#FFFFFF'), ('!active', '#FFFFFF')])

    # Create a frame to hold the content
    frame = ttk.Frame(root, padding="20 20 20 20", style='TFrame')
    frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

    # Add a stylish heading
    heading = ttk.Label(root, text="Welcome to Face Recognition System", font=('Helvetica', 26, 'bold'), foreground='#000080')
    heading.pack(pady=40)

    # Add a label
    label = ttk.Label(frame, text="Are you a new user or an existing user?", style='TLabel')
    label.grid(row=0, column=0, columnspan=2, pady=20)

    # Add buttons
    new_user_button = ttk.Button(frame, text="New User", command=lambda: new_user(root, db, bucket, knownEncodings, studentNames), style='TButton')
    new_user_button.grid(row=1, column=0, padx=10, pady=10)

    existing_user_button = ttk.Button(frame, text="Existing User", command=lambda: existing_user(root, db, bucket, knownEncodings, studentNames), style='TButton')
    existing_user_button.grid(row=1, column=1, padx=10, pady=10)

    # Add a signature text
    signature = ttk.Label(root, text="Created by Ved | parekhved03@gmail.com", font=('Helvetica', 14), foreground='#333')
    signature.pack(side=tk.BOTTOM, pady=10)

    # Run the application
    root.mainloop()
