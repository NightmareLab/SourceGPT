import openai_prompt.capa_minimal as capa_minimal
import openai_prompt.smartcontract_vuln as smartcontract_vuln
import openai_prompt.rce_taint_analysis as rce_taint_analysis


examples = [
  capa_minimal,
  smartcontract_vuln,
  rce_taint_analysis
]



class PromptClass :

  def __init__(self, prompt):
    self.prompt = prompt

  def validate_data(self, data):
    blacklist = self.prompt['blacklist']
    data = [ x.strip() for x in data.lower().split(" ") if x.strip() != "" ]
    cc = { x:0 for x in blacklist.keys() }
    for x in data:
      if x in cc :
        cc[x] += 1
    for k,v in cc.items() :
      if v >= blacklist[k] :
        return False
    return True

  def assistant(self):
    return self.prompt['text']['assistant']
  
  def instruction(self, *args):
    instruction = self.prompt['text']['instruction']
    char_proj_name_holder = self.prompt['text']['char_proj_name_holder']
    if len(args) > 0 :
      proj_name = args[0]
      if char_proj_name_holder.strip() != '' :
        return instruction.replace(char_proj_name_holder, proj_name)
    return instruction
  
  def body(self, *args):
    char_separator = self.prompt['text']['char_separator']
    filename = args[0]
    text = args[1]
    format_body = "```\nTitle: {0}\nText:\n{1}\n{2}\n\n```".format(
      filename,
      text,
      char_separator
    )
    return format_body
  

  def tail(self):
    char_terminator = self.prompt['text']['char_terminator']
    return "```\n{0}{0}\n```".format(char_terminator)


