# Copyright 2021 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the 'License');
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an 'AS IS' BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


import time
import json
import logging
from typing import Dict, Any, Sequence

import requests

from error.error_handling import ErrorHandler
from models.execution import Batch
from uploaders import utils
from uploaders.uploaders import MegalistaUploader

# Petlove
from datetime import datetime


class GoogleAnalytics4MeasurementProtocolUploaderDoFn(MegalistaUploader):
  def __init__(self, error_handler: ErrorHandler):
    super().__init__(error_handler)
    self.API_URL = 'https://www.google-analytics.com/mp/collect'
    self.API_DEBUG_URL = 'https://www.google-analytics.com/debug/mp/collect'
    self.reserved_keys = ['app_instance_id', 'client_id', 'uuid', 'user_id', 'timestamp_micros']

  def start_bundle(self):
    pass

  @staticmethod
  def _str2bool(s: str) -> bool:
    return s.lower() == 'true'

  @staticmethod
  def _exactly_one_of(a: Any, b: Any) -> bool:
    return (a and not b) or (not a and b)

  @staticmethod
  def _validate_param(key: str, value: Any, reserved_keys: Sequence[str]) -> bool:
    return key not in reserved_keys and value is not None and value != ''

  @utils.safe_process(logger=logging.getLogger('megalista.GoogleAnalytics4MeasurementProtocolUploader'))
  def process(self, batch: Batch, **kwargs):
    return self.do_process(batch)

  # Created to facilitate testing without going into @utils.safe_process
  def do_process(self, batch: Batch):
    execution = batch.execution

    api_secret = execution.destination.destination_metadata[0]
    is_event = self._str2bool(execution.destination.destination_metadata[1])
    is_user_property = self._str2bool(execution.destination.destination_metadata[2])
    non_personalized_ads = self._str2bool(execution.destination.destination_metadata[3])

    # logging.getLogger('megalista.GoogleAnalytics4MeasurementProtocolUploader').info(f"[PETLOVE] api_secret: {api_secret}")
    # logging.getLogger('megalista.GoogleAnalytics4MeasurementProtocolUploader').info(f"[PETLOVE] is_event: {is_event}")
    # logging.getLogger('megalista.GoogleAnalytics4MeasurementProtocolUploader').info(f"[PETLOVE] is_user_property: {is_user_property}")
    # logging.getLogger('megalista.GoogleAnalytics4MeasurementProtocolUploader').info(f"[PETLOVE] non_personalized_ads: {non_personalized_ads}")


    # # Petlove
    # def str_to_timestamp_micros(sheet_date):
    #   try: 
    #     data = datetime.strptime(sheet_date, "%Y-%m-%d %H:%M:%S.%f")
    #     return int(data.timestamp()) * 1000000
      
    #   except Exception as err:
    #     raise ValueError(f'Missing start date information. Received: {sheet_date}. Exception: {err}')
      
      

    firebase_app_id = None
    if len(execution.destination.destination_metadata) >= 5:
      firebase_app_id = execution.destination.destination_metadata[4]

    # Petlove
    conversion_name = None

    measurement_id = None
    if len(execution.destination.destination_metadata) >= 6:
      #measurement_id = execution.destination.destination_metadata[5]
 
      logging.getLogger('megalista.GoogleAnalytics4MeasurementProtocolUploader').info(f"[PETLOVE] execution.destination.destination_metadata: {execution.destination.destination_metadata}")
      conversion_name = execution.destination.destination_metadata[5]

  # Calcula o start_date que será passado para consultar a tabela 
  # Caso esteja como "YYYY-MM-DD HH:mm:SS.fff" irá retornar os últimos 3d; Caso esteja como uma data seguindo o padrão
  # "YYYY-MM-DD HH:mm:SS.fff" irá consultar dessa data

    # start_date = str()
    # destination_metadata_start_date = execution.destination.destination_metadata[6]
    
    # if destination_metadata_start_date  == "YYYY-MM-DD HH:mm:SS.fff":
    #   today = datetime.now()
    #   unix_today = int(datetime(today.year, today.month, today.day, 23, 59, 59).timestamp())
    #   unix_three_days = 86400 * 3
    #   start_date = int((unix_today - unix_three_days) * 1000000)
     
    # elif destination_metadata_start_date != "YYYY-MM-DD HH:mm:SS.fff":
    #   try:
    #     start_date = str_to_timestamp_micros(destination_metadata_start_date) 
     
    #   except Exception as error:
    #       raise ValueError(f'Invalid format date of start_date. Received: {destination_metadata_start_date}. Expected: \"YYYY-MM-DD HH:mm:SS.fff\" | \n error: {error}')

  
    # stop_date = str()
    # destination_metadata_stop_date = execution.destination.destination_metadata[7]
    
    # if destination_metadata_stop_date == "YYYY-MM-DD HH:mm:SS.fff":
    #   today = datetime.now()
    #   unix_today = int(datetime(today.year, today.month, today.day, 23, 59, 59).timestamp())
    #   unix_one_day = 86400
    #   stop_date = int((unix_today - unix_one_day) * 1000000)

    # elif destination_metadata_stop_date != "YYYY-MM-DD HH:mm:SS.fff":
    #   try:
    #     stop_date = str_to_timestamp_micros(destination_metadata_stop_date)
      
    #   except Exception as error:
    #       raise ValueError(f'Invalid format date of stop_date. Received: {destination_metadata_stop_date}. Expected: \"YYYY-MM-DD HH:mm:SS.fff\" | \n error: {error}')

      #TO DO
    measurement_id = None
    #if len(execution.destination.destination_metadata) >= 9:
    #   measurement_id = execution.destination.destination_metadata[8]
    
    if not api_secret:
          raise ValueError(
            'GA4 MP should be called with a non-null api_secret'
          )
    if not self._exactly_one_of(firebase_app_id, measurement_id):
          raise ValueError(
            'GA4 MP should be called either with a firebase_app_id (for apps) or a measurement_id (for web)')      

    if not self._exactly_one_of(is_event, is_user_property):
          raise ValueError(
            'GA4 MP should be called either for sending events or a user properties')        
    
    accepted_elements = []
    status_code_elements = []

    logging.getLogger('megalista.GoogleAnalytics4MeasurementProtocolUploader').info(f"[PETLOVE] Returning data to make the request")  
    
    for row in batch.elements:
      #timestamp_micros = row.get('timestamp_micros')


      # Petlove
      # logging.getLogger('megalista.GoogleAnalytics4MeasurementProtocolUploader').info(f'[PETLOVE] timestamp_micros: {timestamp_micros}, start_date: {start_date}, stop_date: {stop_date}')

      # logging.getLogger('megalista.GoogleAnalytics4MeasurementProtocolUploader').info(
      #   f'[PETLOVE] start_date: {start_date} timestamp_micros: {timestamp_micros} stop_date: {stop_date}')  

      # Petlove
      #if start_date <= timestamp_micros <= stop_date:
      # if 1==1:
        
      app_instance_id = row.get('app_instance_id')
      client_id = row.get('client_id')
      user_id = row.get('user_id')
      timestamp_micros = row.get('timestamp_micros')
        

      payload: Dict[str, Any] = {
        'nonPersonalizedAds': non_personalized_ads
      }

      if not self._exactly_one_of(app_instance_id, client_id):
        raise ValueError(
          'GA4 MP should be called either with an app_instance_id (for apps) or a client_id (for web)')
      
      if is_event:
        event_reserved_keys = self.reserved_keys + ['name']
        #params = {k: v for k, v in row.items() if self._validate_param(k, v, event_reserved_keys)}
        #payload['events'] = [{'name': row['name'], 'params': params}]
        
        # params = {k: v for k, v in row.items() if self._validate_param(k, v, event_reserved_keys)}
        # payload['events'] = [{'name': row['name'], 'params': params}]
          
        # Petlove
        event_params = {}
        for k, v in row.items():
          # logging.getLogger('megalista.GoogleAnalytics4MeasurementProtocolUploader'
          #                   ).info(f'[PETLOVE] k: {k} - v: {v}')
          if self._validate_param(k, v, event_reserved_keys) and "event_" in k:
            event_params.update({
                k.replace("event_", ""): v
            })
        
        # teste estava com um tab pra frente 
        event_params.update({'currency': 'BRL'})

        # logging.getLogger('megalista.GoogleAnalytics4MeasurementProtocolUploader'
        #                     ).info(f'[PETLOVE] event_params: {event_params}')
          
        # payload["events"] = {"name": row["name"], "params": event_params}
        payload["events"] = {"name": conversion_name, "params": event_params}
          
        user_property_params = {
            k.replace("user_property_", ""): {"value": v}
            for k, v in row.items()
            if self._validate_param(k, v, self.reserved_keys)
            and "user_property_" in k and len(str(v)) <= 36
        }
        payload["userProperties"] = user_property_params

      if is_user_property: 
        payload['userProperties'] = {k: {'value': v} for k, v in row.items() if self._validate_param(k, v, self.reserved_keys)}
        # Petlove
        #payload['events'] = {'name': 'user_property_addition_event', 'params': {}}
        
        payload['events'] = {'name': 'user_property_addition_event', 'params': {'currency': 'BRL'}}

      url_container = [f'{self.API_URL}?api_secret={api_secret}']
        
      # Petlove
      url_debug_container = [f'{self.API_DEBUG_URL}?api_secret={api_secret}']

      if firebase_app_id:
        url_container.append(f'&firebase_app_id={firebase_app_id}')
          
        # Petlove
        url_debug_container.append(f'&firebase_app_id={firebase_app_id}')
        if not app_instance_id:
          raise ValueError(
            'GA4 MP needs an app_instance_id parameter when used for an App Stream.')
        payload['app_instance_id'] = app_instance_id
          
      measurement_id = None
      if measurement_id:
        url_container.append(f'&measurement_id={measurement_id}')
        # Petlove
        url_debug_container.append(f'&measurement_id={measurement_id}')
        if not client_id:
          raise ValueError(
            'GA4 MP needs a client_id parameter when used for a Web Stream.')
        payload['client_id'] = client_id
      # else:
      #   logging.getLogger('megalista.GoogleAnalytics4MeasurementProtocolUploader').info(f"[PETLOVE] measurement_id not in use")

      if user_id:
        payload['user_id'] = user_id

      if timestamp_micros:
        payload['timestamp_micros'] = int(str(timestamp_micros))
      url = ''.join(url_container)
        
      #Petlove
      logging.getLogger('megalista.GoogleAnalytics4MeasurementProtocolUploader').info(
        f'[PETLOVE] Payload created:\n {json.dumps(payload)}')
        
      #debug_response = requests.post(''.join(url_debug_container),data=json.dumps(payload))

      # logging.getLogger('megalista.GoogleAnalytics4MeasurementProtocolUploader').info(f"[PETLOVE] url_debug_container: {url_debug_container}")
        


      # for k, v in debug_response["validationMessages"][0].items():
      #   print(k, v)
      # logging.getLogger('megalista.GoogleAnalytics4MeasurementProtocolUploader').info(f"[PETLOVE] debug payload: {debug_response}")
      
        
      response = requests.post(url,data=json.dumps(payload))
        
      # logging.getLogger('megalista.GoogleAnalytics4MeasurementProtocolUploader').info(f"[PETLOVE] response: {response}")
        
      # logging.getLogger('megalista.GoogleAnalytics4MeasurementProtocolUploader').info(f"[PETLOVE] response.status_code: {response.status_code}")
        
      if response.status_code != 204:
        error_message = f'Error calling GA4 MP {response.status_code}: {str(response.content)}'
        logging.getLogger('megalista.GoogleAnalytics4MeasurementProtocolUploader').error(error_message)
        self._add_error(execution, error_message)
        
      else:
        #logging.getLogger('megalista.GoogleAnalytics4MeasurementProtocolUploader').info(f"[PETLOVE] response.status_code: {response.status_code}")
        #logging.getLogger('megalista.GoogleAnalytics4MeasurementProtocolUploader').info(f"[PETLOVE] response.status_code TYPE: {type(response.status_code)}")

        
        #logging.getLogger('megalista.GoogleAnalytics4MeasurementProtocolUploader').info(f"[PETLOVE] response.content: {response}")
        #logging.getLogger('megalista.GoogleAnalytics4MeasurementProtocolUploader').info(f"[PETLOVE] response.content TYPE: {type(response.content)}")

          # Petlove
          # logging.getLogger('megalista.GoogleAnalytics4MeasurementProtocolUploader').info(f"[PETLOVE] status code: {response.status_code}")
          # logging.getLogger('megalista.GoogleAnalytics4MeasurementProtocolUploader').info(f"[PETLOVE] response: {response}")
          
        accepted_elements.append(row)
        status_code_elements.append(response.status_code)
    
    logging.getLogger('megalista.GoogleAnalytics4MeasurementProtocolUploader').info(f"[PETLOVE] response.status_code: {status_code_elements}")
    logging.getLogger('megalista.GoogleAnalytics4MeasurementProtocolUploader').info(
      f'Successfully uploaded {len(accepted_elements)}/{len(batch.elements)} events.')
    
    return [Batch(execution, accepted_elements)]
