from uc.itm import ITM, UCAdversary

class Sim_Com(UCAdversary):
    def __init__(self, k, bits, crupt, sid, pid, channels, pump):
        print('Sim com sid:', sid)
        self.ssid = sid[0]
        self.committer = sid[1]
        self.receiver = sid[2]

        UCAdversary.__init__(self, k, bits, crupt, sid, pid, channels, pump)

        self.table = {}
        self.revtable = {}
        self.receiver_random = None
        self.receiver_state = 1
        self.committed_bit = None
        self.dont_open = False

        self.a2f_msgs['hash'] = self.env_hash
        if self.is_dishonest(self.sid, self.receiver):
            self.party_msgs['commit'] = self.recv_commit
            self.party_msgs['open'] = self.recv_open
            self.party_msgs['recvmsg'] = self.recvmsg
        elif self.is_dishonest(self.sid, self.committer):
            self.a2p_msgs['sendmsg'] = self.commit_send

    def hash(self, s):
        if s not in self.table:
            self.table[s] = self.sample(self.k)
            self.revtable[self.table[s]] = s
        return self.table[s]

    def env_hash(self, s):
        self.write( ch='a2z', msg=('F2A', (self.sid,self.hash(s))) )

    def commit_send(self, to, msg):
        receiver, msg = msg
        b = self.sample(1)
        if msg[0] == 'commit' and to == (self.sid, self.committer):
            if msg[1] in self.revtable:
                try:
                    n,b = self.revtable[msg[1]]
                except:
                    self.dont_open = True
            else: self.dont_open = True
            self.write( ch='a2p', msg=(to, ('commit', b)) )
            self.committed_bit = b
            self.a2p_msgs['sendmsg'] = self.open_send
        else: 
            self.write( ch='a2p', msg=(to, ('sendmsg', receiver, msg)) )

    def open_send(self, to, msg):
        receiver, msg = msg
        if msg[0] == 'open' and to == (self.sid, self.committer) and not self.dont_open:
            try: 
                rec, (nonce, bit) = msg
                assert bit == self.committed_bit
                self.write( ch='a2p', msg=(to, ('reveal',)) )
            except: 
                self.dont_open = True
                self.pump.write('')
        else:
            self.write( ch='a2p', msg=(to, ('sendmsg', receiver, msg)) )

    def recvmsg(self, sender, msgsender, msg):
        self.write( ch='a2z', msg=('P2A', (sender, ('recvmsg', (msgsender, msg)))) )

    def recv_commit(self, sender):
        if sender == (self.sid, self.receiver) and self.receiver_state is 1:
            self.receiver_random = self.sample(self.k)
            self.write( ch='a2z', msg=('P2A', (sender, ('recvmsg', ((self.sid, self.committer), self.receiver_random)))) )
            self.receiver_state = 2
        else: self.pump.write('')


    def recv_open(self, sender, bit):
        if sender == (self.sid, self.receiver) and self.receiver_state is 2:
            self.write( ch='a2z', msg=('P2A', (sender, ('recvmsg', ((self.sid, self.committer), (self.sample(self.k), bit))))) )
            self.receiver_state = 3
        else: self.pump.write('')
