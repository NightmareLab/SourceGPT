#!/usr/bin/env python
import os
import sys
import subprocess
import time
import argparse
import copy

from flask import Flask, render_template, session, request, flash
from werkzeug.utils import secure_filename
import logging

from init_mongo import WrapMongo
import work


###
## Config
#

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = None

# to implement logger
logger = logging.getLogger('werkzeug')


ALLOWED_EXTENSIONS = {'zip'}
wrap_mongo = None
mongo_ip = "mongo"



########## Extracted from init_mongo.py
# Type of scan
COLLAPSE_SCAN = 0
SINGLE_SCAN = 1
MULTIPLE_SCAN = 2
default_scan = COLLAPSE_SCAN
########## 




###
## Helper functions
#

def allowed_file(filename):
  return '.' in filename and \
    filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def launch_thread(proj_id, result_id):
  pid = os.fork()
  if pid == 0 :
    work.work(proj_id, result_id, wrap_mongo)
    sys.exit(0)
  else :
    return


###
## Web uri
#

@app.route('/mongo_ready')
def mongo_ready():
  return wrap_mongo.is_admin()

@app.route('/')
def index():
  return render_template('index.html')

@app.route('/results')
def results():
  order_view = ["date", "id", "id_proj", "status", "type_scan", "result"]
  type_scan_list = ["collapse_scan", "single_scan", "multiple_scan"]

  #results = [ {x:'Ok' for x in order_view} ]
  results = wrap_mongo.get_results()
  for x in results :
    x['date'] = time.strftime("%H:%M:%S %Y-%m-%d", time.gmtime(int(x['date'])))
    x['type_scan'] = type_scan_list[x['type_scan']]

  return render_template('results.html', results=results, order_view=order_view)

@app.route('/prompts')
def prompts():
  order_view = ["id", "name", "details"]
  modal_view = ["description", 'assistant', 'instruction']
  prompts = wrap_mongo.get_prompts()
  return render_template('prompts.html', prompts=prompts, order_view=order_view, modal_view=modal_view)


@app.route('/settings', methods=['GET','POST'])
def settings():
  status = ""
  if request.method == 'POST' :
    try :
      if 'tmp_folder' in request.form :
        tmp_folder = request.form['tmp_folder'].strip()
        if tmp_folder != '' :
          make = True if 'tmp_folder_make' in request.form else False
          wrap_mongo.change_dest_folder(
            tmp_folder, 
            make=make
          )
          app.config['UPLOAD_FOLDER'] = wrap_mongo.local_settings['tmp_folder']

      if 'api_key' in request.form :
        api_key = request.form['api_key'].strip()
        if api_key != '' :
          wrap_mongo.set_api_key(api_key)

      if 'proxy_url' in request.form :
        proxy_url = request.form['proxy_url'].strip()
        if proxy_url != '' :
          if proxy_url.startswith("http"):
            wrap_mongo.set_proxy(proxy_url)
          else :
            raise Exception("Invalid 'proxy_url' field given")

      status="Ok"

    except Exception as ex:
      status="Fail: " + str(ex)

  settings_data = wrap_mongo.get_updated_settings()
  return render_template(
    'settings.html', 
    folder=settings_data['tmp_folder'], 
    api_key=settings_data['api_key'][:4],
    proxy=settings_data['proxy'],
    status=status
  )




def get_blacklist_words(request_form):
  blacklist_words = {}
  for k,v in request_form.items() :
    if k.startswith("blacklist_word_") :
      if v != "" :
        k2 = int(k.split("_")[-1])
        blacklist_words.update({k2:v.strip()})
  
  output = {}
  for k,v in blacklist_words.items() :
    v2 = 1
    k2 = "blacklist_counter_{}".format(k)
    if k2 in request_form :
      tmp_v2 = request_form[k2].strip()
      if tmp_v2 != '' :
        v2 = int(tmp_v2)
    output.update({v:v2})

  return output


###############################
# /uploadprompt not tested enough
###############################

@app.route('/uploadprompt', methods=['GET', 'POST'])
def uploadprompt():
  status = ""
  get_prompt_field = [
    "name_prompt", 
    "description", 
    "assistant_text", 
    "instruction_text",
    "char_separator", 
    "char_terminator",
    "char_proj_name_holder"
  ]

  if request.method == 'POST' :
    prompt_args = []

    try :
      blacklist_words = get_blacklist_words(request.form)

      for field in get_prompt_field :
        prompt_args.append(request.form[field].strip())
      prompt_args.append(blacklist_words)

      prompt_id = wrap_mongo.add_prompt_entry(*prompt_args)
      status = "Ok. Prompt id:{}".format(prompt_id)

    except Exception as ex :
      status="Fail: " + str(ex)


  else :
    pass

  extra = copy.deepcopy(wrap_mongo.local_settings)
  for x in ['char_proj_name_holder', 'char_separator', 'char_terminator'] :
    extra['default_sets'][x] = repr(extra['default_sets'][x])
  return render_template(
    'uploadprompt.html', 
    status=status,
    extra=extra
  )



def prompt_id_is_valid(request_form):
  rets = None
  if "prompt_id" in request_form :
    try :
      prompt_id = int(request_form['prompt_id'])
      rets = wrap_mongo.get_prompt_entry(prompt_id, enforce_asserts=False)
    except ValueError :
      pass
  return rets


@app.route('/uploadfile', methods=['GET','POST'])
def uploadfile():
  status = ""
  if request.method == 'POST' :

    # check if a valid model has been selected
    prompt_entry = prompt_id_is_valid(request.form)
    if prompt_entry is None :
      status = "Fail 'invalid prompt id given'"

    else :
      # check if the post request has the file part
      if 'file_upload' not in request.files:
        status = "Fail 'file_upload' was not found'"

      else :
        file = request.files["file_upload"]
        if file.filename == '':
          status = "Fail 'No selected file'"

        elif not allowed_file(file.filename):
          status = "Fail 'Invalid format uploaded'"

        else :
          api_key = wrap_mongo.get_api_key()
          if not api_key :
            status = "Fail 'API key is not set'"
          
          else :
            filename = secure_filename(file.filename)
            fullpath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(fullpath)

            type_scan = default_scan
            if "type_scan" in request.form :
              type_scan = int(request.form["type_scan"])

            proj_id, result_id = wrap_mongo.add_blank_entry(
              fullpath,
              id_prompt = prompt_entry['id'],
              delete_proj = "do_delete_scan" in request.form,
              type_scan = type_scan
            )

            if type_scan == SINGLE_SCAN :

              wtime_single_scan = None
              if "wtime_single_scan" in request.form :
                wtime_tmp = request.form["wtime_single_scan"].strip()
                if wtime_tmp != "" :
                  wtime_single_scan = float(wtime_tmp)

              wrap_mongo.update_result_singlescan(
                result_id, 
                single_scan_wtime = wtime_single_scan
              )

            launch_thread(proj_id, result_id)
            status = "Ok. Project id:{}, Result id:{}".format(proj_id, result_id)

  extra = wrap_mongo.local_settings
  prompt_models = wrap_mongo.get_prompts()
  return render_template(
    'uploadfile.html', 
    prompt_models=prompt_models, 
    status=status, 
    extra=extra
  )



## API

@app.route('/api/project', methods=['GET'])
def get_project():
  data = request.args
  if 'id' not in data :
    return ''
  proj_id = int(data['id'])
  proj_entry = wrap_mongo.get_proj_entry(proj_id)
  del proj_entry['_id']
  return str(proj_entry)

@app.route('/api/result', methods=['GET'])
def get_result():
  data = request.args
  if 'id' not in data :
    return ''
  result_id = int(data['id'])
  result_entry = wrap_mongo.get_result_entry(result_id)
  del result_entry['_id']
  return str(result_entry)

@app.route('/api/prompt', methods=['GET'])
def get_prompt():
  data = request.args
  if 'id' not in data :
    return ''
  result_id = int(data['id'])
  result_entry = wrap_mongo.get_prompt_entry(result_id)
  del result_entry['_id']
  return str(result_entry)



if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  parser.add_argument(
    "--mongo_ip",
    default=mongo_ip,
    help="Mongodb ip (default {})".format(mongo_ip)
  )
  parser.add_argument(
    "--host",
    default="0.0.0.0",
    help="Address listening"
  )
  parser.add_argument(
    "--port",
    default=9090,
    help="Port listening"
  )
  parser.add_argument(
    "--debug",
    default=False,
    action="store_true",
    help="Enable Flask debugging mode"
  )
  args = parser.parse_args()
  wrap_mongo = WrapMongo(mongo_ip=args.mongo_ip)
  app.config['UPLOAD_FOLDER'] = wrap_mongo.local_settings['tmp_folder']
  app.run(host=args.host, port=os.environ.get("FLASK_SERVER_PORT", args.port), debug=args.debug)
  # kill -11 `ps aux | grep python | grep defunct | cut -d' ' -f 2`



