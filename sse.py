import errno
import time

import adafruit_requests


class Response(adafruit_requests.Response):
    _timeout = None

    @property
    def timeout(self):
        return self._timeout

    @timeout.setter
    def timeout(self, value):
        self.socket.settimeout(value)
        self._timeout = value

    def _readto(self, stop: bytes) -> bytearray:
        to = self.timeout
        self.timeout = None
        try:
            return super()._readto(stop)
        finally:
            self.timeout = to


# adafruit_requests.Response = Response

# EventSource states
_CONNECT = 0  # Starting state, open immediately
_OPEN = 1  # Connection is open and data is flowing
_LOST = 2  # Connection lost, wait retry and then _CONNECT
_CLOSED = 3  # Connection was deliberately closed, do nothing.


class EventSource:
    # This is implemented as a state machine

    handler = None
    _resp = None
    _last_event_id = None
    _retry = 10
    _next_try: float
    _buffer: bytes  # FIXME: More efficient buffer

    def __init__(self, session, url, **opts):
        self._session = session
        self._url = url
        self._request_opts = opts
        self._state = _CONNECT

    def close(self):
        """
        Stop the SSE stream.
        """
        if self._resp is not None:
            self._resp.close()
            del self._resp
        self._state = _CLOSED

    def __del__(self):
        self.close()

    def loop(self):
        """
        Service the SSE connection
        """
        print(f"loop {self._state=}")
        if self._state == _CONNECT:
            headers = {
                'Accept': 'text/event-stream',
                'Cache-Control': 'no-cache',
            }
            if self._last_event_id is not None:
                headers['Last-Event-ID'] = self._last_event_id

            self._resp = self._session.get(self._url, headers=headers)
            if self._resp.status_code == 200:
                self._resp.timeout = 0
                self._state = _OPEN
                self._buffer = b""
                self._fields = []
            else:
                self._resp.close()
                del self._resp
                self._state = _LOST
                self._next_try = time.monotonic() + self._retry

        elif self._state == _OPEN:
            # I believe that iter_conent() will stop iterating when the buffer runs out.
            try:
                for chunk in self._resp.iter_content(256):
                    print(f"chunk {chunk=}")
                    self._buffer += chunk
                    while b'\n' in self._buffer:
                        line, _, self._buffer = self._buffer.partition(b'\n')
                        if not line:
                            # Since we consume whole lines, this means that we got a blank line
                            if self._fields:
                                self._got_event(self._fields)
                                self._fields = []
                        else:
                            self._fields.append(self._parse_line(line))
                    return  # Since adafruit_requests doesn't have a non-blocking mode
            except OSError as exc:
                if exc.errno == errno.EAGAIN:
                    print("EAGAIN")
                else:
                    raise

        elif self._state == _LOST:
            if time.monotonic() > self._next_try:
                self._state = _CONNECT
                del self._next_try

        elif self._state == _CLOSED:
            # Do nothing, forever
            pass

    @ staticmethod
    def _parse_line(line):
        field, _, value = line.decode('utf-8').partition(':')
        if value.startswith(' '):
            value = value[1:]
        return field, value

    def _got_event(self, fields):
        if not self.handler:
            return

        msg = {'event': 'message', 'data': ''}
        # https://html.spec.whatwg.org/multipage/server-sent-events.html#event-stream-interpretation
        real_event = False  # Only call the handler if we got something resembling an actual event
        for k, v in fields:
            if k == 'retry':
                try:
                    self._retry = int(v)
                except ValueError:
                    pass
            elif k == 'data':
                real_event = True
                if msg['data']:
                    msg['data'] += '\n' + v
                else:
                    msg['data'] = v
            elif not k:
                pass
            else:
                real_event = True
                if k == 'id':
                    self._last_event_id = v
                # Spec says we should ignore unknown fields. We're passing them on.
                msg[k] = v

        if real_event:
            self.handler(msg)
