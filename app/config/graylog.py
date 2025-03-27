import logging
import os
import uuid

from dotenv import load_dotenv
from pygelf import GelfUdpHandler

load_dotenv()

class ContextFilter(logging.Filter):
    def filter(self, record):
        record.request_id = str(uuid.uuid4())
        return True

logger = logging.getLogger('navigo_logger')
logger.setLevel(logging.INFO)
graylog_host = os.getenv("GRAYLOG_HOST")
graylog_port_udp = os.getenv("GRAYLOG_PORT_UDP")
if graylog_host and graylog_port_udp:
    handler = GelfUdpHandler(host=graylog_host, port=int(graylog_port_udp), include_extra_fields=True)
    logger.addHandler(handler)
    logger.addFilter(ContextFilter())