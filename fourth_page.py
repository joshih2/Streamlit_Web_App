###########################
# F333290 - H.Joshi        #
# Date Created: 29/07/2024 #
# Last Updated: 13/08/2024 #
###########################


'''
fourth_page.py

This module corresponds to the Raw & Processed Chromatogram Analysis page (page 4) in the ProteoSpark Streamlit Web App. 

Please refer to app.py for a detailed description of this module.

Functions: 
def tic_chromatograms(file_reader) - calculating TIC values from the scan data extracted from raw and processed .mzML files 
def bpc_chromatograms(file_reader) - calculating BPC values from the scan data extracted from raw and processed .mzML files
def xic_chromatograms(file_reader, target_mz, mass_window) - calculating XIC values from the scan data extracted from raw and processed .mzML files
def fourth_page() - displaying the Raw and Processed Chromatogram Analysis page within the streamlit web app 

Parameters:
file_reader (object): for accessing the scan data from the raw and processed .mzML file 
target_mz (float): for inputting the m/z ratio of the ion for which xic is being extracted from the raw and processed .mzML files 
mass_window (float): for specifying the range around the target_mz before totaling all intensity values 
    
Returns:
tic (dictionary): storing time and intensity values for a MS level of a scan in the raw and processed .mzML file 
bpc_dict (dictionary): storing time values intensity values for a MS level of a scan in the raw and processed .mzML file 
xic (dictionary): storing time and intensity values for a MS level of a scan in the raw and processed .mzML files 

Raises:
Exception/Error - when there is an issue with the .mzMl file, chromatogram visualisation or .csv file upload 
'''

# Importing libraries and modules required for this modules 
import streamlit as st
import pandas as pd
import numpy as np 
import plotly.express as px
from pyteomics import mzml

def tic_chromatograms(file_reader):
    '''
    Function for calculating TIC values from the scan data extracted from raw and processed .mzML files.

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
    Function for calculating BPC values from the scan data extracted from raw and processed .mzML files.

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


def xic_chromatograms(file_reader, target_mz, mass_window):
    '''
    Function for calculating the XIC values from scan data in raw and processed .mzML files. 

    A dictionary called xic is created. The keys are the MS level and the associated values are the 
    dictionaries containing the list of the time values and intensity values. 

    The m/z values are filterd based on the closeness to the target_mz and if it is within the mass_window range. 
    The sum of these m/z values are then calculated and appended to the intensity values list in xic dictionary.

    Both the time values and intensity values lists are then converted into numpy arrays. 

    Parameters:
    file_reader (object): for accessing the scan data from the .mzML file 
    target_mz (float): user inputs the mass to charge ratio of the ion for which xic is being extracted 
    mass_window (float): user specifying the range around the target_mz before totaling all intensity values 
    
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

        # Filtering m/z values which are close to the target_mz and within the mass_window
        mz_filter = (mz_values >= target_mz - mass_window) & (mz_values <= target_mz + mass_window)
        # Calculating the sum of all the intensity values which match the retrieved m/z values and are within the mass_window range 
        xic_value = np.sum(intensity_values[mz_filter]) 
       # Appending the xic_value to the intensity values list for each MS level in the xic dictionary 
        xic[ms_level]["intensity values"].append(xic_value)
    # For loop for iterating through each MS level in xic dictionary and converting time and intensity values list into numpy arrays 
    for ms_level in xic:
        xic[ms_level]["time values"] = np.array(xic[ms_level]["time values"])
        xic[ms_level]["intensity values"] = np.array(xic[ms_level]["intensity values"])
    
    return xic


def fourth_page():
    '''
    Function for making the Raw & Processed Chromatogram Analysis page in the web app. 

    Users will be able to upload the following: raw .mzML file, processed .mzML file and the retrieved PSM data
    downloaded and saved from page 3.
    
    Three types of interactive chromatograms will be displayed: TIC, BPC, XIC. 
    All visualisations will be supported by a dataframe table which shows the plotted data points in the chromatogram. 
    If only MS1 is detected, then only MS1 chromatogram will be displayed.
    If both MS1 and MS2 scans are detected, then both chromatograms will be shown.  

    For the XIC, the user will be able to set the mass window and the target m/z which they can double check 
    from the uploaded .csv report. 

    Raises:
    Exception/Error - when there is an issue with the .mzMl file, chromatogram visualisation or .csv file upload 
    '''
    
    st.title("Raw & Processed Chromatogram Analysis")

    with st.expander("### ℹ️ Information"):
            st.write("""
                     Please upload the raw .mzML file , the processed .mzML file and the retrieved PSM Report data that you have
                     downloaded and saved from page 3 into the respective file uploaders in the sidebar. 
                     
                     Each file uploader can only upload one file at a time. 
                     
                     In the retrieved Default PSM Report, there are two columns: Spectrum File and m/z which are of importance. 
                     
                     You can look through the Spectrum File column to then find the revelant .mzML files from the raw and processed 
                     directory in your file explorer that corresponds to a particular protein main accession code.

                     You will be able to visualise three types of chromatograms for each raw and processed .mzML file: TIC, BPC & XIC. 
                     
                     Each chromatogram will be interactive and the table of the data points plotted will also be displayed alongside the 
                     chromatograms.
                     If only MS1 is detected, then only MS1 chromatogram will be displayed.
                     If both MS1 and MS2 scans are detected, then both chromatograms will be shown.  

                     Note: For the XIC chromatogram, you will be able to select between MS1 and MS2 scans (if detected)
                     and be able to set the mass window you wish to analyse.
                     Also, using the .csv file you have uploaded, you will be able to use the m/z value that corresponds to 
                     to the .mzML file you are viewing as an input for the target m/z value. 
                """)

    st.sidebar.subheader("Please upload the following files below:")
    # Creating sidebar file uploader widgets for uploading: a raw .mzML file, a processed .mzML file and the retrieved PSM data from page 3
    retrieved_psm_data = st.sidebar.file_uploader("Default PSM report data retrieved from page 3", type = ["csv"], key = "psm_data_page3", accept_multiple_files = False)

    raw_spectrum_file = st.sidebar.file_uploader(".mzML file from the raw directory", type = ["mzml"], key = "raw_spectrum", accept_multiple_files = False)
    
    processed_spectrum_file = st.sidebar.file_uploader(".mzML file from the processed directory", type = ["mzml"], key = "processed_spectrum", accept_multiple_files =False)

    # Checking if the .csv file has been uploaded
    if retrieved_psm_data is not None:
        # If uploaded, .csv file is read and converted to pandas dataframe
        # Otherwise, an error would be displayed 
        try:
            retrieved_psm_df = pd.read_csv(retrieved_psm_data)
            st.write("### Retrieved Data on page 3 from the Default PSM Report")
            st.dataframe(retrieved_psm_df)
        except Exception as e:
            st.error(f"Error reading .csv file: {e}")


    # Checking if the processed .mzML file has been uploaded 
    if processed_spectrum_file is not None:
        # If yes, then this statement will be printed 
        st.write("### Chromatograms using processed .mzML files")

        # Try - Except block for visualising chromatograms from processed .mzML files 
        try:
            # The filename is retrieved and the processed .mzML file is read 
            file_name = processed_spectrum_file.name
            read_spectrum_file = mzml.read(processed_spectrum_file, use_index = True)
            
            # Generating TIC by reading the processed .mzML file
            generate_tic = tic_chromatograms(read_spectrum_file)
            # Generating BPC by reading the processed .mzML file 
            generate_bpc = bpc_chromatograms(read_spectrum_file)
            
            # Tab layout for the three processed chromatogram plots
            tic_tab, bpc_tab, xic_tab = st.tabs(["Processed TIC Chromatogram", "Processed BPC Chromatogram", "Processed XIC Chromatogram"])

            # For loop for iterating through the MS scan levels for visualising the data
            for ms_level in [2]:  
                # If MS2 does not exist, then warning message will be displayed and continues the loop
                if ms_level not in generate_tic or ms_level not in generate_bpc:
                    st.warning(f"Data cannot be found for MS level: {ms_level} in uploaded .mzML file.")
                    continue

                # Creating dataframes of the time and intensity values plotted for the TIC & BPC chromatograms at the selected MS level
                tic_df = pd.DataFrame({"Time": generate_tic[ms_level]["time values"],
                                       "TIC":  generate_tic[ms_level]["intensity values"]})
                bpc_df = pd.DataFrame({"Time": generate_bpc[ms_level]["time values"],
                                       "BPC":  generate_bpc[ms_level]["intensity values"] })

                
                # Creating and displaying an interactive TIC chromatogram for the uploaded processed .mzML file 
                # Configuring the axis, axis labels, chart title, markers, hover tooltips, plot size
                with tic_tab:
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        fig_tic = px.line(tic_df, x = "Time", y = "TIC",
                                          labels = {"Time": "Time", "TIC": "Intensity"},
                                          title = f"Total Ion Chromatogram (MS{ms_level}) for Processed {file_name}",
                                          markers = True,
                                          hover_data = {"Time": True, "TIC": True})
                        
                        # Setting the x and y axis to start at (0,0) and the y axis scale is set to 10% more than the maximum value in the data 
                        fig_tic.update_layout(
                            xaxis = dict(range = [0, tic_df["Time"].max() * 1.1]),  
                            yaxis = dict(range = [0, tic_df["TIC"].max()  * 1.1]))    
                        
                        # Configuring y axis to be written in scientific notation 
                        fig_tic.update_layout(yaxis = dict(tickformat = ".1e"))

                        # Configuring height and wdith of the chromatogram plot
                        fig_tic.update_layout(width = 400 , height = 550)

                        # Displaying the TIC plot on the left side of the page
                        st.plotly_chart(fig_tic, use_container_width = True)

                    # Displaying the dataframe of the TIC data points on the right side of the page
                    with col2:
                        st.subheader(f"TIC Data Points (MS{ms_level})")
                        st.dataframe(tic_df)

                # Creating and displaying an interactive BPC chromatogram for the uploaded processed .mzML file 
                # Configuring the axis, axis labels, chart title, markers, hover tooltips, plot size
                with bpc_tab:
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        fig_bpc = px.line(bpc_df, x = "Time", y = "BPC",
                                          labels = {"Time": "Time", "BPC": "Intensity"},
                                          title = f"Base Peak Chromatogram (MS{ms_level}) for Processed {file_name}",
                                          markers = True,
                                          hover_data = {"Time": True, "BPC": True})
                        
                        # Setting the x and y axis to start at (0,0) and the y axis scale is set to 10% more than the maximum value in the data 
                        fig_bpc.update_layout(
                            xaxis = dict(range = [0, bpc_df["Time"].max() * 1.1]),  
                            yaxis = dict(range = [0, bpc_df["BPC"].max()  * 1.1]))    
                        
                        # Configuring y axis to be written in scientific notation 
                        fig_bpc.update_layout(yaxis = dict(tickformat = ".1e"))

                        # Configuring height and wdith of the chromatogram plot
                        fig_bpc.update_layout(width = 400, height = 550)

                        # Displaying the BPC plot on the left side of the page
                        st.plotly_chart(fig_bpc, use_container_width = True)

                    # Displaying the dataframe of the BPC data points on the right side of the page
                    with col2:
                        st.subheader(f"BPC Data Points (MS{ms_level})")
                        st.dataframe(bpc_df)

                with xic_tab:
                    # Using columns to layout the XIC tab
                    col1, col2 = st.columns([3, 1])

                    # Creating selection and input boxes for the user to select/input the MS level, target m/z and mass_window for XIC
                    select_ms_level = st.selectbox("Please select the MS level:", key = "select_processed_level", options = [1, 2])
                    target_mz = st.number_input("Please enter the target m/z value:", key = "select_target_mz")
                    mass_window = st.number_input("Please enter the mass window:", key = "input_mass_window")
                
                    # If user has specified the target_mz and mass_window then only will the XIC chromatogram be visualised inside the try-except block  
                    if target_mz and mass_window:
                        try: 
                            with col1:
                                # Generating XIC from the read processed .mzML file, target_mz and mass_window
                                generate_xic = xic_chromatograms(read_spectrum_file, target_mz, mass_window)

                                # Creating dataframe of the time and intensity values plotted for the XIC chromatogram
                                xic_df = pd.DataFrame({"Time": generate_xic[select_ms_level]["time values"],
                                                       "XIC":  generate_xic[select_ms_level]["intensity values"]})
                                
                                # Creating and displaying an interactive XIC chromatogram for the uploaded processed .mzML file 
                                # Configuring the axis, axis labels, chart title, markers, hover tooltips, plot size
                                fig_xic = px.line(xic_df, x = "Time", y = "XIC",
                                                  labels = {"Time": "Time", "XIC": "Intensity"},
                                                  title = f"Extracted Ion Chromatogram (m/z = {target_mz}) for Processed {file_name} - (MS{select_ms_level})",
                                                  markers = True,
                                                  hover_data = {"Time": True, "XIC": True})
                                
                                # Setting the x and y axis to start at (0,0) and the y axis scale is set to 10% more than the maximum value in the data 
                                fig_xic.update_layout(
                                    xaxis = dict(range = [0, xic_df["Time"].max() * 1.1]),  
                                    yaxis = dict(range = [0, xic_df["XIC"].max()  * 1.1]))    
                               
                                # Configuring y axis to be written in scientific notation 
                                fig_xic.update_layout(yaxis = dict(tickformat = ".1e"))

                                # Configuring height and wdith of the chromatogram plot
                                fig_xic.update_layout(width = 400 , height = 550)
                                
                                # Displaying the XIC plot on the left side of the page
                                st.plotly_chart(fig_xic, use_container_width = True)

                            # Displaying the dataframe of the XIC data points on the right side of the page
                            with col2:
                                st.subheader(f"XIC Data Points (MS{select_ms_level})")
                                st.dataframe(xic_df)
                          
                        except Exception as e:
                            st.error(f"Error occured during XIC chromatogram visualisation: (MS{select_ms_level}) not found.")

        except Exception as e:
            st.error(f"Error occured when uploading processed .mzML file: {e}.")

    
    # Checking if the raw .mzML file has been uploaded
    if raw_spectrum_file is not None:
        # If yes, then this statement will be printed 
        st.write("### Chromatograms using raw .mzML files")

        # Try - Except block for visualising chromatograms from raw .mzML files 
        try:
            # The filename is retrieved and the raw .mzML file is read 
            file_name = raw_spectrum_file.name
            read_spectrum_file = mzml.read(raw_spectrum_file, use_index = True)
            
            # Generating TIC by reading the raw .mzML file
            generate_tic = tic_chromatograms(read_spectrum_file)
            # Generating BPC by reading the raw .mzML file 
            generate_bpc = bpc_chromatograms(read_spectrum_file)

            # Tab layout for the three raw chromatogram plots
            tic_tab, bpc_tab, xic_tab = st.tabs(["Raw TIC Chromatogram", "Raw BPC Chromatogram", "Raw XIC Chromatogram"])

            # For loop for iterating through the MS scan levels 1 & 2 for visualising the data
            for ms_level in [1, 2]: 
                # If both MS levels does not exist, then warning message will be displayed and continues the loop
                if ms_level not in generate_tic or ms_level not in generate_bpc:
                    st.warning(f"Data cannot be found for MS level: {ms_level} in uploaded .mzML file.")
                    continue

                # Creating dataframes of the time and intensity values plotted for the TIC & BPC chromatograms at the selected MS level
                tic_df = pd.DataFrame({"Time": generate_tic[ms_level]["time values"],
                                       "TIC":  generate_tic[ms_level]["intensity values"]})
                bpc_df = pd.DataFrame({"Time": generate_bpc[ms_level]["time values"],
                                       "BPC":  generate_bpc[ms_level]["intensity values"]})
                
                # Creating and displaying an interactive BPC chromatogram for the uploaded raw .mzML file 
                # Configuring the axis, axis labels, chart title, markers, hover tooltips, colour, plot size
                with tic_tab:
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        fig_tic = px.line(tic_df, x = "Time", y = "TIC",
                                          labels = {"Time": "Time", "TIC": "Intensity"},
                                          title = f"Total Ion Chromatogram (MS{ms_level}) for Raw {file_name}",
                                          markers = True,
                                          hover_data = {"Time": True, "TIC": True})
                        
                        # Setting the x and y axis to start at (0,0) and the y axis scale is set to 10% more than the maximum value in the data 
                        fig_tic.update_layout(
                            xaxis = dict(range = [0, tic_df["Time"].max() * 1.1]),  
                            yaxis = dict(range = [0, tic_df["TIC"].max()  * 1.1]))            

                        # Configuring y axis to be written in scientific notation 
                        fig_tic.update_layout(yaxis = dict(tickformat = ".1e"))
                        
                        # Customising the plotting to red colour
                        fig_tic.update_traces(line_color = "red")

                        # Configuring height and wdith of the chromatogram plot
                        fig_tic.update_layout(width = 400, height = 550)
                       
                        # Displaying the TIC plot on the left side of the page
                        st.plotly_chart(fig_tic, use_container_width = True)

                    # Displaying the dataframe of the TIC data points on the right side of the page
                    with col2:
                        st.subheader(f"TIC Data Points (MS{ms_level})")
                        st.dataframe(tic_df)

                # Creating and displaying an interactive BPC chromatogram for the uploaded raw .mzML file 
                # Configuring the axis, axis labels, chart title, markers, hover tooltips
                with bpc_tab:
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        fig_bpc = px.line(bpc_df, x = "Time", y = "BPC",
                                          labels = {"Time": "Time", "BPC": "Intensity"},
                                          title = f"Base Peak Chromatogram (MS{ms_level}) for Raw {file_name}",
                                          markers = True,
                                          hover_data = {"Time": True, "BPC": True})
                        
                       # Setting the x and y axis to start at (0,0) and the y axis scale is set to 10% more than the maximum value in the data 
                        fig_bpc.update_layout(
                            xaxis = dict(range = [0, bpc_df["Time"].max() * 1.1]),  
                            yaxis = dict(range = [0, bpc_df["BPC"].max()  * 1.1]))          
                       
                        # Configuring y axis to be written in scientific notation 
                        fig_bpc.update_layout(yaxis = dict(tickformat = ".1e"))
                        
                        # Customising the plotting to red colour 
                        fig_bpc.update_traces(line_color = "red")
                        
                        # Configuring height and wdith of the chromatogram plot
                        fig_bpc.update_layout(width = 400, height = 550)
                       
                        # Displaying the BPC plot on the left side of the page
                        st.plotly_chart(fig_bpc, use_container_width = True)

                    # Displaying the dataframe of the TIC data points on the right side of the page
                    with col2:
                        st.subheader(f"BPC Data Points (MS{ms_level})")
                        st.dataframe(bpc_df)


                with xic_tab:
                    # Using columns to layout the XIC tab
                    col1, col2 = st.columns([3, 1])

                    # Creating unique keys for the selection and input boxes when both MS1 and MS2 scans have been detected
                    raw_unique_keys = f"{file_name}_MS{ms_level}"

                
                    # Creating selection and input boxes for the user to select/input the MS level, target m/z and mass_window for XIC
                    # If both MS1 and MS2 scans are detected in the raw .mzML file, then raw_unique_keys will differentiate between both scans
                    select_ms_level = st.selectbox("Please select the MS level:", key = f"select_ms_level_{raw_unique_keys}", options = [1, 2])
                    target_mz = st.number_input(f"Please enter the target m/z value:", key = f"target_mz_{raw_unique_keys}")
                    mass_window = st.number_input(f"Please enter the mass window:" , key = f"mass_window_{raw_unique_keys}")
                
                    # If user has specified the target_mz and mass_window then only will the XIC chromatogram be visualised inside the try-except block 
                    if target_mz and mass_window:
                        try:
                            with col1:
                                # Generating XIC from the read processed .mzML file, target_mz and mass_window
                                generate_xic = xic_chromatograms(read_spectrum_file, target_mz, mass_window)
                                
                                # Creating dataframe of the time and intensity values plotted for the XIC chromatogram
                                xic_df = pd.DataFrame({"Time": generate_xic[select_ms_level]["time values"],
                                                       "XIC":  generate_xic[select_ms_level]["intensity values"]})
                                
                                # Creating and displaying an interactive XIC chromatogram for the uploaded raw .mzML file 
                                # Configuring the axis, axis labels, chart title, markers, hover tooltips, colour, plot size
                                fig_xic = px.line(xic_df, x = "Time", y = "XIC",
                                                    labels = {"Time": "Time", "XIC": "Intensity"},
                                                    title = f"Extracted Ion Chromatogram (m/z = {target_mz}) for Raw {file_name} - (MS{select_ms_level})",
                                                    markers = True,
                                                    hover_data = {"Time": True, "XIC": True})
                                
                                # Setting the x and y axis to start at (0,0) and the y axis scale is set to 10% more than the maximum value in the data 
                                fig_xic.update_layout(
                                    xaxis = dict(range = [0, xic_df["Time"].max() * 1.1]),  
                                    yaxis = dict(range = [0, xic_df["XIC"].max()  * 1.1]))          
                                
                                # Configuring y axis to be written in scientific notation 
                                fig_xic.update_layout(yaxis = dict(tickformat = ".1e"))

                                # Customising the plotting to red colour
                                fig_xic.update_traces(line_color = "red")
                                
                                # Configuring height and wdith of the chromatogram plot
                                fig_xic.update_layout(width = 400 , height = 550)

                                # Displaying the XIC plot on the left side of the page
                                st.plotly_chart(fig_xic, use_container_width = True)
                            
                            # Displaying the dataframe of the XIC data points on the right side of the page
                            with col2:
                                st.subheader(f"XIC Data Points (MS{select_ms_level})")
                                st.dataframe(xic_df)
                            
                        except Exception as e:
                            st.error(f"Error occured during XIC chromatogram visualisation: (MS{select_ms_level}) not found.")

        except Exception as e:
            st.error(f"Error occured when uploading .mzML file: {e}")



                     
                            