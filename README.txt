ProteoSpark - Proteomics Data Analysis Tool for DIA Spectrometry
===============================================================

For more information about this project, please contact: 
Dr. Amanda Pearce 
Pearce Polymer Lab
Loughborough University 
Email: a.pearce@lboro.ac.uk

This code has been adapted from the following code written by Dr. Jedd Bellamy-Carter - Loughborough University:
https://github.com/jbellamycarter/quick-ms-explorer_streamlit-app

This streamlit web app was created as part of an MSc Data Science Project by:
Hetal Joshi - Loughborough University


===============================================================

The purpose of this web app is to facilitate further data analysis and validation of exported PeptideShaker Reports
as part of a pre-existing proteomics data processing pipeline for DIA Spectrometry. 

The following proteomics data processing pipeline was used:

DIA-Umpire
SearchGUI
PeptideShaker
(ProteoSpark)

In this project, there is a folder called Streamlit_App.
It contains the following: venv, __pycache__ , requirements.txt, peptideshaker_reports.db, python modules, app.py and a README file.

There are four modules that have been created:
 - home_page.py
 - second_page.py
 - third_page.py
 - fourth_page.py
 

These modules are imported into app.py and are executed in an sequential order to launch the web app. 

Users will need to ensure the following: 

1. Python 3.7 or higher is installed 

2. A sqlite database has been created - this code already comes with peptideshaker_reports.db as the default

3. PeptideShaker Reports have been exported and saved as Excel files to then upload into the web app 

4. Raw and Processed .mzML files that can be uploaded to the web app 

5. It is highly recommended that DB Browser for SQLite is also used to manage the files in the sqlite database

6. Run app.py in command prompt using the following Windows commands:
   Copy and paste the current filepath of your current directory e.g. cd "C:\Users\joshi\Documents\Project\Coding\Streamlit_App" 
   Then press Enter
   Activate the virtual environment by copying and pasting this command into the command prompt: .\venv\Scripts\Activate
   Then press Enter
   Type in 'streamlit run app.py' and press enter; the script will be executed and the web app will be launched. 








