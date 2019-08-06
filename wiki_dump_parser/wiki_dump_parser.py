#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
  wiki_dump_parser.py

  Script to convert a xml mediawiki history dump to a csv file with readable useful data
for pandas processing.

  Copyright 2017-2019 Abel 'Akronix' Serrano Juste <akronix5@gmail.com>
"""

import xml.parsers.expat
import sys
import time

__version__ = '2.0.1'

Debug = False 

delim_char = ","

def xml_to_csv(filename):

  ### BEGIN xmt_to_csv var declarations ###
  # Shared variables for parser subfunctions:
  ## output_csv, _current_tag, _parent
  ## page_id,page_title,page_ns,revision_id,timestamp,contributor_id,contributor_name,bytes_var

  output_csv = None
  _parent = None
  _current_tag = ''
  page_id = page_title = page_ns = revision_id = timestamp = contributor_id = contributor_name = comment = ''
  minor = bytes_var = ''

  def start_tag(tag, attrs):
    nonlocal output_csv, _current_tag, _parent
    nonlocal minor, bytes_var

    _current_tag = tag
    
    if tag == 'minor':
      minor = '1'
    elif tag == 'text':
      if 'bytes' in attrs:
        bytes_var = attrs['bytes']
      else: # There's a 'deleted' flag or no info about bytes of the edition
        bytes_var = '-1'
    elif tag == 'page' or tag == 'revision' or tag == 'contributor':
      _parent = tag

    if tag == 'upload':
      print("!! Warning: '<upload>' element not being handled", file=sys.stderr)

  def data_handler(data):
    nonlocal output_csv, _current_tag, _parent
    nonlocal page_id,page_title,page_ns,revision_id,timestamp,contributor_id,contributor_name,comment

    if _current_tag == '': # Don't process blank "orphan" data between tags!!
      return

    if _parent:
      if _parent == 'page':
        if _current_tag == 'title':
          page_title = '|' + data + '|'
        elif _current_tag == 'id':
          page_id = data
          if Debug:
            print("Parsing page " + page_id )
        elif _current_tag == 'ns':
          page_ns = data
      elif _parent == 'revision':
        if _current_tag == 'id':
          revision_id = data
        elif _current_tag == 'timestamp':
          timestamp = data
        elif _current_tag == 'comment':
          comment = '|' + data + '|'
      elif _parent == 'contributor':
        if _current_tag == 'id':
          contributor_id = data
        elif _current_tag == 'username':
          contributor_name = '|' + data + '|'
        elif _current_tag == 'ip':
          contributor_id = data
          contributor_name = 'Anonymous'

  def end_tag(tag):
    nonlocal output_csv, _current_tag, _parent
    nonlocal page_id,page_title,page_ns,revision_id,timestamp,contributor_id,contributor_name,comment
    nonlocal minor,bytes_var


    def has_empty_field(lst):
      field_empty = False;
      i = 0
      while (not field_empty and i<len(lst)):
        field_empty = (lst[i] == '');
        i = i + 1
      return field_empty

    def has_nAn_field(lst):
      field_nAn = False;
      i = 0
      while (not field_nAn and i<len(lst)):
        field_nAn = (not lst[i].isdigit());
        i = i + 1
      return field_nAn


    # uploading one level of parent if any of these tags close
    if tag == 'page':
      _parent = None
    elif tag == 'revision':
      _parent = 'page'
    elif tag == 'contributor':
      _parent = 'revision'

    # print revision to revision output csv
    if tag == 'revision':
       
      if not minor == '1':
        minor = '0'      

      revision_row = [page_id, page_title, page_ns,
                      revision_id, timestamp,
                      contributor_id,contributor_name,comment,
                      minor,bytes_var]
 
      # check for incorrect data types and empty fields (except empty comment)
      num_fields = [page_id, page_ns, revision_id, minor, bytes_var]
      nonComment_fields = [page_title, timestamp, contributor_id, contributor_name]  

      if (has_nAn_field(num_fields) and has_empty_field(nonComment_fields)):
        errors = ['1','1']
        print('nAn & empty ', revision_row)
        error_csv.write(delim_char.join(revision_row + errors) + '\n')
      elif has_nAn_field(num_fields):
        errors = ['1','0'] 
        print('nAn ONLY ', revision_row)
        error_csv.write(delim_char.join(revision_row + errors) + '\n')
      elif has_empty_field(nonComment_fields):
        errors = ['0','1']
        print('empty ONLY ', revision_row)
        error_csv.write(delim_char.join(revision_row + errors) + '\n')
 
      # write every row to csv
      output_csv.write(delim_char.join(revision_row) + '\n')
      
      # Debug lines to standard output
      if Debug:
        print(delim_char.join(revision_row))

      # Clearing data that has to be recalculated for every row:
      revision_id = timestamp = contributor_id = contributor_name = comment = '' 
      minor = bytes_var = ''

    _current_tag = '' # Very important!!! Otherwise blank "orphan" data between tags remain in _current_tag and trigger data_handler!! >:(


  ### BEGIN xml_to_csv body ###

  # Initializing xml parser
  parser = xml.parsers.expat.ParserCreate(encoding='UTF-8')
  input_file = open(filename, 'rb')

  parser.StartElementHandler = start_tag
  parser.EndElementHandler = end_tag
  parser.CharacterDataHandler = data_handler
  parser.buffer_text = True
  parser.buffer_size = 1024

  # writing error csv file
  error_csv = open("error_"+filename[0:-3]+"csv",'w', encoding='utf8')
  error_csv.write(delim_char.join(["page_id","page_title","page_ns","revision_id","timestamp","contributor_id","contributor_name","comment","minor","bytes","nAn","empty"]))
  error_csv.write("\n")

  # writing header for output csv file
  output_csv = open(filename[0:-3]+"csv",'w', encoding='utf8')
  output_csv.write(delim_char.join(["page_id","page_title","page_ns","revision_id","timestamp","contributor_id","contributor_name","comment","minor","bytes"]))
  output_csv.write("\n")

  # Parsing xml and writting proccesed data to output csv
  print("Processing...")
  parser.ParseFile(input_file)
  print("Done processing")

  input_file.close()
  output_csv.close()

  return True

if __name__ == "__main__":
  if(len(sys.argv)) >= 2:
    print ('Dump files to process: {}'.format(sys.argv[1:]))
    for xmlfile in sys.argv[1:]:
      tick = time.time()
      print("Starting to parse file " + xmlfile)
      if xml_to_csv(xmlfile):
        tock = time.time()
        print("Data dump {0} parsed succesfully in {1:2f} minutes".format(xmlfile, (tock-tick)/60))
        sys.exit(0)
  else:
    print("Error: Invalid number of arguments. Please specify one or more .xml file to parse", file=sys.stderr)
    sys.exit(1)
