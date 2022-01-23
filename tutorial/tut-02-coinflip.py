from uc.utils import readChan, fork, collectOutputs
import gevent

from uc.apps.coinflip import F_Flip, Flip_Prot, Sim_Flip
from uc.apps.commitment import F_Com_Channel
from uc.adversary import DummyAdversary
from uc import execUC
from uc.protocol import protocolWrapper, DummyParty

"""""
The following are example environments for F_CoinFlip.
"""""
def env(k, static, z2p, z2f, z2a, a2z, f2z, p2z, pump):
    sid = ('one', "1, 2")
    static.write( (('sid',sid), ('crupt',)))

    transcript = []
    def _a2z():
        while True:
            m = readChan(a2z)
            transcript.append('a2z: ' + str(m))
            print('a2z: ' + str(m))

            # The benign environment has the adv respond to askflip
            if m == ('F2A', ('askflip', 1)):
                z2a.write( ('A2F', ('yes',)) )
            else:
                pump.write('dump')

    def _p2z():
        while True:
            m = readChan(p2z)
            transcript.append('p2z: ' + str(m))
            print('p2z: ' + str(m))
            pump.write('dump')

    g1 = fork(_a2z)
    g2 = fork(_p2z)

    z2p.write( (1, ('flip',)) )
    readChan(pump)

    z2p.write( (1, ('getflip',)) )
    readChan(pump)

    z2p.write( (2, ('getflip',)) )
    readChan(pump)

    gevent.kill(g1)
    gevent.kill(g2)

    return transcript

def env_flipper_crupt(k, static, z2p, z2f, z2a, a2z, f2z, p2z, pump):
    sid = ('one', "1, 2")
    static.write( (('sid',sid), ('crupt', 1)))

    transcript = []
    def _a2z():
        while True:
            m = readChan(a2z)
            transcript.append('a2z: ' + str(m))
            print('a2z: ' + str(m))
            pump.write('dump')

    def _p2z():
        while True:
            m = readChan(p2z)
            transcript.append('p2z: ' + str(m))
            print('p2z: ' + str(m))
            pump.write('dump')

    g1 = fork(_a2z)
    g2 = fork(_p2z)

    z2a.write( ('A2P', (1, ('commit', 1))) )
    readChan(pump)

    z2p.write( (2, ('getflip',)) )
    readChan(pump)
    
    z2a.write( ('A2P', (1, ('sendmsg', ('yoyoyoy',)))) )
    readChan(pump)

    z2p.write( (2, ('sendmsg', ('titititititit',))) )
    readChan(pump)

    z2p.write( (2, ('getflip',)) )
    readChan(pump)

    z2a.write( ('A2P', (1, ('reveal',))) )
    readChan(pump)

    z2p.write( (2, ('getflip',)) )
    readChan(pump)

    gevent.kill(g1)
    gevent.kill(g2)

    return transcript

def env_flipper_crupt_no_open(k, static, z2p, z2f, z2a, a2z, f2z, p2z, pump):
    sid = ('one', "1, 2")
    static.write( (('sid',sid), ('crupt', 1)))

    transcript = []
    def _a2z():
        while True:
            m = readChan(a2z)
            transcript.append('a2z: ' + str(m))
            print('a2z: ' + str(m))
            pump.write('dump')

    def _p2z():
        while True:
            m = readChan(p2z)
            transcript.append('p2z: ' + str(m))
            print('p2z: ' + str(m))
            pump.write('dump')

    g1 = fork(_a2z)
    g2 = fork(_p2z)

    z2a.write( ('A2P', (1, ('commit', 1))) )
    readChan(pump)

    z2p.write( (2, ('getflip',)) )
    readChan(pump)
    
    z2a.write( ('A2P', (1, ('sendmsg', ('yoyoyoy',)))) )
    readChan(pump)

    z2p.write( (2, ('sendmsg', ('titititititit',))) )
    readChan(pump)

    z2p.write( (2, ('getflip',)) )
    readChan(pump)

    #z2a.write( ('A2P', (1, ('reveal',))) )
    #readChan(pump)

    z2p.write( (2, ('getflip',)) )
    readChan(pump)

    gevent.kill(g1)
    gevent.kill(g2)

    return transcript

def env_receiver_crupt(k, static, z2p, z2f, z2a, a2z, f2z, p2z, pump):
    sid = ('one', "1, 2")
    static.write( (('sid',sid), ('crupt', 2)))

    transcript = []
    def _a2z():
        while True:
            m = readChan(a2z)
            transcript.append('a2z: ' + str(m))
            pump.write('dump')

    def _p2z():
        while True:
            m = readChan(p2z)
            transcript.append('p2z: ' + str(m))
            print('p2z: ' + str(m))
            pump.write('dump')

    g1 = fork(_a2z)
    g2 = fork(_p2z)

    z2a.write( ('A2P', (2, ('sendmsg', ('is this a real message',)))) )
    readChan(pump)

    z2p.write( (1, ('flip',)) )
    readChan(pump)

    z2p.write( (1, ('sendmsg', ('yea this is the honest message',))) )
    readChan(pump)

    z2a.write( ('A2P', (2, ('sendmsg', ('notbit', 1)))) )
    readChan(pump)

    z2p.write( (1, ('getflip',)) )
    readChan(pump)

    z2a.write( ('A2P', (2, ('sendmsg', ('bit', 1)))) )
    readChan(pump)

    z2p.write( (1, ('getflip',)) )
    readChan(pump)

    gevent.kill(g1)
    gevent.kill(g2)

    return transcript


##########################
# Run each of the examples
##########################

print('\n benign \n')
benign = execUC(120, env, F_Flip, DummyParty, DummyAdversary)

print('\n real \n')
treal = execUC(
    128,
    env_flipper_crupt_no_open,
    F_Com_Channel,
    Flip_Prot,
    DummyAdversary
)

print('\n ideal \n')
tideal = execUC(
    128,
    env_flipper_crupt_no_open,
    F_Flip,
    DummyParty,
    Sim_Flip
)
