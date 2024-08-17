###########################
# F333290 - H.Joshi        #
# Date Created: 29/07/2024 #
# Last Updated: 17/08/2024 #
###########################

'''
second_page.py 

This module corresponds to the Interactive Data Tables page (page 2) in the ProteoSpark Streamlit Web App. 

Please refer to app.py for a detailed description of this module.

Functions: 
def save_tables_to_db(table_name, df) - saving dataframe to a sqlite table in the database 
def retrieve_tables_from_db(table_name) - retrieving and storing data to a dataframe from sqlite tables
def delete_tables_from_db(table_name) - delating sqlite tables one at a time from within the web app 
def second_page() - displaying the Interactive Data Tables page within the streamlit web app 

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
import plotly.express as px
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


def delete_tables_from_db(table_name):
    '''
    Function for the user to delete tables one at a time from the sqlite database within the web app without writing any sqlite commands. 

    The changes are then reflected in the peptideshaker_reports.db. 

    Parameter:
    table_name (str): name of the data table 

    '''
    connection = sqlite3.connect(sqlite_db_path, check_same_thread = False)
    cursor = connection.cursor()
    cursor.execute(f"DROP TABLE IF EXISTS {table_name}")
    connection.commit()
    connection.close()


def second_page():
    '''
    Function for making the Interactive Data Tables page in the web app.

    Users will be able to upload multiple Excel files which will be saved to the sqlite database. 
    They will be able to conduct basic cleaning and manipulation of the data, calculate column counts and percentages 
    and create pie charts and heatmaps on the cleaned processed data. 

    They will also be able to connect to the sqlite database to remove any data tables one at a time from the sqlite database. 
    '''
    st.title("Interactive Data Tables")

     # Establishing session state for deleted_table process 
    if "deleted_table" not in st.session_state:
        st.session_state.deleted_table = False

    with st.expander("### ℹ️ Information"):
            st.write("""
                     Firstly, please upload the PeptideShaker Reports that you want to further analyse and visualise.
                     The file uploader is be able to accept multiple Excel files. 
                     The uploaded files will be saved to a sqlite database. 
                     
                     You will be able to select the data cleaning operation(s) from the sidebar that you require for the uploaded DataFrame. 
                     The changes you select will be reflected in the uploaded DataFrame table. 
                     You will be able to save the changes you make by hovering at the top right of the table 
                     to download the DataFrame as a .csv file. 
                     
                     When you select Group By Column(s), it will show another DataFrame with the grouped columns.
                     However, grouped columns will only update the Grouped DataFrame and will not update the statistics and visualisations. 
                     You will be able to save the grouped Dataframe by hovering at the top right of the table to download
                     the DataFrame as a .csv file. 
                     
                     Any selections you make in the sidebar will update the contents of the uploaded DataFrame, 
                     and subsequent statistics and visualisations.
                     
                     Note: The files that have been uploaded into the sqlite database will not be updated by any changes made.
                     The updates to the tables are for data analysis and visualisation purposes. 
                     
                     Note: To delete any uploaded files on this page, please select the table name from the pre-populated dropdown menu
                     below the information tab. Then a delete button will appear and once clicked, the selected table will be removed
                     from the sqlite database. The dropdown menu for deleting table(s) will only appear if you have uploaded a file into the web app. 
                     Only one table can be deleted at a time from the dropdown menu. 

                """)
   

    st.sidebar.subheader("Please upload the PeptideShaker Reports here")
   
    # Creating a sidebar widget for users to upload multiple Excel files
    excel_tables = st.sidebar.file_uploader("This file uploader can accept multiple file uploads", type = ["xlsx"], accept_multiple_files = True)

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
        # Creating a session state flag to indicate if a table has been deleted 
        st.session_state.deleted_table = True  

    # Connecting to the sqlite database to query and retrieve all table names
    connection = sqlite3.connect(sqlite_db_path, check_same_thread = False)
    cursor = connection.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type = 'table';")
    tables = cursor.fetchall()
    # Closing the connection once finished querying 
    connection.close()

    # Checking whether there are any tables in the database
    if tables:
        # If tables are found, then table names are extracted from a tuple of tables
        table_names = [table[0] for table in tables]
        
        # Creating a selectbox widget for deleting tables one at a time
        selected_table = st.selectbox("If required, please select a table to delete from the sqlite database", options = ["Select one table at a time for deletion"] + table_names)

        # Checking if a table name has been selected and the delete button has been clicked by the user
        if selected_table != "Select a table" and st.button("Delete the selected table"):
            # Removing the selected data table from the sqlite database
            delete_tables_from_db(selected_table)
            st.success(f"Table: {selected_table} has been successfully deleted from the sqlite database.")
            # Creating a session state flag to indicate that a table has been deleted 
            st.session_state.deleted_table = True  

    # If the table has been deleted, then the session state flag is removed and the data is refreshed
    if st.session_state.deleted_table:
        st.session_state.deleted_table = False
        with st.spinner("Refreshing the page with user updates to the sqlite database..."):
            # Connecting to the sqlite database to fetch and display the tables after the user has deleted table(s)
            connection = sqlite3.connect(sqlite_db_path, check_same_thread = False)
            cursor = connection.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type ='table';")
            tables = cursor.fetchall()
            # Closing the connection once finished querying 
            connection.close()
            
            # If tables are found, then the table names are extracted from the tuple and retrieved from the sqlite database 
            if tables:
                for table_name in tables:
                    table_name = table_name[0]
                    df = retrieve_tables_from_db(table_name)
            # If no tables are found in the database after deletion, then a warning message is logged
            else:
                st.warning("No tables in the sqlite database can be found. Please upload PeptideShaker Reports to start your data analysis.")

    # For loop for iterating through each table_name 
    for table_name in tables:
        table_name = table_name[0]
        st.write(f"## {table_name}")
        # Retrieving the dataframe of the retrieved table_name 
        df = retrieve_tables_from_db(table_name)

        # Using widgets to remove, filter and group columns in the table
        st.sidebar.subheader(f"Select data cleaning operation(s) for {table_name}")
        
        # Creating a list of columns that the user can remove from the table
        data_columns = df.columns.tolist()
        # Creating a sidebar multiselect dropdown menu of columns that the user can remove from the table
        remove_columns = st.sidebar.multiselect("Remove Column(s)", options = data_columns, default=[])

        # If columns have been selected to be removed via the multiselect widget, then they will be removed from the dataframe 
        if remove_columns:
            df = df.drop(columns = remove_columns)

        # Creating a selectbox for the user to select which column to filter
        # The selectbox contains all of the column names and a "None" option if filtering is not required
        column_filter = st.sidebar.selectbox("Filter by Column (one column at a time)", options = ["None"] + data_columns)
        # If user selection is not "None", then the user is prompted to enter the value they want to put the filter on 
        if column_filter != "None":
           user_filter_value = st.sidebar.text_input(f"Enter value to filter {column_filter}", "")
           # If user has applied the filter, then the selected column in the dataframe is then filtered and updated
           # All column values would be classed as strings so that the user can apply the filter
           # The filter is not case sensitive 
           # Any NaN values in any column are not filtered and shown in the updated dataframe 
           # Any rows that do not have any filters are not shown in the updated dataframe 
           if user_filter_value:
                df = df[df[column_filter].astype(str).str.contains(user_filter_value, case = False, na = False)]
    
        # Creating a multiselect widget for grouping the data based on multiple columns 
        # Users will be able to select the column names they wish to group by 
        group_columns = st.sidebar.multiselect("Group By Column(s)", options = data_columns)
        # If a column has been selected for grouping, then:
        # Grouped rows will have unique set of values relating to the grouped columns
        # The occurance of a value in grouped columns will be calculated
        # The grouped results are made into a dataframe and the "size" column is changed to "Count of Occurance within the Group"
        if group_columns:
            group_columns_df = df.groupby(group_columns).size().reset_index(name = "Count of Occurances within the Group")
            st.write("### Grouped DataFrame")
            st.dataframe(group_columns_df)

        st.write("### Uploaded DataFrame")
        st.dataframe(df)
        

        # Using columns to calculate the frequency and perentages of the data 
        st.write("#### Calculated Column Counts & Percentages based on the above cleaned processed data")
        calculate_columns = df.select_dtypes(include = "object").columns

        # If there are columns which contain categorical data, then a dropdown menu is displayed
        if calculate_columns.size > 0:
            select_column = st.selectbox("Please choose a column from the above cleaned data table to see counts & percentages:", calculate_columns)

             # For the user selected column, frequency counts and percentages are shown and displayed as a dataframe
            if select_column:
                frequency = df[select_column].value_counts()
                percentages = (frequency / frequency.sum() * 100).round(2).astype(str) + "%"
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

                # Creating heatmaps to visualise the data from the uploaded cleaned data 
                st.write("### Heatmaps using data based on the above cleaned processed data")

                # Creating a dropdown menu for the user to select the columns required for the heatmap 
                heatmap_column_1 = st.selectbox("Please select the column for the y axis:", calculate_columns)
                heatmap_column_2 = st.selectbox("Please Choose the column for the x axis:", calculate_columns)

                # Selecting columns which have numeric data in the dataframe 
                numeric_columns = df.select_dtypes(include = "number").columns

                # Creating a dropdown menu for the user to select the column values for the heatmap
                actual_value_column = st.selectbox("Please select the values of the column you want to display:", numeric_columns)

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
                                    fig_heatmap = px.imshow(heatmap_data,
                                                            labels = dict(x = heatmap_column_2, y = heatmap_column_1, color = actual_value_column),
                                                            title = f"Heatmap of {heatmap_column_1} versus {heatmap_column_2} based on {actual_value_column}")
                                    st.plotly_chart(fig_heatmap)
                    else:
                        st.warning("Selected columns must be different for heatmap visualisation!")
                else:
                    st.warning(f"{actual_value_column} should have numeric data and must not be empty.")
                               
    
