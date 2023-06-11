"""
LangWizard is a open source extensible package for chaining together prompts.
"""
from copy import deepcopy
import re
from typing import List, Dict, Set, Tuple, Union
import yaml

from app.prompt_error import NoPromptException
from app.sha_hash import hash_message_sha_256
from app.database_adapters import InputAdapter
from app.openai_utils import num_tokens_from_string


class LangWizard:
    """ Base LangWizard """

    @staticmethod
    def load_yaml(file_path: str) -> Dict:
        """ Load a yaml file into memory """
        return yaml.safe_load(open(file_path, encoding='utf-8'))

    @staticmethod
    def find_keywords(content: str, keywords: List[str]) -> Set:
        """ Find the set of keywords that appear in the text """
        found = []
        for text in content:
            for keyword in keywords:
                if re.search(keyword, text):
                    found.append(keyword)
        return set(found)

    @staticmethod
    def tuple_column(rows: List, column_number: int) -> List[str]:
        """ get a column from a list of tuples """
        temp = []
        for row in rows:
            if row[column_number] is not None:
                temp.append(row[column_number])
        return temp

    @staticmethod
    def num_interrogations(keyword_replacements: Dict) -> int:
        """ get the number of times that an interrogation will occur """
        found_max = 0
        for key in keyword_replacements:
            if isinstance(keyword_replacements[key], str):
                i = 1
            else:
                i = len(keyword_replacements[key])
            if i > found_max:
                found_max = i
        return found_max

    def __init__(self,
                 endpoints_yaml_path,
                 rollback_query_max,
                 surrounding_special,
                 ai_adapters,
                 stream_output=True,
                 pinecone_adapter=None,
                 storage_adapter=None,
                 input_adapter=InputAdapter(),
                 rollback_token_length=3500):
        self.endpoints_yaml_path = endpoints_yaml_path
        self.rollback_query_max = rollback_query_max
        self.surrounding_special = surrounding_special

        yaml_loaded = self.load_yaml(endpoints_yaml_path)
        self.endpoints = yaml_loaded['endpoints']
        self.keywords = yaml_loaded['keywords']

        self.keywords_index = {list(k.keys())[0]: i for i, k in enumerate(self.keywords)}

        self.stream = stream_output

        self.storage_adapter = storage_adapter
        self.ai_adapters = ai_adapters
        self.database_adapters = {'pinecone': pinecone_adapter, 'input': input_adapter}

        self.rollback_token_length = rollback_token_length

    def get_endpoint_key(self, endpoint: str, key: str, error_return: str) -> str:
        """ get from the endpoint dictionary a key """
        try:
            return self.endpoints[endpoint][key]
        except KeyError:
            return error_return

    def get_interrogation(self, endpoint: str) -> Dict:
        """ get the interrogation dict or an empty dict """
        return self.get_endpoint_key(endpoint, "interrogation", {})

    def get_prompt(self, endpoint: str) -> Dict:
        """ get the prompt dict or an empty dict """
        return self.get_endpoint_key(endpoint, "prompt", {})

    def get_keywords(self) -> List:
        """ Ket a list of keywords """
        return [list(k.keys())[0] for k in self.keywords]

    def surround_with_surrounding_special(self, text: str) -> str:
        """ Surrounding text around the prompt keywords """
        if self.surrounding_special == "()":
            return "\\" + self.surrounding_special[0] + text + "\\" + self.surrounding_special[1]
        return self.surrounding_special[0] + text + self.surrounding_special[1]

    def search_for_keywords(self, interrogation: List[Dict], prompt: List[Dict]) -> List[str]:
        """ Search the prompt and interrogation for keywords """
        keywords = self.get_keywords()
        keywords_surrounded = [self.surround_with_surrounding_special(k) for k in keywords]

        content = [message['content'] for message in interrogation]
        content += [message['content'] for message in prompt]

        found = self.find_keywords(content, keywords_surrounded)
        found_words = [f[1: -1] for f in found]
        return found_words

    def get_keyword_store(self, keyword: str) -> str:
        """ Find which database a keyword should be extracted from """
        keyword_index = self.keywords_index[keyword]
        store = self.keywords[keyword_index][keyword]['store']
        return store

    def get_keyword_config(self, keyword: str) -> Tuple:
        """ Congifuration of a keyword
            return keyword store and key 
        """
        keyword_index = self.keywords_index[keyword]

        store = self.keywords[keyword_index][keyword]['store']
        if 'key' in self.keywords[keyword_index][keyword].keys():
            key = self.keywords[keyword_index][keyword]['key']
        else:
            key = None

        # if 'interrogate' in self.keywords[keyword_index][keyword].keys():
        #     interrogate = self.keywords[keyword_index][keyword]['key']
        # else:
        #     interrogate = None

        return keyword, store, key#, interrogate

    def query_keywords(self, message: str, found_keywords: List[str]):
        """ Using the appropriate database adapter get the details for a given keyword
            Note that per keyword if the keyword has the same database adapter
                the queries will be checked to see if the data already exists
                and if it does then it will not query again 
        """
        keyword_configs = []
        for keyword in found_keywords:
            keyword_configs.append(self.get_keyword_config(keyword))

        queried_databases = {}
        keyword_replacements = {}
        content_ids = {}

        for config in keyword_configs:
            database = config[1]
            database_adapter = self.database_adapters[database]

            if database in queried_databases:
                documents = queried_databases[database]
            else:
                documents = database_adapter.query(message)
                queried_databases[database] = documents

            content = database_adapter.pull_key_from_responses(documents, config[2])
            keyword_replacements[config[0]] = content
            content_ids[config[0]] = database_adapter.pull_id_from_reponses(documents)
        return keyword_replacements, content_ids

    def replace_content_in_chat_indexed(self,
                                        prompt: List[Dict],
                                        keyword: str,
                                        replacement_list: List,
                                        i: int) -> List[Dict]:
        """ For interrogations index replacements is required. """
        temp_prompt = []
        keyword_search_text = self.surround_with_surrounding_special(keyword)
        for chat in prompt:
            content = chat['content']
            if re.search(keyword_search_text, chat['content']):
                if self.get_keyword_store(keyword) == 'input':
                    content = re.sub(keyword_search_text, replacement_list[0].strip(), content)
                else:
                    content = re.sub(keyword_search_text, replacement_list[i].strip(), content)
            temp_chat = {
                "role": chat["role"],
                "content": content
            }
            temp_prompt.append(temp_chat)
        return temp_prompt

    def rollback_list(self, replacement_list):
        """ Generates a content replacement that is less than a 
            given size of tokens.
        """
        for i in range(len(replacement_list), 0, -1):
            content = ""
            for j in range(0, i, 1):
                content += str(replacement_list[j])
            if num_tokens_from_string(content, "cl100k_base") < self.rollback_token_length:
                return content.strip()
        return str(replacement_list[0]).strip()

    def replace_content_in_chat(self,
                                prompt: List[Dict],
                                keyword: str,
                                replacement_list: Union[List[str], str]) -> List[Dict]:
        """ replaces a keyword in a prompt with either a rollback or with a the most likely answer. """
        temp_prompt = []
        keyword_search_text = self.surround_with_surrounding_special(keyword)
        for chat in prompt:
            content = chat['content']
            if re.search(keyword_search_text, chat['content']):
                if isinstance(replacement_list, str):
                    content = re.sub(keyword_search_text, replacement_list.strip(), content)
                else:
                    if self.rollback_token_length:
                        #TODO RE.ERROR fix %s
                        content = re.sub(keyword_search_text,
                                         self.rollback_list(replacement_list),
                                         content)
                    else:
                        content = re.sub(keyword_search_text,
                                         str(replacement_list[0]).strip(),
                                         content)
            temp_chat = {
                "role": chat["role"],
                "content": content
            }
            temp_prompt.append(temp_chat)
        return temp_prompt

    def replace_interrogation_text(self,
                                   interrogation: List[Dict],
                                   keyword_replacements: Dict,
                                   i: int) -> List[Dict]:
        """ Replaces the interrogation text with the found keywords associated content """
        copied_interrogation = deepcopy(interrogation)
        for keyword in [list(k.keys())[0] for k in self.keywords]:
            copied_interrogation = self.replace_content_in_chat_indexed(
                copied_interrogation,
                keyword,
                keyword_replacements[keyword],
                i)
        return copied_interrogation

    def replace_prompt_text(self, prompt: List[Dict], keyword_replacements: Dict) -> List[Dict]:
        """ replace keywords with the most likely replacement """
        copied_prompt = deepcopy(prompt)
        for keyword in [list(k.keys())[0] for k in self.keywords]:
            copied_prompt = self.replace_content_in_chat(
                copied_prompt,
                keyword,
                keyword_replacements[keyword])
        return copied_prompt

    @staticmethod
    def clean_interrogation_text(text: str) -> str:
        """ remove periods and lower case a string """
        text = re.sub(r'\.', '', text)
        return text.lower()

    def interrogate_replacements(self, interrogation, keyword_replacements, ai_adapter=None):
        """ for each of the interrogations question the content replacements
            When the answer becomes a yes, end the interrogation and deliver the content
        """
        num_interrogations = self.num_interrogations(keyword_replacements)
        for i in range(num_interrogations):
            temp_interrogation = deepcopy(interrogation)
            replacement_interrogation = self.replace_interrogation_text(
                temp_interrogation,
                keyword_replacements,
                i)

            ai_adapter = self.select_ai_adapter(ai_adapter)
            answer = ai_adapter.chat(replacement_interrogation)
            answer = self.clean_interrogation_text(answer)

            if answer == "no":
                continue
            return True, replacement_interrogation, i
        return False, interrogation, 0

    def select_keyword_replacements(self,
                                    keyword_replacements: Dict,
                                    content_ids: Dict, i: int) -> List[Dict]:
        """ select the proper replacements from the interrogation """
        if i == -1:
            i = 0
        temp_keyword_replacements = {}
        for keyword in keyword_replacements:
            if self.get_keyword_store(keyword) == 'input':
                temp_keyword_replacements[keyword] = keyword_replacements[keyword][0]
                temp_keyword_replacements['input_id'] = content_ids[keyword][0]
            else:
                temp_keyword_replacements[keyword] = keyword_replacements[keyword][i]
                temp_keyword_replacements[self.get_keyword_store(keyword)] = content_ids[keyword][i]
        return temp_keyword_replacements

    def batch_or_stream(self, messages, ai_adapter=None):
        """ return either a generator or a total piece of content """
        ai_adapter = self.select_ai_adapter(ai_adapter)
        if self.stream:
            return ai_adapter.chat_stream(messages)
        return ai_adapter.chat(messages)

    def make_storeage_interaction(self,
                                  message: str,
                                  keyword_replacements,
                                  storage_keys: List) -> Dict:
        """ Create both the payload and primary key for storage. """
        payload = deepcopy(keyword_replacements)
        message_hash = hash_message_sha_256(message)
        keys = [message_hash] + storage_keys
        return keys, payload

    def store_interaction(self,
                          message: str,
                          keyword_replacements,
                          storage_keys: List) -> Dict:
        """ given a storage adapater store a message with contents and metadata """
        keys, payload = self.make_storeage_interaction(message,
                                                       keyword_replacements,
                                                       storage_keys)
        self.storage_adapter.store(payload, keys)
        return {'key': keys, 'payload': payload}

    def select_ai_adapter(self, aiadapter):
        """ select between adapters or default first adapter """
        if aiadapter in self.ai_adapters:
            return self.ai_adapters[aiadapter]
        return self.ai_adapters[list(self.ai_adapters.keys())[0]]

    @staticmethod
    def keyword_nullification(keyword_replacements):
        payload = deepcopy(keyword_replacements)
        for keyword in keyword_replacements:
            payload[keyword] = ''
        return payload

    def endpoint_responce(self, endpoint, message, storage_keys=None, ai_adapter=None):
        """ Main function of the langwizard
            Using the endpoints yaml file to both interrogate the incoming data from keywords
                and to react with the proper prompt.
           """
        prompt = self.get_prompt(endpoint)
        if not prompt:
            raise NoPromptException

        interrogation = self.get_interrogation(endpoint)

        found_keywords = self.search_for_keywords(interrogation, prompt)

        keyword_replacements, content_ids = self.query_keywords(message, found_keywords)

        found = True
        if interrogation:
            found, interrogation, replacement_index = self.interrogate_replacements(interrogation,
                                                                                    keyword_replacements,
                                                                                    ai_adapter)
            keyword_replacements = self.select_keyword_replacements(keyword_replacements,
                                                                    content_ids,
                                                                    replacement_index)

        if found is False:
            output = ["There were no documents in my records that could answer that question."]
            keyword_replacements = self.keyword_nullification(keyword_replacements)
        else:
            prompt = self.replace_prompt_text(prompt, keyword_replacements)
            output = self.batch_or_stream(prompt, ai_adapter)

        if self.storage_adapter:
            storage_json = self.store_interaction(message, keyword_replacements, storage_keys)
        else:
            keys, payload = self.make_storeage_interaction(message, keyword_replacements, storage_keys)
            storage_json = {
                "keys": keys,
                "payload": payload
            }

        return output, keyword_replacements, storage_json
