import os
import requests
import time


# For now based on free openai api
# https://github.com/PawanOsman/ChatGPT


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
      single_scan_wtime=None,
      openai_proxy_url=None
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
    self.single_scan_wtime = single_scan_wtime
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

  def ask(self, 
      query, 
      single_scan=False, 
      multiple_scan=False
    ):
    """
      query         : List of query (source code's contents)
      single_query  : for each data do a separate query (default: False)
      multiple_scan : in the same request add multiple messages as the number of files
      t_out         : if single_query, wait 't_out' time after each request
      
      TODO: multiple_scan, and ask_with_openai

    """
    return self.ask_with_proxy(
      query, 
      single_scan=single_scan, 
      multiple_scan=False
    )


  def ask_with_openai(self, 
      query, 
      single_scan=False, 
      multiple_scan=False
    ):
    """
      Here we should extend to openai module
    """
    #TODO
    pass


  def ask_with_proxy(self, 
      query, 
      single_scan=False, 
      multiple_scan=False
    ):
    self.data['messages'] = []
    self.data['messages'].append(self.data_assistant)
    self.data['messages'].append(self.data_instruction)

    output = []
    for q in query :
      output.append( self.openai_prompt.body(*q) )

    if not multiple_scan :
      self.data['messages'].append({'role':'user', 'content':''})
      self.data['messages'].append(self.openai_prompt.tail())

      if single_scan :
        responses = []
        for i, q in enumerate(output) :
          self.data['messages'][-2]['content'] = q
          resp_q = requests.post(self.url, headers=self.headers, json=self.data)
          responses.append([query[i][0], resp_q.json()])
          time.sleep(self.single_scan_wtime)

        return responses

      else :
        self.data['messages'][-2]['content'] = "\n".join(output)
        resp_q = requests.post(self.url, headers=self.headers, json=self.data)

        try :
          rets = resp_q.json()
        except Exception as ex :
          if "PayloadTooLargeError" in resp_q.text :
            raise Exception("Payload (source code) too large")
          else :
            raise Exception("Unknown response received: {}".format(resp_q.text))

        return rets

    else :
      raise Exception(
        "'multiple_scan' does not work well with chatgpt plus proxied api. " +\
        "Instead openai api should be used"
      )


