###########################
# F333290 - H.Joshi        #
# Date Created: 29/07/2024 #
# Last Updated: 07/08/2024 #
###########################

'''
Streamlit Web App for ProteoSpark - Proteomics Data Analysis Tool for DIA Spectrometry

The purpose of this web app is to facilitate further data analysis of exported PeptideShaker Reports
as part of a pre-existing proteomics data processing pipeline for DIA Spectrometry. 

App Structure:

home_page():   Explains the functionality of the web app to the user 

second_page(): Allows users to conduct detailed analysis of the uploaded reports by using 
               the interactive Aggrid table and by calculating and visualising the count and percentages
               of the report table columns using pie charts and heatmaps

third_page():  Users will be able to conduct quick analysis here by searching for a protein Main Accession Code
               and retrieve the associated peptides and PSMs for that protein

fourth_page(): Users will be able to upload a .mzML file from the processed directory to visualise TIC, BPC and XIC chromatograms.
               For visualising the XIC, they will need to save the retrieved PSM data from page 3 as a .csv file so
               that they can input the m/z value for that .mzML file as the target m/z value. 
               They will be able to also specify the RT Window value as well. 
'''

# Importing modules required for this script
import streamlit as st
import sqlite3
import pandas as pd
import numpy as np 
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode
import plotly.express as px
from pyteomics import mzml



# Setting up the page configuration for the web app
st.set_page_config(page_title = "ProteoSpark", layout = "wide")


def save_tables_to_db(table_name, df):
    '''
    Function for saving a dataframe to a data table in the peptideshaker_reports.db . 

    Parameters:
    table_name (str): name of the data table
    df (pandas.DataFrame): to be saved to the data table
    '''
    connection = sqlite3.connect("peptideshaker_reports.db", check_same_thread = False)
    df.to_sql(table_name, connection, if_exists = "replace", index = False)
    connection.close()


def retrieve_tables_from_db(table_name):
    '''
    Function for retrieving and storing data to a dataframe from a table in peptideshaker_reports.db using SQL query. 
    
    Parameter:
    table_name (str): name of the data table 

    Returns:
    df (pandas.DataFrame): contains the retrieved data from a data table 
    '''
    connection = sqlite3.connect("peptideshaker_reports.db", check_same_thread = False)
    df = pd.read_sql(f"SELECT * FROM {table_name}", connection)
    connection.close()
    return df


def retrieve_table_names():
    '''
    Function for retrieving all names of the data tables stored in peptideshaker_reports.db using SQL query.

    Returns:
     list of str: list of data table names
    '''
    connection = sqlite3.connect("peptideshaker_reports.db", check_same_thread = False)
    cursor = connection.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type ='table';")
    tables = cursor.fetchall()
    connection.close()
    return [table[0] for table in tables] 


def tic_chromatograms(file_reader):
    '''
    Function for calculating TIC values from the scan data extracted from .mzML files.

    A dictionary called tic is created. The keys are the MS level and the associated values are the 
    dictionaries containing the time values and intensity values. 

    The m/z values and intensity values are retreived directly from the scans and converted into numpy arrays. 
    To calculate the tic_value, all intentsity values are totaled and stored in the tic dictionary. 

    Parameter:
    file_reader (object): for accessing the scan data from the .mzML file 

    Returns:
    tic (dictionary): storing the time values and intensity values for a MS level of a scan
    '''
    
    # Creating a empty dictionary for the TIC time and intensity values 
    tic = {}
    # Resetting file_reader so that it reads the .mzML file from the start
    file_reader.reset()
    
    # For loop for iterating through each scan in the .mzML file 
    for scan in file_reader:
        # Retrieving the MS level of each scan 
        ms_level = scan["ms level"]
        # Initialising time and intensity values as empty lists if the MS level does not exist in tic dictionary 
        if ms_level not in tic:
            tic[ms_level] = {"time values": [], "intensity values": []}
        
        # Appending scan start time to the list of time values for the MS level in tic dictionary
        scan_time = scan["scanList"]["scan"][0]["scan start time"]
        tic[ms_level]["time values"].append(scan_time)
        
        # TIC calculations
        # Retrieving m/z values from scan data and converting them into a numpy array
        mz_values = np.array(scan.get("m/z array", []))
        # Retrieving intensity values from scan data and converting them into a numpy array 
        intensity_values = np.array(scan.get("intensity array", []))
        # Calculating the sum of all intensity values in the numpy array
        tic_value = np.sum(intensity_values)
        # Appending the tic_value to the intensity values for the MS level in the tic dictionary 
        tic[ms_level]["intensity values"].append(tic_value)
    
    # For loop for iterating through each MS level in the tic dictionary 
    # Converting lists of time values and intensity values into numpy arrays 
    for ms_level in tic:
        tic[ms_level]["time values"] = np.array(tic[ms_level]["time values"])
        tic[ms_level]["intensity values"] = np.array(tic[ms_level]["intensity values"])
    
    return tic


def bpc_chromatograms(file_reader):
    '''
    Function for calculating BPC values from the scan data extracted from .mzML files.

    A dictionary called bpc_dict is created. The keys are the MS level and the associated values are the 
    dictionaries containing the list of the time values and intensity values. The time and intensity values
    list are then converted into numpy arrays. 

    The base peak intensity is calculated and stored in the intensity values list. 

    Parameter:
    file_reader (object): for accessing the scan data from the .mzML file 

    Returns:
    bpc_dict (dictionary): storing the time values and intensity values for a MS level of a scan 
    '''
    # Creating a empty dictionary for the BPC time and intensity values 
    bpc_dict = {}
    # Resetting file_reader so that it reads the .mzML file from the start
    file_reader.reset()
    
    # For loop for iterating through each scan in the .mzML file
    for scan in file_reader:
        # Retrieving the MS level of each scan
        ms_level = scan["ms level"]
        # Initialising time and intensity values as empty lists if the MS level does not exist in bpc_dict 
        if ms_level not in bpc_dict:
            bpc_dict[ms_level] = {"time values": [], "intensity values": []}
         # Appending scan start time to the list of time values for the MS level in bpc_dict
        scan_time = scan["scanList"]["scan"][0]["scan start time"]
        bpc_dict[ms_level]["time values"].append(scan_time)
        
        # Retrieving scan data intensity values and converting them into numpy arrays
        intensity_values = np.array(scan.get("intensity array", []))
        # If there intensity values exist, then the maximum base peak intensity value will be found 
        if len(intensity_values) > 0:
            base_peak_intensity = np.max(intensity_values)  # Maximum intensity value
        # If not, then base peak intensity will be set to zero
        else:
            base_peak_intensity = 0
        # Appending base peak intensity to the list of intensity values for each MS level in the bpc dictionary 
        bpc_dict[ms_level]["intensity values"].append(base_peak_intensity)
    
    # For loop for iterating through each MS level in bpc_dict and converting time and intensity values list into numpy arrays 
    for ms_level in bpc_dict:
        bpc_dict[ms_level]["time values"] = np.array(bpc_dict[ms_level]["time values"])
        bpc_dict[ms_level]["intensity values"] = np.array(bpc_dict[ms_level]["intensity values"])
    
    return bpc_dict


def xic_chromatograms(file_reader, target_mz, rt_window):
    '''
    Function for calculating the XIC values from scan data in .mzML files. 

    A dictionary called xic is created. The keys are the MS level and the associated values are the 
    dictionaries containing the list of the time values and intensity values. 

    The m/z values are filterd based on the closeness to the target_mz and if it is within the rt_window range. 
    The sum of these m/z values are then calculated and appended to the intensity values list in xic dictionary.

    Both the time values and intensity values lists are then converted into numpy arrays. 

    Parameters:
    file_reader (object): for accessing the scan data from the .mzML file 
    target_mz (float): user inputs the mass to charge ratio of the ion for which xic is being extracted 
    rt_window (float): user specifying the range around the target_mz before totaling all intensity values 
    
    Returns:
    xic (dictionary):  storing the time values and intensity values for a MS level of a scan 
    '''
    # Creating a empty dictionary for the XIC time and intensity values 
    xic = {}
    # Resetting file_reader so that it reads the .mzML file from the start
    file_reader.reset()
    
    # For loop for iterating through each scan in the .mzML file
    for scan in file_reader:
        # Retrieving the MS level of each scan
        ms_level = scan["ms level"]
        # Initialising time and intensity values as empty lists if the MS level does not exist in xic dictionary 
        if ms_level not in xic:
            xic[ms_level] = {"time values": [], "intensity values": []}
        # Appending scan start time to the list of time values for the MS level in xic dictionary
        scan_time = scan["scanList"]["scan"][0]["scan start time"]
        xic[ms_level]["time values"].append(scan_time)
        
        # Retrieving m/z and intensity values from scan data and converting them into numpy arrays 
        mz_values = np.array(scan.get("m/z array", []))
        intensity_values = np.array(scan.get("intensity array", []))

        # Filtering m/z values which are close to the target_mz and within the rt_window
        mz_filter = (mz_values >= target_mz - rt_window) & (mz_values <= target_mz + rt_window)
        # Calculating the sum of all the intensity values which match the retrieved m/z values and are within the rt_window range 
        xic_value = np.sum(intensity_values[mz_filter]) 
       # Appending the xic_value to the intensity values list for each MS level in the xic dictionary 
        xic[ms_level]["intensity values"].append(xic_value)
    # For loop for iterating through each MS level in xic dictionary and converting time and intensity values list into numpy arrays 
    for ms_level in xic:
        xic[ms_level]["time values"] = np.array(xic[ms_level]["time values"])
        xic[ms_level]["intensity values"] = np.array(xic[ms_level]["intensity values"])
    
    return xic

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
                     
        1. **Detailed Analysis (page 2):**
        
        Users will be able to upload PeptideShaker reports into interactive tables. 
        They will be able to perform basic data cleaning operations on the raw data such as:
        filtering, grouping and deleting columns and saving these changes to a new Excel file. 
        They will also be able to conduct basic statistics and visualisations such as: count, percentages, 
        pie charts and heatmaps on the uploaded raw data.
         
        2. **Quick Analysis (page 3):**
        
        Users will be required to specifically upload the PeptideShaker Protein and PSM reports ('.xlsx').
        Using a form widget, users will be able to input a main accession code for a protein that
        is in both the Protein & PSM reports (raw uncleaned data files). 
        The form will then retrieve the data on the associated peptides and PSMs for a particular protein.
        Users will be able to download and save the retrieved data as .csv files.  
                    
        3. **Chromatogram Analysis (page 4):**
        
        Using the retrieved Default PSM Report from page 3, users can then upload .mzML files from 
        the processed directory that correspond to the particular protein main accession code they had 
        searched for. Using a tab layout, three different chromatograms (TIC, BPC & XIC) along with a table
        of the time and intensity values plotted on the chromatograms will be displayed.
        The chromatograms have been designed to be interactive in nature. 

        For the XIC, users will be able to upload the saved Default PSM Report as a .csv file from page 3. 
        They will be able to use the m/z value in the m/z column that corresponds to the .mzML file in the 
        Spectrum File column to set the target m/z value. They will also be able to set the RT window as well.
        The data table of the plotted values will automatically update when the user inputs the target m/z and
        the RT window values. 
                    
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


def second_page():
    '''
    Function for making the Detailed Ananlysis page in the web app.

    Users will be able to upload multiple Excel files which will be saved to the sqlite database. 
    They will be able to use the interactive features of the table to conduct basic cleaning and manipulation of the data. 

    They will also be able to calculate column counts and percentages and create pie charts and heatmaps on the raw uncleaned data. 
    '''
   
    st.title("Detailed Analysis: Interactive Data Tables")
    # Creating a widget for users to upload multiple Excel files
    excel_tables = st.file_uploader("Upload Excel files here", type = ["xlsx"], accept_multiple_files = True)
    
   # Checking for and processing uploaded '.xlsx' files
    if excel_tables:
        for table in excel_tables:
            # Reading excel file as dataframe
            df = pd.read_excel(table, engine = "openpyxl")
            # Extracting the file name without the extension to create the table_name 
            table_name = table.name.split('.')[0]
            # Saving the dataframe and the updated table_name to the peptideshaker_reports.db 
            save_tables_to_db(table_name, df)
            st.write(f"Table: {table_name} has been successfully saved to the sqlite database.")

    # Connecting to the sqlite database to query and retrieve all table names
    connection = sqlite3.connect("peptideshaker_reports.db", check_same_thread = False)
    cursor = connection.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    # Closing the connection once finished querying 
    connection.close()
    
    # For loop for iterating through each table_name 
    for table_name in tables:
        table_name = table_name[0]
        st.write(f"### {table_name}")
        # Retrieving the dataframe of the retrieved table_name 
        df = retrieve_tables_from_db(table_name)

    
        # Configuring the Aggrid table grid options
        grid_options_builder = GridOptionsBuilder.from_dataframe(df)
        
       
        # Configuring pagination and interactive column settings (filtering, sorting, editing, resizing) in the Aggrid table 
        grid_options_builder.configure_pagination(paginationPageSize=10)
        grid_options_builder.configure_default_column(filterable = True, sortable = True, editable = True,resizable = True)

        # Creating the Aggrid grid options using the configured settings
        grid_options = grid_options_builder.build()
        
        # Configuring extra settings for columns and for grouping columns in the Aggrid table 
        grid_options.update({
            "columnDefs": [{"field": col,"editable": col} for col in df.columns],
            "defaultColDef": {
                "flex": 1,
                "filter": True,
                "floatingFilter": True,
                "sortable": True,
                "resizable": True,
                "enableRowGroup": True
            },
            "autoGroupColumnDef": {
                "minWidth": 150,
                "filter": "agGroupColumnFilter",
                "resizable": True
            },
            "rowGroupPanelShow": "always"
        })

        # Displaying a dataframe of the table as an interactive Aggrid table
        # If there are any changes made to the table, the table will show these changes when viewed 
        grid = AgGrid(
            df,
            gridOptions = grid_options,
            editable = True,
            fit_columns_on_grid_load = True,
            theme="alpine",
            update_mode = GridUpdateMode.VALUE_CHANGED
        )
        
        # Using columns to calculate the frequency and perentages of the data 
        st.write("#### Calculated Column Counts & Percentages on the uploaded raw data")
        calculate_columns = df.select_dtypes(include = "object").columns
        
        # If there are columns which contain categorical data, then a dropdown menu is displayed
        if calculate_columns.size > 0:
            select_column = st.selectbox("Choose a column from the above table to see counts & percentages:", calculate_columns)

            # For the user selected column, frequency counts and percentages are shown and displayed as a dataframe
            if select_column:
                frequency = df[select_column].value_counts()
                percentages = (frequency / frequency.sum() * 100).round(2).astype(str) + '%'
                calculation_df = (pd.DataFrame({"Count": frequency, "Percentage": percentages}))
                st.dataframe(calculation_df, use_container_width = True)

                # Creating a dictionary to create a dataframe with three columns (category, count and percentage) 
                data_plot = pd.DataFrame({
                    "Category": frequency.index,
                    "Count": frequency.values,
                    # Percentages have been rounded to 2 d.p 
                    "Percentage": (frequency / frequency.sum() * 100).round(2)  
                })
                
                # Creating a pie chart to display the percentages shown in the dataframe
                fig = px.pie(data_plot, names = "Category", values = "Count",
                             title = f"Pie Chart showing the distribution of {select_column}", hover_data = {"Percentage": True})
                st.plotly_chart(fig)

                # Creating heatmaps to visualise the data from the Aggrid table 
                st.write("### Heatmaps of the uploaded raw data")
                columns = df.columns
                
                # Creating a dropdown menu for the user to select the columns required for the heatmap 
                heatmap_column_1 = st.selectbox("Please select the column for the y axis:", calculate_columns)
                heatmap_column_2 = st.selectbox("Please Choose the column for the x axis:", calculate_columns)
                
                # Selecting columns with hold numeric data in the dataframe 
                # Filtering and listing the names of those selected numeric columns that have actual valid values 
                numeric_actual_columns = df.select_dtypes(include = "number").columns
                numeric_not_empty_columns = [col for col in numeric_actual_columns if df[col].notnull().any()]
                
                # Creating a dropdown menu for the user to select the column values for the heatmap
                actual_value_column = st.selectbox("Please select the values of the column you want to show:", numeric_actual_columns)


                if heatmap_column_1 and heatmap_column_2 and actual_value_column:
                    # Checking whether the user selected columns for the x and y axis are different from each other
                    if heatmap_column_1 != heatmap_column_2:
                           # Converting the data in the actual_value_column to a numeric data type
                           # Any values in the actual_value_column that cannot be changed to numeric is converted to NaN
                           # If the actual_value_column has numerical values, then a True result is returned otherwise False
                           # If the boolean series has one True result, then True is returned otherwise False 
                           if pd.to_numeric(df[actual_value_column], errors = "coerce").notna().any():
                                    # Creating a pivot table of the dataframe 
                                    heatmap_data = df.pivot_table(
                                        # Using the two selected columns to create the rows and columns of the pivot table
                                        index = heatmap_column_1,
                                        columns = heatmap_column_2,
                                        # Using the values of the actual_value_column to fill the cells of the pivot table 
                                        values = actual_value_column,  
                                        # Replacing any missing values with zero in the pivot table 
                                        fill_value = 0               
                                )
                                    # Creating and displaying heatmap visualisation
                                    fig_heatmap = px.imshow(
                                        heatmap_data,labels = dict(x = heatmap_column_2, y = heatmap_column_1, color = actual_value_column),
                                        title = f"Heatmap of {heatmap_column_1} versus {heatmap_column_2} based on {actual_value_column}")
                                    st.plotly_chart(fig_heatmap)
                    else:
                        st.warning("Selected columns must be different for heatmap visualisation!")
                else:
                    st.warning(f"{actual_value_column} should have numeric data and must not be empty.")
                            

def third_page():
    ''''
    Function for making the Quick Analysis page in the web app. 

    Users will be required to upload two PeptideShaker reports in Excel file format (Default PSM and Protein Report) 
    which will be saved into the peptideshaker_reports.db. 
    
    Using a form widget, the Main Accession Code for a particular protein can be typed and submitted. 
    The revelant data on the protein and its associated peptides and PSMs can then be retrieved from 
    the Default Protein & PSM Reports stored in the sqlite database. 
    '''
    st.title("Quick Analysis: Retrieving data on Proteins and their associated peptides and PSMs")
    
    # Creating a wigdet for uploading the Default Protein & Default PSM Reports
    excel_reports = st.file_uploader("Upload Excel files here", type = ["xlsx"], accept_multiple_files = True)
    
    # Checking for and processing uploaded '.xlsx' files 
    if excel_reports:
        for report in excel_reports:
            # Reading excel file as dataframe
            df = pd.read_excel(report, engine = "openpyxl")
            # Extracting the filename without the file extension
            report_name = report.name.split('.')[0]
            # Saving the dataframe with the report name as the name of the table in the database
            save_tables_to_db(report_name, df)
            st.write(f"Table: {report_name} been successfully saved to the sqlite database.")


    # Retrieving a list of table_names  
    table_names = retrieve_table_names()

    # Creating a form widget for the user to input the Main Accession code for a particular protein
    with st.form(key = "protein_peptide_psm_form"):
        st.write("### Protein-Peptides-PSM Data Retrieval Form")
        # Creating dropdown menus to select the Protein and PSM reports from the list of table names in the database 
        psm_table = st.selectbox("Please select the PSM Report:", options = table_names)
        protein_table = st.selectbox("Please select the Protein Report:", options = table_names)

        # Creating an input box to enter the protein Main Accession code into the form       
        input_accession = st.text_input("Please enter the protein Main Accession code below:")
        # Creating a button to submit the input into the form 
        submit_input_button = st.form_submit_button(label = "Submit")

        # If the submit button was pressed and an input was entered, then the web app connects to the sqlite database      
        if submit_input_button and input_accession:
            connection = sqlite3.connect("peptideshaker_reports.db", check_same_thread = False)
                    
            # Retrieving data from the protein_table (Protein Report) based on the user inputted Main Accession code
            query_protein = f"""
            SELECT * FROM {protein_table}
            WHERE "Main Accession" = ?;
            """
            default_protein_df = pd.read_sql(query_protein, connection, params = (input_accession,))
            
            # Retrieving data from the psm_table (PSM Report) based on user inputted Accession code
            query_psm = f"""
            SELECT * FROM {psm_table}
            WHERE "Protein(s)" LIKE ?;
            """
            default_psm_df = pd.read_sql(query_psm, connection, params=(f"%{input_accession}%",))

            # Closing the connection to the database once finished querying      
            connection.close()
        
            # Displaying retrieved data from the protein_table for a particular protein only if dataframe is not empty
            if not default_protein_df.empty:
                st.write("### Retrieved from Default Protein Report")
                st.dataframe(default_protein_df, use_container_width = True)
            else:
                st.warning("No data in the data tables has been found for the inputted Main Accession code.")

            # Displaying associated peptides and PSMs for a particular protein only is dataframe is not empty
            if not default_psm_df.empty:
                st.write("### Retrieved from Default PSM Report")
                st.dataframe(default_psm_df, use_container_width=True)
                st.info("""
                        The number of Validated PSMs retrieved from the Default Protein Report should 
                        match the number of rows retrieved from the Default PSM Report.
                
                        E.g. Accession code P01859 has 66 validated PSMs (as seen in the Default Protein Report) 
                        and the Default PSM Report has 66 rows.
                        
                        In the Default PSM table,the rows index starts from zero rather than one so there are 65 rows 
                        but this actually represents 66 validated PSMs.
                    """)
                
                st.info("""
                            For chromatogram visualisation, please save the retrieved Default PSM Report by
                            clicking on the 'Download As CSV' toggle at the top of the specified table. 
                            
                            This .csv file can then be uploaded for chromatogram analysis on page 4.             
                        """) 
            else:
                st.warning("Associated peptides and PSMs cannot be found for the inputted Main Accession code")           
        else:
            st.info("Please upload the following PeptideShaker reports here for analysis: Default Protein Report & Default PSM Report.")
            st.info("If these reports have been uploaded previously on page 2, then there is no need to upload them here again.")

            
def fourth_page():
    '''
    Function for making the Chromatogram Analysis page in the web app. 

    Users will be able to upload a .mzML file from the processed directory which corresponds to the protein Main Accession Code 
    which was searched on the quick analysis page. 

    Three types of interactive chromatograms will be displayed: TIC, BPC, XIC. 
    All visualisations will be supported by a dataframe table which shows the plotted data points in the chromatogram 

    For XIC chromatogram, the retrieved PSM data for a searched protein can be saved as a .csv file
    and uploaded into the XIC tab to use the m/z value for the .mzML file as the target m/z value to input.  
    The user will also be able to input the RT Window value as well. 

    Raises:
    Exception/Error - when there is an issue with the .mzMl file or .csv file upload
    '''
    
    st.title("Chromatogram Analysis using Processed .mzML files")

    # Creating a widget for uploading a .mzML file from the processed directory
    spectrum_file = st.file_uploader("Upload .mzML file here", type = ["mzml"], accept_multiple_files = False)
    
    # Checking whether the .mzML file has been uploaded
    if spectrum_file is not None:
        # If yes, then the filename is retrieved and the .mzML file is read
        try:
            file_name = spectrum_file.name
            read_spectrum_file = mzml.read(spectrum_file, use_index = True)
            
            # Generating TIC by reading the .mzML file
            generate_tic = tic_chromatograms(read_spectrum_file)
            # Generating BPC by reading the .mzML file 
            generate_bpc = bpc_chromatograms(read_spectrum_file)
            
            # Selecting the MS level for the scans - default is MS2 
            ms_level = 2  

            # If the MS level exists in the tic and bpc dictionaries, the time and intensity values for both chromatograms are retrieved 
            if ms_level in generate_tic and ms_level in generate_bpc:
                tic_rt = generate_tic[ms_level]["time values"]
                tic = generate_tic[ms_level]["intensity values"]
                bpc_rt = generate_bpc[ms_level]["time values"]
                bpc = generate_bpc[ms_level]["intensity values"]
                
                # Creating dataframes of the time and intensity values plotted for the TIC & BPC chromatograms
                # Done for user reference when the chromatograms become hard to interpret  
                tic_df = pd.DataFrame({"Time": tic_rt,"TIC": tic})
                bpc_df = pd.DataFrame({"Time": bpc_rt,"BPC": bpc})

                # Creating and displaying an interactive TIC chromatogram for the uploaded .mzML file 
                # Configuring the axis, axis labels, chart title, markers, hover tooltips
                fig_tic = px.line(tic_df, x = "Time", y = "TIC",
                    labels = {"Time": "Time","TIC": "Intensity"},
                    title = f"Total Ion Chromatogram for {file_name}",
                    markers = True,
                    hover_data = {"Time": True, "TIC": True})
                # Configuring y axis to be written in scientific notation 
                fig_tic.update_layout(yaxis = dict(tickformat = ".1e"))

                
                # Creating and displaying an interactive TIC chromatogram for the uploaded .mzML file 
                # Configuring the axis, axis labels, chart title, markers, hover tooltips
                fig_bpc = px.line(bpc_df, x = "Time", y = "BPC",
                labels = {"Time": "Time", "BPC": "Intensity"},
                title = f"Base Peak Chromatogram for {file_name}",
                markers = True,
                hover_data = {"Time": True, "BPC": True})
                # Configuring y axis to be written in scientific notation 
                fig_bpc.update_layout(yaxis = dict(tickformat = ".1e"))
                
                # Tab layout for the three chromatogram plots
                tic_tab, bpc_tab, xic_tab = st.tabs(["TIC Chromatogram", "BPC Chromatogram", "XIC Chromatogram"])

                # USing columns to layout the TIC Tab
                with tic_tab:
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        # Displaying the TIC plot on the left side of the page
                        st.plotly_chart(fig_tic, use_container_width = True)
                    with col2:
                        # Displaying the dataframe of the TIC data points on the right side of the page
                        st.subheader("TIC Data Points")
                        st.dataframe(tic_df)
                
                # Using columns to layout the BPC tab
                with bpc_tab:
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        # Displaying the BPC plot on the left side of the page
                        st.plotly_chart(fig_bpc, use_container_width = True)
                    with col2:
                        # Displaying the dataframe of the BPC data points on the right side of the page
                        st.subheader("BPC Data Points")
                        st.dataframe(bpc_df)
                
                
                # Layout for XIC Tab
                with xic_tab:
                    st.info("""
                            Please upload the Default PSM Report for a particular protein 
                            that you have downloaded and saved from page 3 into the file uploader below. 

                            * Only one .csv file at a time can be uploaded here. 

                            In the retrieved Default PSM Report, there are two columns: Spectrum File and m/z which are of importance. 

                            Users can search through the Spectrum File column to find the revelant .mzML files in the 
                            processed directory that corresponds to a particular protein main accession code.

                            Then for a particular .mzML file, the corresponding m/z value can then be used as an
                            input for the target m/z value. 
                            
                            The user can then decide on the RT Window they wish to analyse.

                            An interactive XIC chromatogram with a table of the data points plotted will be displayed. 
                         """)

                    
                    
                    # Creating a widget for uploading the .csv file of the retrieved Default PSM Report from page 3
                    upload_csv = st.file_uploader("Upload .csv file here", type =["csv"], accept_multiple_files = False)
                    
                    # Checking if .csv file has been uploaded 
                    if upload_csv is not None:
                        # If uploaded, .csv file is read and converted to pandas dataframe
                        # Otherwise, an error would be displayed 
                        try:
                            retrieved_psm_df = pd.read_csv(upload_csv)
                            st.dataframe(retrieved_psm_df)
                        except Exception as e:
                            st.error(f"Error reading the .csv file: {e}")
        
                    # Creating input boxes for the user to input the target m/z and rt_window for XIC
                    target_mz = st.number_input("Please enter the target m/z value:")
                    rt_window = st.number_input("Please enter the RT window:")
                    
                    # Generating XIC from the read .mzML file, target_mz and rt_window
                    generate_xic = xic_chromatograms(read_spectrum_file, target_mz, rt_window)
                   
                    # Retrieving the time and intensity values for the specified MS level from the generated XIC data
                    xic_rt = generate_xic[ms_level]["time values"]
                    xic = generate_xic[ms_level]["intensity values"]
                    
                    # Creating dataframe of the time and intensity values plotted for the XIC chromatogram
                    # Done for user reference when the chromatogram become hard to interpret  
                    xic_df = pd.DataFrame({"Time": xic_rt, "XIC": xic})
                    
                    # Creating and displaying an interactive XIC chromatogram for the uploaded .mzML file 
                    # Configuring the axis, axis labels, chart title, markers, hover tooltips
                    fig_xic = px.line(xic_df, x = "Time", y = "XIC",
                        labels = {"Time": "Time", "XIC": "Intensity"},
                        title = f"Extracted Ion Chromatogram (m/z = {target_mz}) for {file_name}",
                        markers = True,
                        hover_data = {"Time": True, "XIC": True})
                    # Configuring y axis to be written in scientific notation 
                    fig_xic.update_layout(yaxis = dict(tickformat = ".1e"))
                    
                    # Using columns to layout the XIC tab
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        # Displaying the XIC plot on the left side of the page
                        st.plotly_chart(fig_xic, use_container_width = True)
                    with col2:
                        # Displaying the dataframe of the XIC data points on the right side of the page
                        st.subheader("XIC Data Points")
                        st.dataframe(xic_df)

            else:
                st.warning(f"No data has been found for MS level: {ms_level}.")
                
        except Exception as e:
            st.error(f"Error occured when uploading .mzMLL file: {e}")
    else:
        st.info("This file uploader will only accept one .mzML file at a time for chromatogram visualisation.")


# Sidebar Page Menu Configuration 
st.sidebar.title("Page Navigation")
menu = st.sidebar.selectbox("Click to go to", ["Home", "Page 2: Detailed Analysis", "Page 3: Quick Analysis", "Page 4: Chromatogram Analysis"])

# Creating a dropdown menu to select the page the user wants to navigate to
if menu == "Home":
    home_page()
elif menu == "Page 2: Detailed Analysis":
    second_page()
elif menu == "Page 3: Quick Analysis":
    third_page() 
elif menu == "Page 4: Chromatogram Analysis":
    fourth_page()


