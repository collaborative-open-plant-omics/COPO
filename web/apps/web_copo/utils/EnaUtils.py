__author__ = 'fshaw'
import re
from django.urls import reverse
from django.core.exceptions import ObjectDoesNotExist
import os

import PyPDF2
from datetime import time
from dal.ena_da import EnaCollection


def get_sample_html_from_details_id(details_id):
    # get related study and sample set
    try:
        #study = EnaStudy.objects.get(collection__id=collection_id)
        #sample_set = EnaSample.objects.filter(ena_study__id=study.id)
        details = EnaCollection().GET(details_id)
        sample_set = details['samples']
    except ObjectDoesNotExist:
        return 'not found'

    out = ''
    #construct output html
    for s in sample_set:
        out += '<tr><td>' + '<a rest_url="' + reverse('rest:get_sample_html', args=[str(s["_id"])]) + '" href="">' + s['Source_Name'] + '</a>' + '</td><td>' + s['Sample_Name'] + '</td><td>' + s['Individual_Name'] + '</td><td>' + s['Description'] + '</td></tr>'
    return out


def handle_uploaded_file(f):
    # get timestamp
    t = str(time.time()).replace('.', '')
    k = 'file_' + f.name
    path = os.path.join('/Users/fshaw/Desktop/test/', k)
    destination = open(path, 'w+')
    for chunk in f.chunks():
        destination.write(chunk)


# function does a pdf file test
def is_pdf_file(file_name):
    file_obj = open(file_name, 'rb')
    is_pdf = True
    try:
        pdfReader = PyPDF2.PdfFileReader(file_obj)
    except:
        is_pdf = False
    return is_pdf


def is_fastq_file(file_name):
    with open(file_name, 'r') as f:
        second_line_length = 0
        for k in range(0, 4):
            li = f.readline().strip()

            if k == 0:
                if not li.startswith('@'):
                    # if first line don't start with @ can't be fastq
                    return False
            elif k == 1:
                if not re.match('^(A|G|T|C|N|-)+$', li):
                    # return false if not only AGTC is present in data string
                    print('illegal character in line: ' + li)
                    return False
                else:
                    # store length of string
                    second_line_length = len(li)
            elif k == 2:
                if not li.startswith('+'):
                    # check thrid line starts with +
                    return False
            else:
                if len(li) != second_line_length:
                    print ('line lengths not equal' + li)
                    # if length of 2nd and 4th lines is not equal, return false
                    return False

        return True


def is_sam_file(file_name):
    # get the first line of the file and compare to regex
    with open(file_name, 'r') as f:
        li = f.readline().strip()
        regex1 = "^@[A-Za-z][A-Za-z](\t[A-Za-z][A-Za-z0-9]:[ -~]+)+$"
        regex2 = "^@CO\t.*"
        return (re.match(regex1, li) is not None or re.match(regex2, li) is not None)

'''
def is_bam_file(file_name):
    # try opening the file with pysam. If this causes an exception, its not a bam file
    try:
        with pysam.AlignmentFile(file_name, "rb") as samfile:
            return True
    except(Exception) as inst:
        return False
'''
def is_cram_file(file_name):
    pass


def is_gzipped(file_name):
    # try opening the file in gzip and reading the first few chars
    #if this produces an IOError, it probably isn't gzipped
    import gzip

    try:
        f = gzip.open(file_name, 'rb')
        r = f.read(5)
        return True
    except(IOError) as inst:
        return False
    finally:
        f.close()

def filesize_toString(f_size):
    import math
    KB = math.pow(10,3)
    MB = math.pow(10,6)
    GB = math.pow(10,9)
    TB = math.pow(10,12)

    if 0 <= f_size < KB:
        out = "%.2f" % f_size + ' B'
    elif KB <= f_size < MB:
        out = "%.2f" % (f_size / KB) + " KB"
    elif MB <= f_size < GB:
        out = "%.2f" % (f_size / MB) + " MB"
    elif GB <= f_size < TB:
        out = "%.2f" % (f_size / GB) + " GB"
    else:
        out = "%.2f" % (f_size / TB) + " TB"
    return out
