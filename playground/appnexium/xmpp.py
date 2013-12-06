#
# A simple XMPP library for AppNexus.
#
# Author: Adam Donahue
#

import ssl
import sys
import getpass
import logging

from sleekxmpp import ClientXMPP
from sleekxmpp.exceptions import IqError, IqTimeout

class AppnexiumXMPPClient(ClientXMPP):

    def __HANDLERS(self):
        return {
            "session_start":     self.session_start,
            "changed_status":    self.changed_status,
            "message":           self.message,
            "groupchat_message": self.groupchat_message
            }

    def __init__(self, jid, password):
        ClientXMPP.__init__(self, jid, password)

        # OpenFire requires SSLv23.
        #
        self.ssl_version = ssl.PROTOCOL_SSLv23

        for n,f in self.__HANDLERS().items():
            self.add_event_handler(n, f)

        self.register_plugin('xep_0045')

    def groupchat_message(self, *args, **kwargs):
        logging.debug("groupchat_message")

    def changed_status(self, *args, **kwargs):
        logging.debug("changed_status")

    def sent_presence(self, *args, **kwargs):
        logging.debug("sent_presence")

    def session_start(self, event):
        self.send_presence()    # TODO: Flesh out
        self.get_roster()       # TODO: Flesh out

        # TODO: Remove this testing code.
        self.plugin['xep_0045'].joinMUC('devops@conference.appnexus.com', 'adonahue@appnexus.com', wait=False)

    def message(self, message):
        print 'message received?'
        logging.info("message:", message)

    def presence(self, *args, **kwargs):
        pass

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG, format='%(levelname)-8s %(message)s')

    username = getpass.getuser()
    password = getpass.getpass()
    xmppClient = AppnexiumXMPPClient('%s@appnexus.com' % username, password)

    if xmppClient.connect():
        processRet = xmppClient.process(block=True)
    else:
        raise RuntimeError("Could not connect to XMPP server.")

