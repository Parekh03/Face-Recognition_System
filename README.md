# Face-Recognition_System

## Project Overview
This project is a Face Recognition System developed during a summer internship at the Indian Institute of Technology, Bhubaneswar. The system is designed to detect, store, process, and recognize faces in real-time, enhancing user authentication and attendance tracking.

## Introduction
The concept of Face Recognition has become an integral part of modern technologies. From mobile phone cameras to surveillance systems for security, this underlying software have made our lives more secure and convenient by providing robust authentication identities. These systems leverage the unique physiological traits of a person's face, making them highly reliable and difficult to replicate compared to traditional methods such as passwords or PINs.

The project involves building a Face Recognition System which an advanced and reliable software/app which enables quick detection, storing, processing and recognition of faces in real-time. This system / software enhances the user authentication and attendance updation quality.

## Primary Objectives
1. Develop a robust and reliable face recognition system with a user-friendly interface.
2. Capture and securely store user data, including facial images.
3. Perform real-time face recognition and display user details with updated date and time.

## Working
Pictorial representation of working of the system is as follows:

![Flowchart (1)](https://github.com/user-attachments/assets/8ac3b935-7cbb-43fd-a812-c8d2fd848ea0)

### 1. Initialization
Initialization: Run the main Python script to start the software.

### 2. User Selection
Choose between new user registration and existing user recognition.

![new_or_existing (1)](https://github.com/user-attachments/assets/741a5a97-d933-49e2-91fa-7ce5d8973d07)

### 3. New User Registration

#### Data collection for new users:
![new_user_data_collection](https://github.com/user-attachments/assets/281a6279-c92a-4408-8b57-7dd58ea37b41)


#### Capturing picture of new user after data collection:
![user_image_capture](https://github.com/user-attachments/assets/ef192055-31b9-4e05-809f-4e1557355ea3)


#### Choice to proceed for recognition / attendance marking or quit:
![proceed_confirmation](https://github.com/user-attachments/assets/cdb16ec9-f352-4e61-a950-1d312801b3da)


#### On proceeding with recognition: Initially Active mode
![main_recognition_window](https://github.com/user-attachments/assets/98d95088-9b11-4965-9f9b-7ea03a70691f)


#### On pressing 'r' (case insensitive) for recognition (This marked mode is displayed for a few seconds):
![marked_window (1)](https://github.com/user-attachments/assets/b2ed68db-5610-406f-a76c-4f0f7dfeb547)


#### After a few seconds:
![details_window](https://github.com/user-attachments/assets/1a5d6445-3f0f-4d08-9139-d4e8709a14ee)

## Existing User Recognition
If the user selects the "Existing User" option, the workflow bypasses the registration steps and starts directly from the [recognition process](https://github.com/Parekh03/Face-Recognition_System/edit/main/README.md#on-proceeding-with-recognition-initially-active-mode)


## Testing
The software has been tested on a diverse group of individuals under various conditions, demonstrating high accuracy and reliability in face recognition. Some of the results are as follows:

![vasu](https://github.com/user-attachments/assets/9890eb68-d0f2-4e21-b8d5-c373fbdf8a76)

![saswat](https://github.com/user-attachments/assets/f9d87174-7683-41dc-bbea-e28aedf39a1d)

![pratush](https://github.com/user-attachments/assets/319be0ec-e379-4285-9686-038e1b4f600e)

![sawan](https://github.com/user-attachments/assets/0c2b910b-776a-45f6-9d74-12d6eaa8ce19)


## Notes
1.	Due to poor network connectivity, the second window displaying “Marked. Loading your data” might not appear. Instead, the final details window might be shown directly.

2.	If the face is not recognized during the real-time live video, pressing ‘r’ multiple times will have no effect. It is recommended to use the system in a well-lit area where the face is visible to the camera.

3.	Poor network connectivity or data deletion from the database can result in data not being displayed in the final window. In such cases, the following will be observed:







