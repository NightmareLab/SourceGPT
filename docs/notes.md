
## 1 Nothing is Free
 - The code given, before being passed to openai servers, is passed to the proxy hosted by project https://github.com/PawanOsman/ChatGPT. Before having access to their proxy you need to request an API key, link https://gist.github.com/PawanOsman/72dddd0a12e5829da664a43fc9b9cf9a.


## 2 Host your own proxy
 - To host your own reverse proxy, chatgpt plus account is required (https://github.com/PawanOsman/ChatGPT#self-host-your-own-api).
 - Also note that the proxy they host does not give you the model `gpt-3.5-turbo` but instead only `text-davinci-003`, but maybe i am wrong. 
 - Still if you want better results you should host your own reverse proxy, because then you would be able to control the `chat id` which keeps track of a conversation and can be used to keep history of the chats and also can be used by chatgpt to keep its responses aligned with your initial request


## 3 Change reverse proxy API
 - If we do not like how the reverse proxy web API is hosted we can implement our own APIs, in fact the reverse proxy part, which does escape OpenAI captcha, is taken from this project https://github.com/acheong08/ChatGPT-Proxy-V4 (ChatGPT plus account is required)


## 4 Openai API
 - Not supported yet sorry. We do not have access to it otherwise we can implement that in future. But if you stil want to add it, i would suggest to start by modifying `wrap_openai.py`'s methods `__init__, ask, ask_with_openai`


## 5 Where is the source code saved
 - As default `/tmp/db_capa` folder is used to save the uploaded source code (.zip) files (you can change it on the settings page)
 - Each project is saved into folder `res<id>` with 'id' as the project id that was assigned before. 
 - When the mongodb schemas are deleted remember also to delete `/tmp/db-capa`'s content as no delete option is permitted via web after you uploaded a project if the delete checkbox wasn't selected. If you need to delete projects add the web feature or do it by yourself.


