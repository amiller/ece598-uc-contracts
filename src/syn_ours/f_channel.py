import dump
from itm import UCWrappedFunctionality
from utils import wait_for

class Syn_Channel(UCWrappedFunctionality):
    def __init__(self, sid, pid, channels):
        self.ssid = sid[0]
        self.sender = sid[1]
        self.receiver = sid[2]
        self.delta = sid[3]
        UCWrappedFunctionality.__init__(self, sid, pid, channels)
        self.leakbuffer = None

    def leak(self, msg):
        print('leaking', msg, 'fro', self.sender, 'to', self.receiver)
        self.leakbuffer = msg

    def send_message(self, msg):
        self.f2p.write( (self.receiver, msg) )

    def party_send(self, sender, msg):
        if sender == self.sender:
            self.f2w.write( ('schedule', self.send_message, (msg,), self.delta) )
            assert wait_for(self.w2f).msg == ('OK',)
            self.leak( msg )
            self.f2p.write( (self.sender, 'OK') )
        else:
            dump.dump()

    def party_fetch(self, sender, msg):
        if sender == self.receiver and self.M:
            self.f2p.write( (self.receiver, ('sent', self.M)) )
        else:
            dump.dump()

    def party_msg(self, msg):
        sender,msg = msg
        if msg[0] == 'send':
            self.party_send(sender, msg)
        elif msg[0] == 'fetch':
            self.party_fetch(sender, msg)
        else:
            dump.dump()

    def adv_get_leaks(self):
        self.f2a.write( self.leakbuffer )
        self.leakbuffer = []

    def adv_msg(self, msg):
        if msg[0] == 'get-leaks':
            self.adv_get_leaks()
        else:
            dump.dump()
    def env_msg(self, msg):
        dump.dump()
    def wrapper_msg(self, msg):
        dump.dump()
