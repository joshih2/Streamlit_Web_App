###########################
# F333290 - H.Joshi        #
# Date Created: 29/07/2024 #
# Last Updated: 17/08/2024 #
###########################

'''
third_page.py 

This module corresponds to the Protein-Peptides-PSMs Data Retrieval Form page (page 3) in the ProteoSpark Streamlit Web App. 

Please refer to app.py for a detailed description of this module.

Functions: 
def save_tables_to_db(table_name, df) - saving dataframe to a sqlite table in the database 
def retrieve_tables_from_db(table_name) - retrieving and storing data to a dataframe from sqlite tables
def retrieve_table_names() - retrieving all table names in the sqlite database
def third_page() - displaying the Protein-Peptides-PSMs Data Retrieval Form page within the streamlit web app 

Parameters:
table_name (str): name of the data table
df (pandas.DataFrame): to be saved to the data table
 
Returns:
df (pandas.DataFrame): contains the retrieved data from a data table 
'''

# Importing libraries & modules required for this module
import streamlit as st
import sqlite3
import pandas as pd
import os

# Defining the database directory which stores the sqlite db
sqlite_db_path = "database/peptideshaker_reports.db"
database_filepath = "database"

# Ensuring that the database directory exists
if not os.path.exists(database_filepath):
    os.makedirs(database_filepath)


def save_tables_to_db(table_name, df):
    '''
    Function for saving a dataframe to a data table in the peptideshaker_reports.db . 

    Parameters:
    table_name (str): name of the data table
    df (pandas.DataFrame): to be saved to the data table
    '''
    connection = sqlite3.connect(sqlite_db_path, check_same_thread = False)
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
    connection = sqlite3.connect(sqlite_db_path, check_same_thread = False)
    df = pd.read_sql(f"SELECT * FROM {table_name}", connection)
    connection.close()
    return df

def retrieve_table_names():
    '''
    Function for retrieving all names of the data tables stored in peptideshaker_reports.db using SQL query.

    Returns:
     list of str: list of data table names
    '''
    connection = sqlite3.connect(sqlite_db_path, check_same_thread = False)
    cursor = connection.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type ='table';")
    tables = cursor.fetchall()
    connection.close()
    return [table[0] for table in tables] 


def third_page():
    ''''
    Function for making the Protein-Peptides-PSMs Data Retrieval Form on the third page of the web app. 

    Users will be required to upload two PeptideShaker reports in Excel file format (Default PSM and Protein Report) 
    which will be saved into the peptideshaker_reports.db. 
    If the reports already exist, then they will be asked to select the reports they want to search and retrieve data from. 

    Users will be asked to select from a dropdown menu that has already been pre-populated with descriptions of proteins.
    This is automatically populate the dropdown menu for the main accession code associated with the selected protein description. 
    The form will then retrieve the revelant data on the protein and its associated peptides and PSMs from the 
    Default Protein & PSM Reports stored in the sqlite database. 
    '''
    st.title("Protein-Peptides-PSMs Data Retrieval Form")

    with st.expander("### ℹ️ Information"):
            st.write("""
                     Firstly, please upload the following PeptideShaker Reports: Default Protein Report and Default PSM Report
                     separately into the assigned file uploaders in the sidebar. 
                     The file uploaders will only be able to accept one Excel file at a time.
                     The uploaded files will be saved to a sqlite database. 
                     
                     Note: Please refresh the page and you will see that the Description dropdown menu will automatically populate with the descriptions of proteins.
                     
                     Note: If these two PeptideShaker reports were previously uploaded on page 2, then there is no need to re-upload them here again.
                     As the reports aready exist in the sqlite database, you will need to select the Protein and PSM report filenames 
                     manually from the dropdown menu and then only will the Description dropdown menu will be populated. 

                     Once the Description column is selected, the protein Main Accession code associated with a protein will be
                     automatically populated in the dropdown menu. 

                     Then click the Submit Button and you will be able to view the data on the proteins and the associated peptides and PSMs 
                     retrieved from both the Default Protein & PSM Report.

                     You will able to save the retrieved Default PSM Report by clicking on the 'Download As CSV' toggle at the top of the specified table. 
                     This .csv file can then be uploaded for the raw & processed chromatogram analysis on page 4.  

                     Note: If you need to delete an uploaded PeptideShaker report here on page 3, please go back to page 2 and 
                     follow the instructions in the information tab to learn more this process. The selected table marked for
                     deletion on page 2 will reflect on page 3 as the table will be removed from the sqlite database.            
                """)
            
 
    st.sidebar.subheader("If required, please upload the following PeptideShaker files for the retrieval form here:")
    
    # Creating two separate file uploader widgets which can only accept one file at a time 
    protein_excel_report = st.sidebar.file_uploader("PeptideShaker Default Protein Report",type = ["xlsx"], accept_multiple_files = False)

    psm_excel_report = st.sidebar.file_uploader("PeptideShaker Default PSM Report", type = ["xlsx"], accept_multiple_files = False)
    
    # Connecting the the sqlite database for table name and data retrieval
    connection = sqlite3.connect(sqlite_db_path, check_same_thread = False)

    # Checking for and processing the uploaded Default Protein Report
    if protein_excel_report:
        # Reading the uploaded protein report excel file into a dataframe
        df_protein_report = pd.read_excel(protein_excel_report, engine = "openpyxl")
        # Extracting the filename without the file extension 
        protein_report_name = protein_excel_report.name.split('.')[0]
        # Saving the dataframe with the extracted name as the name of the table in the database
        save_tables_to_db(protein_report_name, df_protein_report)
        st.write(f"Uploaded Report {protein_report_name} has been successfully saved to the sqlite database.")

    else:    
        # Retrieving a list of table_names  
        table_names = retrieve_table_names()
        # Selecting the table name from a dropdown menu of existing tables found in the database 
        protein_table_name = st.selectbox("Please select the Default Protein Report from the sqlite database", options = table_names)

    # Checking for and processing the uploaded Default PSM Report
    if psm_excel_report:
        # Reading the uploaded PSM report excel file into a dataframe
        df_psm_report = pd.read_excel(psm_excel_report, engine = "openpyxl")
        # Extracting the filename without the file extension 
        psm_report_name = psm_excel_report.name.split('.')[0]
        # Saving the dataframe with the extracted name as the name of the table in the database
        save_tables_to_db(psm_report_name, df_psm_report)
        st.write(f"Uploaded Report {psm_report_name} has been successfully saved to the sqlite database.")

    else:
        # Retrieving a list of table_names   
        table_names = retrieve_table_names()
        # Selecting the table name from a dropdown menu of existing tables found in the database 
        psm_table_name = st.selectbox("Please select the Default PSM Report from the sqlite database", options = table_names)
        
        # If a protein report has been selected from dropdown menu, then only the sqlite database is queried 
        if protein_table_name:
            # Selecting & grouping Main Accession column according to the Description column in the selected Protein Report
            query = f"""
            SELECT Description, GROUP_CONCAT([Main Accession]) AS protein_accession_codes
            FROM {protein_table_name}
            GROUP BY Description;
            """
            grouped_protein_df = pd.read_sql(query, connection)
            
            # Checking if the Description column exists in the dataframe
            if "Description" in grouped_protein_df.columns:
                # Identifying unique descriptions in the Description column  
                protein_description = grouped_protein_df["Description"].unique()
                # Creating a dropdown menu for the user to select a protein description from the retrieved unique descriptions
                selected_description = st.selectbox("Please select the description of the protein", options = protein_description)
                # Filtering rows based on the selected description 
                # Extracting a list of individual accession codes from the concatenated string of accession codes 
                accession_codes = grouped_protein_df[grouped_protein_df["Description"] == selected_description]["protein_accession_codes"].values[0].split(',')
                # Creating a dropdown menu for the user to select the associated  main accession code 
                selected_accession_codes = st.selectbox("Please select the protein main accession code", options = accession_codes)

            # If the submit button is clicked, then the following code will be executed:
            if st.button("Submit"):
                # Querying the protein table to retrieve all rows in the table in which the Main Accession column matches the selected accession code 
                query_protein_data = f"SELECT * FROM {protein_table_name} WHERE [Main Accession] = ?;"
                # Reading the SQL query and putting the data into a pandas dataframe 
                read_protein_data = pd.read_sql(query_protein_data, connection, params = (selected_accession_codes,))
                # Querying the psm table to retrieve the rows of the table where the Protein column has the accession code
                query_psm_data = f"SELECT * FROM {psm_table_name} WHERE [Protein(s)] LIKE ?;"
                # Reading the SQL query and putting the data into a Pandas dataframe 
                # Reading the protein main accession code even if there are other accession codes associated with it in the Protein column 
                read_psm_data = pd.read_sql(query_psm_data, connection, params = (f"%{selected_accession_codes}%",))

                # Checking if the protein dataframe is not empty before displaying the datafame with retrieved data
                # Else, warning message will be shown
                if not read_protein_data.empty:
                    st.write("### Retrieved from Default Protein Report")
                    st.dataframe(read_protein_data, use_container_width = True)
                else:
                    st.warning("Data for the selected Main Accession code cannot be found in the Default Protein Report.")

                # Checking if the psm dataframe is not empty before displaying the dataframe with retrieved data 
                # Else, warning message will be shown 
                if not read_psm_data.empty:
                    st.write("### Retrieved from Default PSM Report")
                    st.dataframe(read_psm_data, use_container_width = True)
                else:
                    st.warning("Data for the selected Main Accession code cannot be found in the Default PSM Report.")
        
                # Closing sqlite database connection once data retrieval is done
                connection.close()
                
                st.markdown("""
                           *You can now use the retrieved Main Accession Code to find out more about the cellular location, 
                            molecular and biological processes of the searched protein by visiting the following website:
                            (https://www.ebi.ac.uk/QuickGO/)
                        """)
