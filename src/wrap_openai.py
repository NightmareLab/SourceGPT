import os
import requests
import time


# For now based on free openai api
# https://github.com/PawanOsman/ChatGPT




##### extract from 'init_mongo.py'
# Type of scan
COLLAPSE_SCAN = 0
SINGLE_SCAN = 1
MULTIPLE_SCAN = 2
default_scan = COLLAPSE_SCAN
#####



class WrapException:
  pass

class RetryInitPrompt(WrapException):
  pass


class wrap_openai :

  def __init__(self, 
      proj_name,
      api_key, 
      openai_prompt, 
      openai_server_='proxy',
      model='gpt-3.5-turbo',
      temperature=0.7,
      top_p=0.9,
      frequency_penalty=0,
      presence_penalty=0,
      type_scan=default_scan,
      single_scan_wtime=None,
      openai_proxy_url=None,
      max_tokens=None
    ):
    if openai_server_ == "openai" :
      raise Exception("TODO")
    elif openai_server_ != "proxy" :
      raise Exception("Unknown openai api type '{}'".format(openai_server_))

    self.proj_name = proj_name
    self.url = openai_proxy_url
    self.openai_prompt = openai_prompt
    self.api_key = api_key 
    self.model = model
    self.temperature = temperature
    self.top_p = top_p
    self.frequency_penalty = frequency_penalty
    self.presence_penalty = presence_penalty
    self.type_scan = type_scan
    self.single_scan_wtime = single_scan_wtime
    self.max_tokens = max_tokens
    self.__init_data()


  def __init_data(self):
    self.data_assistant = {
      'role': 'system',
      "content" : self.openai_prompt.assistant()
    }
    self.data_instruction = {
      'role': 'system',
      "content" : self.openai_prompt.instruction(self.proj_name)
    }
    self.headers = {
      'Authorization': f'Bearer {self.api_key}',
      'Content-Type': 'application/json',
    }
    self.data = {
      'model': self.model,
      "temperature": self.temperature,
      "top_p": self.top_p,
      "frequency_penalty": self.frequency_penalty,
      "presence_penalty": self.presence_penalty,
      'messages': []
    }

  def ask(self, query):
    """
      query         : List of query (source code's contents)
      single_query  : for each data do a separate query (default: False)
      multiple_scan : in the same request add multiple messages as the number of files
      t_out         : if single_query, wait 't_out' time after each request
      
      TODO: multiple_scan, and ask_with_openai

    """
    return self.ask_with_proxy(query)


  def ask_with_openai(self, query):
    """
      Here we should extend to openai module
    """
    #TODO
    pass


  def ask_with_proxy(self, query):
    self.data['messages'] = []
    self.data['messages'].append(self.data_assistant)
    self.data['messages'].append(self.data_instruction)

    self.openai_prompt.reset_token_counters()

    output = []
    for q in query :
      output.append(self.openai_prompt.body(*q))
      if self.type_scan == SINGLE_SCAN and \
        self.openai_prompt.latest_total_tokens >= self.max_tokens :
          raise Exception("Can't use single_scan mode on a file with {} tokens".format(
            self.openai_prompt.latest_total_tokens)
          )

    if self.type_scan != MULTIPLE_SCAN :
      self.data['messages'].append({'role':'user', 'content':''})
      self.data['messages'].append({'role':'user', 'content':self.openai_prompt.tail()})

      if self.type_scan == SINGLE_SCAN :
        responses = []

        for i, q in enumerate(output) :
          # note: if we're here, then we know that len(q) is 1
          self.data['messages'][-2]['content'] = q[0]
          resp_q = requests.post(self.url, headers=self.headers, json=self.data)

          rets = self.check_json_response(resp_q)

          responses.append([query[i][0], rets])
          time.sleep(self.single_scan_wtime)

        return responses

      else :
        
        if self.openai_prompt.total_tokens >= self.max_tokens :
          raise Exception("Can't use collapse_scan mode as the tokens are {}".format(
            self.openai_prompt.total_tokens)
          )
 
        # note: if we're here, then we know that len(x) is 1
        self.data['messages'][-2]['content'] = "\n".join([ x[0] for x in output ])
        resp_q = requests.post(self.url, headers=self.headers, json=self.data)
        return self.check_json_response(resp_q)

    else :
      # NOTE: multiple_scan' does not work well with chatgpt plus proxied api
      #       Instead openai api should be used or chatgpt chat
      for i, q in enumerate(output) :
        for j, p in enumerate(q) :
          with open("/tmp/lol123/session{}_{}.txt".format(i,j), "w") as fp :
            fp.write(p)

      for q in output :
        for p in q :
          self.data['messages'].append({'role':'user', 'content':p})

      self.data['messages'].append({'role':'user', 'content':self.openai_prompt.tail()})
      resp_q = requests.post(self.url, headers=self.headers, json=self.data)
      return self.check_json_response(resp_q)


  def check_json_response(self, resp_q):
    try :
      rets = resp_q.json()
    except Exception as ex :
      if "PayloadTooLargeError" in resp_q.text :
        raise Exception("Payload (source code) too large")
      else :
        raise Exception("Unknown response received: {}".format(resp_q.text))
    return rets



