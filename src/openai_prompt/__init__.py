import openai_prompt.capa_minimal as capa_minimal
import openai_prompt.smartcontract_vuln as smartcontract_vuln
import openai_prompt.rce_taint_analysis as rce_taint_analysis

import tokenize
from io import BytesIO


examples = [
  capa_minimal,
  smartcontract_vuln,
  rce_taint_analysis
]


try_encoder = ['utf-8', 'ascii', 'cp437']


class PromptClass :

  def __init__(self, prompt, max_tokens):
    self.prompt = prompt
    self.max_tokens = max_tokens

  def reset_token_counters(self):
    """
      self.total_tokens : Representing the total amount of tokens used for all the files, 
        needed for collapse mode, as we need to know if all can be sent in one request

      self.latest_total_tokens : Token counter of the latest file parsed, needed for
        single request mode, because then we know the file can't be sent in only one request

    """
    self.total_tokens = 0
    self.latest_total_tokens = 0

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

    format_str = "```\nTitle: {}\nPart: 100\nText:\n\n{}\n\n```".format(filename, char_separator)
    format_str_tokens = len(list(tokenize.tokenize(BytesIO(format_str.encode('utf-8')).readline)))
    max_tokens = (self.max_tokens - format_str_tokens)

    text_lines = text.split("\n")
    text_enc = None
    for enc in try_encoder :
      try :
        text.encode(enc)
        text_enc = enc
        break
      except :
        pass
    if text_enc == None :
      raise Exception("Can't encode file's content '{}'".format(filename))

    return self.split_body(filename, char_separator, text_lines, text_enc, max_tokens)


  def _update_token_counters(self, cc):
    self.latest_total_tokens += cc
    self.total_tokens += cc


  def split_body(self, filename, char_separator, text_lines, text_enc, max_tokens):
    self.latest_total_tokens = 0
    body = []
    part = 0
    cc_line_tokens = 0
    cc_index = 0

    for i,x in enumerate(text_lines) :
      x_enc = x.encode(text_enc)

      # Note: No time rn but because of some issue with BytesIO + tokenize, replace enclosure chars
      # e.g. len( list( tokenize.tokenize(BytesIO(b"start { end").readline) ))
      # will raise: tokenize.TokenError: ('EOF in multi-line statement', (2, 0))
      for chr_rep in list("{}[]()") :
        x_enc = x_enc.replace(chr_rep.encode(), b".")

      current_tokens = len(list(tokenize.tokenize(BytesIO(x_enc).readline))) + 1

      # if current line has more than max_tokens, not supported sorry
      if current_tokens >= max_tokens :
        raise Exception(
          "Text line with more than {} tokens are not supported".format(
            max_tokens
          )
        )

      next_cc_line = cc_line_tokens + current_tokens

      if next_cc_line >= max_tokens :
        self._update_token_counters(cc_line_tokens)

        body.append(
          self.__body(
            filename,
            "\n".join(text_lines[cc_index:i]) + "\n",
            char_separator
          )
        )

        cc_index = i
        cc_line_tokens = current_tokens
        part += 1

      else :
        cc_line_tokens = next_cc_line

    self._update_token_counters(cc_line_tokens)

    body.append(
      self.__body(
        filename,
        "\n".join(text_lines[cc_index:i+1]),
        char_separator
      )
    )

    for i, x in enumerate(body):
      body[i] = x(part)
      part -= 1

    return body


  def __body(self, filename, text, char_separator):
    def body_internal(part):
      format_body = "```\nTitle: {0}\nPart: {1}\nText:\n{2}\n{3}\n\n```".format(
        filename,
        part,
        text,
        char_separator
      )
      return format_body
    return body_internal 


  def tail(self):
    char_terminator = self.prompt['text']['char_terminator']
    return "```\n{0}{0}\n```".format(char_terminator)


