import os
import requests
from typing import Optional, List, Dict, Any, Tuple

class Client:
    def __init__(self, base_url: Optional[str] = None):
        self.base_url = base_url or os.environ.get('SEQUIN_URL', 'http://localhost:7376')

    def _request(self, endpoint: str, method: str, body: Optional[Dict] = None) -> Tuple[Optional[Dict], Optional[Dict]]:
        try:
            url = f"{self.base_url}{endpoint}"
            headers = {
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            }
            response = requests.request(method, url, json=body, headers=headers)

            if not response.ok:
                error_data = response.json()
                return None, {'status': response.status_code, 'summary': error_data.get('summary', 'Unknown error')}

            data = response.json()
            return data.get('data', data), None
        except requests.RequestException as e:
            if 'Connection refused' in str(e):
                return None, {
                    'status': 500,
                    'summary': f"We can't reach Sequin on {self.base_url}. Double check that Sequin is running and confirm your Python client is configured properly"
                }
            return None, {'status': 500, 'summary': str(e)}

    def send_message(self, stream: str, key: str, data: Any) -> Tuple[Optional[Dict], Optional[Dict]]:
        return self.send_messages(stream, [{'key': key, 'data': data}])

    def send_messages(self, stream: str, messages: List[Dict]) -> Tuple[Optional[Dict], Optional[Dict]]:
        return self._request(f"/api/streams/{stream}/messages", 'POST', {'messages': messages})

    def receive_message(self, stream: str, consumer: str) -> Tuple[Optional[Dict], Optional[Dict]]:
        res, error = self.receive_messages(stream, consumer, {'batch_size': 1})
        if error:
            return None, error
        return (res[0], None) if res and len(res) > 0 else (None, None)

    def receive_messages(self, stream: str, consumer: str, options: Optional[Dict] = None) -> Tuple[Optional[List[Dict]], Optional[Dict]]:
        batch_size = options.get('batch_size', 10) if options else 10
        return self._request(f"/api/streams/{stream}/consumers/{consumer}/receive?batch_size={batch_size}", 'GET')

    def ack_messages(self, stream: str, consumer: str, ack_ids: List[str]) -> Tuple[Optional[Dict], Optional[Dict]]:
        return self._request(f"/api/streams/{stream}/consumers/{consumer}/ack", 'POST', {'ack_ids': ack_ids})

    def ack_message(self, stream: str, consumer: str, ack_id: str) -> Tuple[Optional[Dict], Optional[Dict]]:
        return self.ack_messages(stream, consumer, [ack_id])

    def nack_messages(self, stream: str, consumer: str, ack_ids: List[str]) -> Tuple[Optional[Dict], Optional[Dict]]:
        return self._request(f"/api/streams/{stream}/consumers/{consumer}/nack", 'POST', {'ack_ids': ack_ids})

    def nack_message(self, stream: str, consumer: str, ack_id: str) -> Tuple[Optional[Dict], Optional[Dict]]:
        return self.nack_messages(stream, consumer, [ack_id])

    def create_stream(self, stream_name: str, options: Optional[Dict] = None) -> Tuple[Optional[Dict], Optional[Dict]]:
        body = {'name': stream_name}
        if options:
            body.update(options)
        return self._request('/api/streams', 'POST', body)

    def delete_stream(self, stream_id_or_name: str) -> Tuple[Optional[Dict], Optional[Dict]]:
        return self._request(f"/api/streams/{stream_id_or_name}", 'DELETE')

    def create_consumer(self, stream_id_or_name: str, consumer_name: str, consumer_filter: str, options: Optional[Dict] = None) -> Tuple[Optional[Dict], Optional[Dict]]:
        body = {
            'name': consumer_name,
            'filter_key_pattern': consumer_filter,
            'kind': 'pull'
        }
        if options:
            body.update(options)
        return self._request(f"/api/streams/{stream_id_or_name}/consumers", 'POST', body)

    def delete_consumer(self, stream_id_or_name: str, consumer_id_or_name: str) -> Tuple[Optional[Dict], Optional[Dict]]:
        return self._request(f"/api/streams/{stream_id_or_name}/consumers/{consumer_id_or_name}", 'DELETE')