import streamlit as st
import os
from pathlib import Path
import pandas as pd
import xlsxwriter
import glob
import shutil
import zipfile
# import pytesseract
import cv2
from pdf2image import convert_from_path
import time
from io import BytesIO
import datetime
# import easyocr
import re
from pypdf import PdfReader
import pdfplumber


st.set_page_config(layout="wide")

st.markdown(f"<h1 style='text-align: center;'>WELCOME TO OCR PAJAK 2<br>LAUTAN LUAS</h1>", unsafe_allow_html=True)



user_input_excel = st.file_uploader("Upload pdf folder", type=['xlsx'], accept_multiple_files=False, key='file_uploader_1')
    
user_input_folder_billing = st.file_uploader("Upload pdf Billing Folder", type=['zip'], accept_multiple_files=False, key='file_uploader_2')

user_input_folder_bpn = st.file_uploader("Upload pdf BPN Folder", type=['zip'], accept_multiple_files=False, key='file_uploader_3')

if user_input_excel is not None:
    if user_input_excel.name.endswith('.xlsx'):
        st.success('File Excel Uploaded Successfully!')
    else:
        st.sidebar.warning('You need to upload an excel file')
        
    if user_input_folder_billing is not None:
        if user_input_folder_billing.name.endswith('.zip'):
            path_to_billing_folder = os.path.join(os.getcwd(), os.path.splitext(user_input_folder_billing.name)[0])
            if os.path.exists(path_to_billing_folder) == False:
                os.mkdir(path_to_billing_folder)
            with zipfile.ZipFile(user_input_folder_billing, 'r') as z:
                z.extractall(path_to_billing_folder)
            st.success('Billing Folder Uploaded Successfully!')
        else:
            st.sidebar.warning('You need to upload zip folder for Billing Folder')
        
        if user_input_folder_bpn is not None:
            if user_input_folder_bpn.name.endswith('.zip'):
                path_to_BPN_folder = os.path.join(os.getcwd(), os.path.splitext(user_input_folder_bpn.name)[0])
                if os.path.exists(path_to_BPN_folder) == False:
                    os.mkdir(path_to_BPN_folder)
                with zipfile.ZipFile(user_input_folder_bpn, 'r') as z:
                    z.extractall(path_to_BPN_folder)
                    st.success('BPN Folder Uploaded Successfully!')
            else:
                st.sidebar.warning('You need to upload zip folder for BPN Folder')

            # Pengolahan data
            df = pd.read_excel(user_input_excel)
            # st.write(df)
            # st.write(path_to_billing_folder)
            # st.write(path_to_BPN_folder)

            
            
            for i in range(len(df)):
                no_po = df['NO PO'][i]
                nama_file_billing = 'BILLING ' + str(no_po) + '.pdf'
                path_to_pdf_billing = os.path.join(path_to_billing_folder, os.path.splitext(user_input_folder_billing.name)[0], nama_file_billing)

                extracted_text_billing_pdf = ""

                try :
                    with pdfplumber.open(path_to_pdf_billing) as pdf:
                        for page in pdf.pages:
                            # Use a corrected bounding box (x0, y0, x1, y1)
                            # (left, bottom, right, top)
                            cropped = page.within_bbox((int(0/20.35*595), int((3.5)/20.35*595), int(15/20.35*595), int((4.5)/20.35*595)))
                            text = cropped.extract_text()
                            if text:
                                extracted_text_billing_pdf += text.strip()
    
                    extracted_text_no_billing = re.findall('(?<=Nomor Billing : )[^ ].*', extracted_text_billing_pdf)
                    extracted_text_tanggal = re.findall('(?<=Tanggal : )[^ ].*', extracted_text_billing_pdf)
    
                    # st.write(extracted_text_no_billing)
                    # st.write(extracted_text_tanggal)
                    
                    df['NO BILLING'][i] = str(extracted_text_no_billing[0])
                    df['TANGGAL'][i] = str(extracted_text_tanggal[0])

                except:
                    pass
                    # df['NO BILLING'][i] = ''
                    # df['TANGGAL'][i] = ''
    
    
                try :
                    pattern_nama_file_BPN = 'BPN_' + str(extracted_text_no_billing[0]) + '*.pdf'
                    path_to_pdf_BPN = os.path.join(path_to_BPN_folder, os.path.splitext(user_input_folder_bpn.name)[0], pattern_nama_file_BPN)
                    
                    path_to_pdf_BPN = glob.glob(str(path_to_pdf_BPN))
                    # st.write(path_to_pdf_BPN)
     
                    reader_BPN = PdfReader(path_to_pdf_BPN[0])
                    a=[]
                    # Iterate through pages and extract text
                    extracted_text = ""
                    for page in reader_BPN.pages:
                        extracted_text += page.extract_text()
                    a = [extracted_text]
                    # st.write(a)
    
                    extracted_text_ntpn = re.findall('(?<=NTPN : )[^ ].*', a[0])
                    extracted_text_no_dokumen = re.findall('(?<=NOMOR DOKUMEN : )[^ ]+(?=\s)', a[0])
                    extracted_text_jumlah_setoran = re.findall('(?<=JUMLAH SETORAN : )[^ ]+(?=\s)', a[0])
    
                    # st.write(extracted_text_ntpn)
                    # st.write(extracted_text_no_dokumen)
                    # st.write(extracted_text_jumlah_setoran)
    
                    df['NTPN'][i] = str(extracted_text_ntpn[0])
                    df['NOMOR DOKUMEN'][i] = str(extracted_text_no_dokumen[0])
                    df['JUMLAH SETORAN'][i] = str(extracted_text_jumlah_setoran[0])

                except :
                    pass
                    # df['NTPN'][i] = ''
                    # df['NOMOR DOKUMEN'][i] = ''
                    # df['JUMLAH SETORAN'][i] = ''
                    
                

            st.write(df)

            with st.spinner("Preparing for data to be downloaded ..."):
                output = BytesIO()
    
                with pd.ExcelWriter(output, engine='xlsxwriter') as writer: 
                    df_download = df.to_excel(writer)

                output_excel_file_name = 'result' + ' ' + str(os.path.splitext(user_input_excel.name)[0]) + '.xlsx'
        
                button_clicked = st.download_button(label=':cloud: Download result', type="secondary", data=output.getvalue(),file_name=output_excel_file_name)

            
                
        else :
            st.error("You have to upload BPN Folder")
    else :
        st.error("You have to upload Billing Folder")
else :
    st.error("You have to upload excel")


    
