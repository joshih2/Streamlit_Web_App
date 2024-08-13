###########################
# F333290 - H.Joshi        #
# Date Created: 29/07/2024 #
# Last Updated: 13/08/2024 #
###########################

'''
Streamlit Web App for ProteoSpark - Proteomics Data Analysis Tool for DIA Spectrometry

The purpose of this web app is to facilitate further data analysis and validation of exported PeptideShaker Reports
as part of a pre-existing proteomics data processing pipeline for DIA Spectrometry. 

App Structure:

home_page():   Explains the functionality of the web app to the user 

second_page(): Allows users to conduct detailed analysis of the uploaded PeptideShaker reports ('.xlsx') by using 
               interactive streamlit tables. They will be able do to basic data cleaning and manipulation operations
               (removing, filtering columns) to update the processed data and subsequent descriptive statistics (count and percentages) 
               and interactive visualisations (pie charts and heatmaps).  
               * Grouping columns will create a new dataframe but will not update the statistics and visualisations. 
               
               Users will be able to download and save the updated tables as a .csv file and visualisations as a static .png file. 
               If they make any changes to the visualisations using the interactive features, then these changes can also be saved.               

third_page():  Users will be able to conduct quick analysis here by searching and retrieving data from 
               uploaded PeptideShaker Default Protein and PSM reports. 
               They will be able to select a protein description from a dropdown menu. 
               The selected protein description will then automatically select the associated protein main accession code.
               The form will then retrieve data from both reports on the proteins and associated peptides and PSMs for the selected protein description.
               
               If users would like to do the raw and processed chromatogram analysis, then they will be required to  
               download and save the retrieved PSM data as .csv file to then upload onto page 4.
               
               A link to the QuickGO website has been provided for users to find out more about the biological role of the searched protein. 

fourth_page(): They will be required to upload the retrieved PSM data from page 3. They can then look through the Spectrum File column
               which shows which .mzML file corresponds to the searched protein. 
               Using this information, users can then search through the raw and processed directory to upload the corresponding 
               raw .mzML and processed .mzML file into the web app.
               
               For each uploaded raw and processed .mzML, three different interactive chromatograms will be visualised: TIC, BPC and XIC. 
               If only MS1 is detected, then only MS1 chromatogram will be displayed.
               If both MS1 and MS2 scans are detected, then both chromatograms will be shown.
               A table of the time and intensity values plotted on the chromatograms will also be displayed for each scan detected. 

               * For the XIC chromatogram, users will be able to select between MS1 and MS2 scans (if detected), input the mass window
               and the target m/z. The target m/z value that corresponds to a uploaded .mzML can be found from the m/z column in the 
               retrieved PSM data from page 3. These changes done by the user will update the subsequent XIC chromatograms and the 
               data table of plotted values. Users will be able to download and save the chromatograms as a static .png file and the 
               data table(s) as .csv files.
               If they make any changes to the chromatograms using the interactive features, then these changes can also be saved.               

'''

# Importing modules required for this script
import streamlit as st

from home_page import home_page
from second_page import second_page
from third_page import third_page
from fourth_page import fourth_page
 

def main():
    '''
    Function for displaying the pages of the web app. 

    The page modules have been imported into this script so that the functions can be executed 
    and the contents of the individual pages can be displayed. 

    The page configuration and navigation has also been set up. 

    If running this script directly from the terminal, then app.py will need to be executed to start the web app.  
    '''
    # Setting up the page configuration for the web app
    st.set_page_config(page_title = "ProteoSpark", layout = "wide")
    
    # Sidebar Page Menu Configuration 
    st.sidebar.title("Page Navigation")
    menu = st.sidebar.radio("Click to go to", ["Home", "Page 2: Interactive Data Tables", "Page 3: Protein-Peptides-PSMs Data Retrieval Form", "Page 4: Raw & Processed Chromatogram Analysis"])
    
    if menu == "Home":
        home_page()
    elif menu == "Page 2: Interactive Data Tables":
        second_page()
    elif menu == "Page 3: Protein-Peptides-PSMs Data Retrieval Form":
        third_page() 
    elif menu == "Page 4: Raw & Processed Chromatogram Analysis":
        fourth_page()

        
if __name__ == "__main__":
    main()