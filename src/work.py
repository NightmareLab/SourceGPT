#!/usr/bin/env python
import os
import sys
import subprocess
import shutil

import wrap_openai
import openai_prompt


def do_unzip(file, dst_folder):
  rets = subprocess.run(["unzip", file, "-d", dst_folder])
  if rets.returncode != 0 :
    return -1
  return 0

def do_check_dir():
  rets = [ x for x in os.listdir() if not x.lower().endswith(".zip") ]
  rets_2 = [-1, None]
  if len(rets) == 1 :
    if not os.path.isdir(rets[0]) :
      rets_2[0] = 0
    else :
      rets_2 = [1, rets[0]]
  elif len(rets) > 1 :
    rets_2[0] = 0
  return rets_2


def do_list_files():
  directory = '.'
  output = []
  # Recursively search for all regular files in the directory tree
  for root, dirs, files in os.walk(directory):
    # skip .git
    if "/.git/" in root or root.endswith(".git") :
      continue
    for file in files:
      # Check if the file is a regular file
      if os.path.isfile(os.path.join(root, file)):
        output.append(os.path.join(root, file))
  return output


def do_inspect_file(openai_prompt, file_path):
  fp = open(file_path)
  data = fp.read().strip()
  is_valid = openai_prompt.validate_data(data)
  if not is_valid :
    return None
  return data


def do_delete_file(file):
  if os.path.isfile(file):
    os.remove(file)
  elif os.path.isdir(file):
    shutil.rmtree(file)
  else :
    pass


def work(proj_id, result_id, wrap_mongo):
  result_entry = wrap_mongo.get_result_entry(result_id)
  proj_entry = wrap_mongo.get_proj_entry(proj_id)
  settings = wrap_mongo.get_updated_settings()
  api_key = settings['api_key']

  prompt_sel = wrap_mongo.get_prompt_entry(result_entry['id_prompt'])
  prompt_sel_class = openai_prompt.PromptClass(prompt_sel, settings["max_tokens"])

  file_tounzip_path = proj_entry['name']
  resdir = "res{}".format(result_id)

  status = "Uploaded"

  try :
    if api_key == '' :
      raise Exception("API key is not set")

    os.chdir(settings['tmp_folder'])

    try :
      os.mkdir(resdir)
    except FileExistsError :
      raise Exception(
        "Folder '{}' is already present, please remove old scans on the stagin folder '{}'".format(
          resdir,
          settings['tmp_folder']
        )
      )

    status = "Unzip"
    wrap_mongo.update_result_status(result_id, status)

    rets = do_unzip(file_tounzip_path, resdir)
    if rets < 0 :
      raise Exception("Can't unzip '{}' to destination folder '{}'".format(proj_entry['name'], resdir))

    os.chdir(resdir)
    rets, proj_name = do_check_dir()
    if rets < 0 :
      raise Exception("Empty zip '{}' to destination folder '{}'".format(proj_entry['name'], resdir))

    next_resdir = resdir
    # if the zip file extracted does contain only a folder, then we update our db to that value
    if rets :
      next_resdir = proj_name
      os.chdir(next_resdir)
    files = do_list_files()
    wrap_mongo.update_proj_name(proj_id, proj_name)
    wrap_mongo.update_proj_files(proj_id, files)

    # scanning code phase
    status = "Scanning-code"
    wrap_mongo.update_result_status(result_id, status)

    openai = wrap_openai.wrap_openai(
      next_resdir,
      api_key,
      prompt_sel_class,
      openai_server_ = "proxy",
      single_scan_wtime=result_entry["single_scan_wtime"],
      type_scan=result_entry["type_scan"],
      openai_proxy_url= wrap_mongo.get_proxy(),
      max_tokens = settings["max_tokens"]
    )
 
    query = []
    file_skip = []
    for file in files :
      try :
        text = do_inspect_file(prompt_sel_class, file)
        if text :
          query.append((file, text))
        else :
          file_skip.append(file)
      except UnicodeDecodeError :
        file_skip.append(file)

    result = openai.ask(query)

    if isinstance(result, list):
      wrap_mongo.update_result_results(result_id, "", result)
    else :
      wrap_mongo.update_result_results(result_id, result, [])

    # now we update the db
    status = "Completed"
    wrap_mongo.update_result_status(result_id, status)

  except Exception as ex :
    print("Error:", ex)
    wrap_mongo.update_result_status(result_id, "Error-" + status, error=str(ex))

  # If 'delete_proj' is True, then delete project's files
  if result_entry['delete_proj'] :
    os.chdir(settings['tmp_folder'])
    do_delete_file(file_tounzip_path)
    do_delete_file(resdir)

  return


