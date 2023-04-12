from init_mongo import  get_template_prompt ,\
                        get_template_extensions


# 1. import your module HERE:
import extension.skel as skel

# 2. append the new module 
extns_list = [skel]



########### From here don't touch 

lookup_extns_list = { extns.name : extns for extns in extns_list }

def add_prompt(wrap_mongo, extns):
  prompt = get_template_prompt()
  prompt_id = wrap_mongo.increment_id("id_prompt")
  prompt['id'] = prompt_id
  prompt['name'] = extns.prompt_name
  prompt['description'] = extns.prompt_description

  set_text = lambda x, y : prompt['text'].update({x:y})
  prompt_arg = [
    'assistant', 'instruction', 'char_separator',
    'char_terminator', 'char_proj_name_holder'
  ]
  for x in prompt_arg :
    loc_x = getattr(extns, x)
    if loc_x != "" :
      set_text(x, loc_x)

  prompt["extra_replacer"] = extns.extra_replacer.copy()
  wrap_mongo.insert_db_prompt(prompt)
  return prompt_id


def add_extension(wrap_mongo, extns):
  id_prompt = add_prompt(wrap_mongo, extns)
  extension_id = wrap_mongo.add_extension_entry(
    extns.name,
    extns.description,
    id_prompt,
    extns.html_file,
    extra = extns.extra
  )
  return extension_id


def init(wrap_mongo):
  id_extns_list = []
  func_extns_list = []

  if not wrap_mongo.get_extension_flag() :
    for extns in extns_list :
      id_extns_list.append(add_extension(wrap_mongo, extns))
      func_extns_list.append(extns.main)

    wrap_mongo.set_extension_flag()

  else :
    for extns in wrap_mongo.get_extensions() :
      extns_module = lookup_extns_list[extns['name']]
      id_extns_list.append(extns['id'])
      func_extns_list.append(extns_module.main)

  return WrapExtension(id_extns_list, func_extns_list)



class WrapExtension:

  def __init__(self, id_list, func_list) :
    """
      self.id_list : Extension's IDs list 
      self.func_list : Extension's functions list
      self.trampoline : Dictionary id-function
    """
    self.id_list = id_list
    self.func_list = func_list
    self.trampoline = {}
    for i, id_ in enumerate(self.id_list) :
      self.trampoline.update({id_:self.func_list[i]})


  def f(self, id_, *args, **kwargs):
    if id_ in self.trampoline :
      return self.trampoline[id_](id_, *args, **kwargs)
    else :
      raise Exception("Invalid '{}' extension id".format(id_)) 



