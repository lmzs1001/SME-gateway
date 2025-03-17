import urequests # type: ignore
import json
import ssl

class HTTPClient:
    def __init__(self, cert_path=None):
        """Init TLS Certificates"""
        self.context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT) if cert_path else None
        if cert_path:
            self.context.load_verify_locations(cert_path)

    def post(self, url, data, headers=None):
        """Send JSON request to server"""
        headers = headers or {"Content-Type": "application/json"}
        
        try:
            response = urequests.post(url, data=json.dumps(data), headers=headers, context=self.context)
            result = response.text
            response.close()
            return result
        except Exception as e:
            return f"Error in petition: {e}"