#!/usr/bin/env python
import os
import time
import subprocess
from pymongo import MongoClient

import openai_prompt


## default values

client = None
db_capa = 'db_capa'
db_capa_tab_set = 'db_capa_settings'

default_sets = {
  "char_separator" : """EOF@#^#@""",
  "char_terminator" : """EOF@#:#@\nEOF@#:#@""",
  "char_proj_name_holder" : "<@PROJ_NAME@>",
  "blacklist" : {
    "openai":1, "chatgpt":1, "malware":100, 
    "exploit":100, "hacker":100, "hacking":100
  }
}
 
default_single_scan_wtime = 5  #5s
default_proxy = "https://api.pawan.krd/v1/chat/completions"

# Type of scan
COLLAPSE_SCAN = 0
SINGLE_SCAN = 1
MULTIPLE_SCAN = 2
default_scan = COLLAPSE_SCAN


def get_template():
  template_project = {
    "id" : 0,
    "name" : "",
    "files" : []
  }
  template_result = {
    "date" : 0,
    "id" : 0,
    "id_proj" : 0,
    "id_prompt" : 0,
    "status" : "Uploaded",
    "error" : "",
    "delete_proj" : False,
    "type_scan": default_scan,
    "single_scan_wtime" : 0,
    "result" : '',
    "results" : []
  }
  return template_project, template_result


def get_template_prompt():
  template_prompt = {
    "id" : 0,
    "name" : '',
    "description" : "",
    "text" : {
      "assistant" : '',
      "instruction" : '',
      "char_separator" : default_sets["char_separator"],
      "char_terminator" : default_sets["char_terminator"],
      "char_proj_name_holder" : default_sets["char_proj_name_holder"]
    },
    "blacklist" : default_sets["blacklist"]
  }
  return template_prompt
  

class WrapMongo(object) :

  def mkdir(folder):
    if folder.startswith("-"):
      raise Exception(folder)
    subprocess.run(["mkdir", "-p", folder])

  def is_init_db():
    db = client[db_capa]
    return db_capa_tab_set in list(db.list_collection_names())

  def init_db():
    db = client[db_capa]
    tmp_folder =  "/tmp/{}".format(db_capa)
    WrapMongo.mkdir(tmp_folder)
    db_tab = db[db_capa_tab_set]
    data = {
      'id_project' : 0,
      'id_result' : 0,
      'id_prompt' : 0,
      'api_key' : '',
      'proxy' : default_proxy,
      "tmp_folder" : tmp_folder,
      "default_sets" : default_sets,
      "default_wtime" : 5
    }
    db[db_capa_tab_set].insert_one(data)



  def __init__(self, mongo_ip="mongo", mongo_port=27017):
    global client
    client = MongoClient("{}:{}".format(mongo_ip, mongo_port))
    #
    object.__init__(self)
    self.client = client
    self.db = self.client[db_capa]
    if not WrapMongo.is_init_db():
      WrapMongo.init_db()
      self.__update_local_view()
      self.build_example()
      self.add_prompt_examples()
    else :
      self.__update_local_view()


  def is_admin(self):
    try:
      self.client.admin.command('ismaster')
    except:
      return "Server not available"
    return "Hello from the MongoDB client!\n"

  def __update_local_view(self):
    self.local_settings = self.__get_settings()

  def __update_db_view(self):
    tmp_local_settings = self.local_settings.copy()
    query = {"_id" : tmp_local_settings["_id"]}
    del tmp_local_settings['_id']
    self.db[db_capa_tab_set].update_one(query, {"$set":tmp_local_settings})

  def set_api_key(self, api_key):
    self.local_settings["api_key"] = api_key
    self.__update_db_view()

  def get_api_key(self):
    return self.local_settings["api_key"]

  def set_proxy(self, proxy):
    self.local_settings["proxy"] = proxy
    self.__update_db_view()

  def get_proxy(self):
    return self.local_settings["proxy"]


  def __get_settings(self):
    return list(self.db[db_capa_tab_set].find())[0]

  def get_updated_settings(self):
    self.__update_local_view()
    return self.local_settings

  def increment_id(self, target="id_project", update_set=True):
    rets = self.local_settings[target]
    self.local_settings[target] = rets + 1
    if update_set :
      self.__update_db_view()
    return rets

  def change_dest_folder(self, tmp_folder, make=False):
    if make :
      WrapMongo.mkdir(tmp_folder)
    if not os.path.isdir(tmp_folder):
      raise Exception("Folder '{}' does not exists or is not a folder".format(tmp_folder))
    self.local_settings['tmp_folder'] = tmp_folder
    self.__update_db_view()


  def check_tab_db(self, tab_name):
    assert(tab_name != None)
    assert(tab_name in list(self.db.list_collection_names()))

  def get_table(self, tab_name=None):
    self.check_tab_db(tab_name)
    return self.db[tab_name]

  def insert_db(self, data, tab_name=None):
    assert(tab_name != None)
    assert(isinstance(data, list) or isinstance(data, dict))
    if isinstance(data, list) :
      self.db[tab_name].insert_many(data)
    else:
      self.db[tab_name].insert_one(data)

  def get_db_projects(self):
    return self.get_table("projects")

  def get_db_results(self):
    return self.get_table("results")

  def get_db_prompt(self):
    return self.get_table("prompt")

  def insert_db_projects(self, data):
    return self.insert_db(data, "projects")

  def insert_db_results(self, data):
    return self.insert_db(data, "results")

  def insert_db_prompt(self, data):
    return self.insert_db(data, "prompt")

  def get_results(self):
    tab = self.get_db_results()
    tab = tab.find().sort("date",-1)
    output = []
    for x in tab :
      result = x['result']
      results = x['results']

      if result :
        if 'error' not in result :
          x['result'] = result['choices'][0]['message']['content']
        else :
          x['result'] = "Openai error"

      elif results :
        for i,y in enumerate(results) :
          if 'error' not in y[1] :
            x['results'][i][1] = y[1]['choices'][0]['message']['content']
          else :
            x['results'][i][1] = "Openai error"
      else :
        # empty
        pass

      output.append(x)
    return output


  def get_prompts(self):
    tab = self.get_db_prompt()
    tab = tab.find().sort("id",1)
    output = []
    for x in tab :
      output.append( {
        'id' : x['id'],
        'name' : x['name'],
        'description' : x['description'],
        'assistant' : x['text']['assistant'],
        'instruction' : x['text']['instruction']
      })
    return output


  def get_entry(self, _id, tab_name="results", enforce_asserts=True):
    tab = self.get_table(tab_name)
    rets = list(tab.find({ "id": _id }))
    if enforce_asserts :
      assert len(rets) > 0, "{} id '{}' not present".format(tab_name, _id)
      assert len(rets) == 1, "{} id '{}' duplicates found (length:{}, data:{})".format(tab_name, _id, len(rets), rets)
    if rets :
      return rets[0]
    return None

  def get_result_entry(self, result_id, enforce_asserts=True):
    return self.get_entry(result_id, enforce_asserts=enforce_asserts)

  def get_proj_entry(self, proj_id, enforce_asserts=True):
    return self.get_entry(proj_id, tab_name="projects", enforce_asserts=enforce_asserts)

  def get_prompt_entry(self, prompt_id, enforce_asserts=True):
    return self.get_entry(prompt_id, tab_name="prompt", enforce_asserts=enforce_asserts)

  def update_proj_name(self, proj_id, name):
    query = {"id" : proj_id}
    self.db["projects"].update_one(query, {"$set":{"name":name}})

  def update_proj_files(self, proj_id, files):
    query = {"id" : proj_id}
    self.db["projects"].update_one(query, {"$set":{"files":files}})

  def update_result_status(self, result_id, status, error=''):
    query = {"id" : result_id}
    self.db["results"].update_one(query, {"$set":{"status":status, "error":error}})

  def update_result_results(self, result_id, result_data, results_data):
    query = {"id" : result_id}
    self.db["results"].update_one(
      query, 
      {
        "$set":{
          "result":result_data, 
          "results":results_data
        }
      }
    )

  def update_result_singlescan(self, result_id, single_scan_wtime=None):
    query = {"id" : result_id}

    if single_scan_wtime is None :
      single_scan_wtime = default_single_scan_wtime

    self.db["results"].update_one(
      query, 
      {
        "$set":{
          "single_scan_wtime":single_scan_wtime
        }
      }
    )

  def add_blank_entry(self, 
      fullpath_name, 
      id_prompt=0, 
      delete_proj=False,
      type_scan=default_scan
    ):
    project, result = get_template()
    proj_id = self.increment_id()
    result_id = self.increment_id("id_result")
    project['id'] = proj_id
    project['name'] = fullpath_name # .*\.zip
    result['id'] = result_id
    result['id_proj'] = proj_id
    result['id_prompt'] = id_prompt
    result['date'] = time.time()
    result['delete_proj'] = delete_proj
    result['type_scan'] = type_scan
    self.insert_db_projects(project)
    self.insert_db_results(result)
    return proj_id, result_id

  def add_prompt_entry(self, 
      name,
      description,
      assistant,
      instruction,
      char_separator=None,
      char_terminator=None,
      char_proj_name_holder=None,
      blacklist=None
    ):

    assert name, "'name' prompt field is None"
    assert description, "'description' prompt field is None"
    assert assistant, "'assistant' prompt field is None"
    assert instruction, "'instruction' prompt field is None"

    assert name != '' , "'name' prompt field can't be ''"
    assert assistant != '', "'assistant' prompt field can't be ''"
    assert instruction, "'instruction' prompt field can't be ''"

    prompt = get_template_prompt()
    prompt_id = self.increment_id("id_prompt")
    prompt['id'] = prompt_id
    prompt['name'] = name
    prompt['description'] = description

    set_text = lambda x, y : prompt['text'].update({x:y})
    prompt_arg = [
      'assistant', 'instruction', 'char_separator', 
      'char_terminator', 'char_proj_name_holder'
    ]
 
    for x in prompt_arg :
      loc_x = locals()[x]
      if loc_x != None :
        set_text(x, loc_x)

    if blacklist :
      prompt['blacklist'] = blacklist

    self.insert_db_prompt(prompt)
    return prompt_id


#################### Examples

  def build_example(self):
    """
      Exanple of project and result entries
    """
    project, result = get_template()
    project['name'] = 'test1'
    project['files'] = ["poc.c", "poc.ver", "readme.md"]
    # date field generated with: time.strftime("%H:%M:%S %Y-%m-%d", time.gmtime())
    result['date'] = 1680729159
    result['status'] = "Completed"
    result['result'] = {'model': 'text-davinci-003', 'object': 'chat.completion', 'choices': [{'finish_reason': 'stop', 'index': 0, 'message': {'content': 'Based on the programming language used, which is C, I can update the following counters:\n- check for OutputDebugString error\n- read and send data from client to server\n- execute shell command and capture output\n- receive data\n- send data\n- connect to HTTP server\n- send HTTP request\n- create pipe\n- get socket status\n- receive data on socket\n- send data on socket\n- connect TCP socket\n- encode data using Base64\n- encode', 'role': 'assistant'}}], 'usage': {'prompt_tokens': 1048, 'completion_tokens': 99, 'total_tokens': 1147}}
    project['id'] = self.increment_id()
    result['id'] = self.increment_id("id_result")
    self.insert_db_projects(project)
    self.insert_db_results(result)


  def add_prompt_examples(self):
    """
      Add default prompt on folder 'openai_prompt'

      Exaples given:
       - capa_minimal.py
       - smartcontract_vuln.py
       - rce_taint_analysis.py
       - find_weak_chiper.py
    """
    for x in openai_prompt.examples :
      f1 = lambda y : getattr(x,y)
      self.add_prompt_entry(
        f1('name'),
        f1('description'),
        f1('assistant'),
        f1('instruction'),
        f1('char_separator'),
        f1('char_terminator'),
        f1('char_proj_name_holder'),
        f1('blacklist')
      )


