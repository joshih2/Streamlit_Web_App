###########################
# F333290 - H.Joshi        #
# Date Created: 29/07/2024 #
# Last Updated: 17/08/2024 #
###########################

'''
home_page.py

Please refer to app.py for a detailed description of this module.

Function:
def home_page() - displaying the home page (page 1) within the ProteoSpark Streamlit Web App

'''

# Importing library required for this module
import streamlit as st

def home_page():
    
    '''
    Function for displaying the home page of the web app. 

    Displaying the title, information, user instructions and contact details for the project.
    '''
    # Configuring the layout of the homepage 
    left_column, right_column = st.columns([2, 1])

    with left_column:
        st.title("ProteoSpark")
        st.subheader("Proteomics Data Analysis Tool for DIA Spectrometry")
        st.markdown("""
        **About:**
        
        *This is ProteoSpark version 1.*

        This web app has been designed to work as part of the following proteomics data processing pipeline:

        - DIA-Umpire
        - SearchGUI
        - PeptideShaker
        - (ProteoSpark)

        Users will be able upload exported PeptideShaker Reports ('.xlsx') into this web app to further analyse the data in an interactive format. 
        
        Users will have the flexibility to select the analysis they require and can go through some or all of 
        the pages if they wish to. 
    
        It is highly recommended that DB Browser for SQLite is also used to manage the files in the sqlite database. 

                     
        There are three types of analysis that can be conducted:
                     
        1. **Interactive Data Tables (page 2):**
        
        Users will be able to upload PeptideShaker reports into Streamlit interactive tables. 
        They will be able to perform data cleaning operations on the processed data such as:
        filtering, grouping and removing columns and saving these changes to a new Excel file.
                     
        They will also be able to conduct descriptive statistics and visualisations such as: 
        count, percentages, pie charts and heatmaps on the cleaned processed data. 
        The data cleaning operations will then be used to update the subsequent statistics and visualisations. 
        
        Note: Grouping columns will create a new dataframe but will not update the statistics and visualisations. 
                
        Users will be able to download and save any of the tables as .csv files and visualisations as static .png files. 
        If they make any changes to the visualisations using the interactive features, then these changes can also be saved.  
                    
        Note: If users need to delete a uploaded table from the sqlite database on page 2 or page 3, they will be able to 
        do so on page 2. Please follow the instructions in the information tab on page 2 to learn more about the table deletion process. 
        Deleted tables will be removed from the sqlite database and so will not be able to be retrieved for analysis on page 2 and 3.  
                    
                                
        2. **Protein-Peptides-PSMs Data Retrieval Form (page 3):**
        
        Users will be required to specifically upload the PeptideShaker Protein and PSM reports ('.xlsx').
        They will be able to select the protein description from a pre-populated dropdown menu which will then
        automatically select the main accession code assoicated with that protein description. 
        The form will retrieve the data from both the Default PSM and Protein Report on the associated peptides and PSMs 
        for that particular protein description. 
        
        Users will be able to download and save the retrieved data as .csv files.
        In particular, for the raw and processed chromatogram analysis on page 4, users will be required 
        to download and save the retrieved PSM data from page 3. 
        
        A link to the QuickGO website has been provided so that users can find out more about the 
        biological processes/locations the searched protein is involved in. 


        3. **Raw & Processed Chromatogram Analysis (page 4):**
        
        Users will be able to upload the retrieved PSM data from page 3, raw .mzML files and processed .mzML files
        that correspond to the particular protein that they have searched for. 
                    
        The retrieved PSM data can be used to check the Spectrum File column to see which .mzML files in the raw 
        and processed directory are to be uploaded into the web app for the searched protein.
        
        For each uploaded raw and processed .mzML, three different chromatograms will be visualised: TIC, BPC and XIC. 
        The chromatograms have been designed to be interactive in nature. 
        If only MS1 is detected, then only MS1 chromatogram will be displayed.
        If both MS1 and MS2 scans are detected, then both chromatograms will be shown.
        A table of the time and intensity values plotted on the chromatograms will also be displayed for each scan detected. 
        
        For the XIC, users will be able to select between MS1 and MS2 scans (if detected) and input the 
        mass window. Using the retrieved PSM data from page 3, they will be able to use the m/z value in the 
        m/z column that corresponds to the .mzML files in the Spectrum File column to set the target m/z value. 
        The data table of the plotted values will automatically update when the user inputs the target m/z and
        the mass window values. 
                    
        Users will be able to download and save the chromatograms as a static .png file and the data table(s) as .csv files. 
        If they make any changes to the chromatograms using the interactive features, then these changes can also be saved.  
                    
                    
        

                             
        **Special Thanks to:**
        
         *Dr. Amanda Pearce*
                    
         *Dr. Jedd Bellamy-Carter*
                    
        *Chemistry Department, Loughborough University.* 
    """)
        
    
    with right_column:
        st.image("https://static.wixstatic.com/media/f3d98f_65795a2c349a4a5bb80a9d7b64de176a~mv2.png/v1/fill/w_235,h_135,al_c,q_85,usm_0.66_1.00_0.01,enc_auto/Pearce%20Polymer%20Group%20Logo%20v3-01.png") 
        st.write("For further information about this project, please contact:")
        st.write("Dr. Amanda Pearce")
        st.write("Chemistry Department, Loughborough University")
        st.write("Email: a.pearce@lboro.ac.uk")
        
        st.write("Once you have finished using this app, we would really appreciate your feedback!")
        st.write("You can send your detailed feedback/comments to the email address above. Thank you!")
