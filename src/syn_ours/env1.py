from itm import ProtocolWrapper, WrappedProtocolWrapper, WrappedPartyWrapper, wrappedPartyWrapper, wrappedProtocolWrapper
from adversary import DummyWrappedAdversary
from syn_ours import Syn_FWrapper, Syn_Channel, Syn_Bracha_Protocol
from syn_ours.f_bracha import RBC_Simulator, Syn_Bracha_Functionality, brachaSimulator
#from execuc import execWrappedUC
from execuc import execWrappedUC
from utils import z_get_leaks, waits
import logging
import gevent
from numpy.polynomial.polynomial import Polynomial

log = logging.getLogger(__name__)
logging.basicConfig( level=50 )

def env1(static, z2p, z2f, z2a, z2w, a2z, p2z, f2z, w2z, pump):
    delta = 3
    n = 3
    #sid = ('one', (1,2,3), delta)
    sid = ('one', tuple(range(1,n+1)), delta)
    static.write( (('sid', sid), ('crupt',)) )

    transcript = []
    def _a2z():
        while True:
            m = waits(a2z)
            transcript.append('a2z: ' + str(m.msg))
            pump.write('dump')

    def _p2z():
        while True:
            m = waits(p2z)
            transcript.append('p2z: ' + str(m.msg))
            pump.write('dump')

    g1 = gevent.spawn(_a2z)
    g2 = gevent.spawn(_p2z)

    def t(s):
        transcript.append('cmd: ' + str(s))

    z2p.write( ((sid,1), ('input', 2)))
    #wait_for(p2z)
    #waits(pump, a2z, p2z)
    waits(pump)

    def channel_id(fro, to, r):
        s = ('one', (sid,fro), (sid,to), r, delta)
        return (s,'F_chan')

    z2a.write( ('A2W', ('get-leaks',)) )
    #msgs = waits(pump, a2z, p2z)
    #log.debug('\033[91m [Leaks] \033[0m {}'.format( '\n'.join(str(m) for m in msgs.msg)))
    waits(pump)

    #log.debug('\033[91m send first VAL, get +2 ECHO messages \033[0m')
    for _ in range(4):
        z2w.write( ('poll',) )
        waits(pump)
        #log.info(waits(pump, a2z, p2z))

    #log.debug('\033[91m +2 ECHO + 1 = 3 polls to send next VAL message +2 ECHO msgs \033[0m')
    for _ in range(3):
        z2w.write( ('poll',) )
        #log.info(waits(pump, a2z, p2z))
        waits(pump)

    #log.debug('\033[91m +2 ECHO + 1 = 3 polls to send last VAL message +2 ECHO msgs \033[0m')
    for _ in range(3):
        z2w.write( ('poll',) )
        #log.info(waits(pump, a2z, p2z))
        waits(pump)

    #log.debug('\033[91m +2 ECHO +1 = 3 polls to send 1 -> 2 ECHO msg, +2 READY msgs \033[0m')
    for _ in range(3):
        z2w.write( ('poll',) )
        #log.info(waits(pump, a2z, p2z))
        waits(pump)

    #log.debug('\033[91m +2 READY +1 = 3 polls to send 1 -> 3 ECHO msg, +2 READY msgs \033[0m')
    for _ in range(3):
        z2w.write( ('poll',) )
        #log.info(waits(pump, a2z, p2z))
        waits(pump)

#    log.debug('\033[91m +2 READY +1 = 3 polls to send 2 -> 1 ECHO msg, +2 READY msgs \033[0m')
    for _ in range(3):
        z2w.write( ('poll',) )
        #log.info(waits(pump, a2z, p2z))
        waits(pump)

#    log.debug('\033[91m +2 READY +1 = 3 polls to send 2 -> 3 ECHO msg, +0 READY msgs \033[0m')
    for _ in range(3):
        z2w.write( ('poll',) )
        #log.info(waits(pump, a2z, p2z))
        waits(pump)

#    log.debug('\033[91m DELAYING \033[0m')
    z2a.write( ('A2W', ('delay', 3)) )
    #log.info(waits(pump, a2z))
    waits(pump)

#    log.debug('\033[91m +0 READY +1 = 3 polls to send 3 -> 1 ECHO msg, +0 msgs \033[0m')
    for _ in range(4):
        z2w.write( ('poll',) )
        #log.info(waits(pump, a2z, p2z))
        waits(pump)

#    log.debug('\033[91m +0 READY +1 = 3 polls to send 3 -> 2 ECHO msg, +0 msgs \033[0m')
    z2w.write( ('poll',) )
    #log.info(waits(pump, a2z, p2z))
    waits(pump)

#    log.debug('\033[91m +0 READY +1 = 3 polls to send 2 -> 1 READY msg, +0 msgs \033[0m')
    z2w.write( ('poll',) )
    #log.info(waits(pump, a2z, p2z))
    waits(pump)

#    log.debug('\033[91m +0 READY +1 = 3 polls to send 2 -> 3 READY msg, +0 msgs \033[0m')
    z2w.write( ('poll',) )
    #log.info(waits(pump, a2z, p2z))
    waits(pump)

#    log.debug('\033[91m +0 READY +1 = 3 polls to send 3 -> 1 READY msg, 1 ACCEPTS\033[0m')
    z2w.write( ('poll',) )
    #log.info('\033[1mp1 output\033[0m {}'.format(waits(pump, a2z, p2z)))
    waits(pump)

#    log.debug('\033[91m +0 READY +1 = 3 polls to send 3 -> 2 READY msg, 2 Doesnt accept \033[0m')
    z2w.write( ('poll',) )
    #log.info(waits(pump, a2z, p2z))
    waits(pump)

#    log.debug('\033[91m +0 READY +1 = 3 polls to send 1 -> 2 READY msg, 2 ACCEPTS\033[0m')
    z2w.write( ('poll',) )
    #log.info('\033[1mp2 output\033[0m {}'.format( waits(pump, a2z, p2z)))
    waits(pump)

#    log.debug('\033[91m +0 READY +1 = 3 polls to send 1 -> 3 READY msg, 3 ACCEPTS\033[0m')
    z2w.write( ('poll',) )
    #log.info('\033[1mp3 output\033[0m {}'.format(waits(pump, a2z, p2z)))
    waits(pump)

    gevent.kill(g1)
    gevent.kill(g2)

    print('Transcript', transcript)
    return transcript


def env3(static, z2p, z2f, z2a, z2w, a2z, p2z, f2z, w2z, pump):
    delta = 3
    n = 3
    #sid = ('one', (1,2,3), delta)
    sid = ('one', tuple(range(1,n+1)), delta)
    #static.write( (('sid', sid), ('crupt',)) )
    static.write( (('sid', sid), ('crupt',(sid,2))) )

    z2p.write( ((sid,1), ('input', 2)), n*(4*n + 1) )
    #wait_for(p2z)
    waits(pump, a2z, p2z)

    def channel_id(fro, to, r):
        s = ('one', (sid,fro), (sid,to), r, delta)
        return (s,'F_chan')

    z2a.write( ('A2W', ('get-leaks',)) )
    msgs = waits(pump, a2z, p2z)
    log.info('\033[91m [Leaks] \033[0m {}'.format('\n'.join(str(m) for m in msgs.msg)))

    log.debug('\033[91m send first VAL, get +2 ECHO messages \033[0m')
    for _ in range(4):
        z2w.write( ('poll',) )
        log.info(waits(pump, a2z, p2z))

    log.debug('\033[91m +2 ECHO + 1 = 3 polls to send next VAL message +2 ECHO msgs \033[0m')
    for _ in range(4):
        z2w.write( ('poll',) )
        log.info(waits(pump, a2z, p2z))
    log.debug('*****')
    
    z2a.write( ('A2P', ((sid,2), ('P2F', ((channel_id(2,1,1)), ('send', ('ECHO', 2)))))) )
    log.debug('crupt output: {}'.format( waits(pump, a2z)))

    z2a.write( ('A2P', ((sid,2), ('P2F', ((channel_id(2,3,1)), ('send', ('ECHO', 2)))))) )
    log.debug('crupt output: {}'.format(waits(pump, a2z)))

    log.debug('\033[91m +2 ECHO + 1 = 3 polls to send last VAL message +2 ECHO msgs \033[0m')
    for _ in range(3):
        z2w.write( ('poll',) )
        log.info(waits(pump, a2z, p2z))

    log.debug('\033[91m +2 ECHO +1 = 3 polls to send 1 -> 2 ECHO msg, +2 READY msgs \033[0m')
    for _ in range(3):
        z2w.write( ('poll',) )
        log.info(waits(pump, a2z, p2z))

    z2a.write( ('A2P', ((sid,2), ('P2F', ((channel_id(2,1,1)), ('send', ('READY', 2)))))) )
    log.info('crupt output: {}'.format(waits(pump, a2z)))

    z2a.write( ('A2P', ((sid,2), ('P2F', ((channel_id(2,3,1)), ('send', ('READY', 2)))))) )
    log.info('crupt output: {}'.format(waits(pump, a2z)))
    
    z2a.write( ('A2P', ((sid,2), ('P2W', ('clock-round',)))) )
    log.info('clock round: {}'.format(waits(pump, a2z)))

    log.debug('\033[91m +2 READY +1 = 3 polls to send 1 -> 3 ECHO msg, +2 READY msgs \033[0m')
    for _ in range(3):
        z2w.write( ('poll',) )
        log.info(waits(pump, a2z, p2z))

    log.debug('\033[91m +2 READY +1 = 3 polls to send 2 -> 1 ECHO msg, +2 READY msgs \033[0m')
    for _ in range(3):
        z2w.write( ('poll',) )
        log.info(waits(pump, a2z, p2z))

    log.debug('\033[91m +2 READY +1 = 3 polls to send 2 -> 3 ECHO msg, +0 READY msgs \033[0m')
    for _ in range(3):
        z2w.write( ('poll',) )
        log.info(waits(pump, a2z, p2z))

    log.debug('\033[91m +0 READY +1 = 3 polls to send 3 -> 1 ECHO msg, +0 msgs \033[0m')
    z2w.write( ('poll',) )
    log.info(waits(pump, a2z, p2z))

    log.debug('\033[91m +0 READY +1 = 3 polls to send 3 -> 2 ECHO msg, +0 msgs \033[0m')
    z2w.write( ('poll',) )
    log.info(waits(pump, a2z, p2z))

    z2a.write( ('A2W', ('get-leaks',)) )
    msgs = waits(pump, a2z, p2z)
    log.info('\033[91m [Leaks] \033[0m {}'.format('\n'.join(str(m) for m in msgs.msg)))

    log.debug('\033[91m +0 READY +1 = 3 polls to send 2 -> 1 READY msg, +0 msgs \033[0m')
    z2w.write( ('poll',) )
    log.info(waits(pump, a2z, p2z))

    log.debug('\033[91m +0 READY +1 = 3 polls to send 2 -> 3 READY msg, +0 msgs \033[0m')
    z2w.write( ('poll',) )
    log.info(waits(pump, a2z, p2z))

    log.debug('\033[91m +0 READY +1 = 3 polls to send 3 -> 1 READY msg, 1 ACCEPTS\033[0m')
    z2w.write( ('poll',) )
    log.info(waits(pump, a2z, p2z))
    
    z2a.write( ('A2W', ('get-leaks',)) )
    msgs = waits(pump, a2z, p2z)
    log.info('\033[91m [Leaks] \033[0m {}'.format('\n'.join(str(m) for m in msgs.msg)))

    log.debug('\033[91m +0 READY +1 = 3 polls to send 3 -> 2 READY msg, 2 Doesnt accept \033[0m')
    z2w.write( ('poll',) )
    log.info(waits(pump, a2z, p2z))

    log.debug('\033[91m +0 READY +1 = 3 polls to send 1 -> 2 READY msg, 2 ACCEPTS\033[0m')
    z2w.write( ('poll',) )
    log.info(waits(pump, a2z, p2z))

    log.debug('\033[91m +0 READY +1 = 3 polls to send 1 -> 3 READY msg, 3 ACCEPTS\033[0m')
    z2w.write( ('poll',) )
    log.info(waits(pump, a2z, p2z))

def env2(static, z2p, z2f, z2a, z2w, a2z, p2z, f2z, w2z, pump):
    delta = 3
    n = 4
    #sid = ('one', (1,2,3), delta)
    sid = ('one', tuple(range(1,n+1)), delta)
    static.write( (('sid', sid), ('crupt',(sid,1))) )

#    z2p.write( ((sid,1), ('input', 2)), n*(4*n + 1) )
#    #wait_for(p2z)
#    waits(pump, a2z, p2z)

    transcript = []
    def _a2z():
        while True:
            m = waits(a2z)
            transcript.append('a2z:{}'.format(m.msg))
            pump.write('dump')

    def _p2z():
        while True:
            m = waits(p2z)
            transcript.append('p2z:{}'.format(m.msg))
            pump.write('dump')

    g1 = gevent.spawn(_a2z)
    g2 = gevent.spawn(_p2z)

    def channel_id(fro, to, r):
        s = ('one', (sid,fro), (sid,to), r, delta)
        return (s,'F_chan')

    z2a.write( ('A2P', ((sid,1), ('P2F', ((channel_id(1,2,1)), ('send', ('VAL', 3)))))))
    #waits(pump, a2z)
    waits(pump)

    z2a.write( ('A2P', ((sid,1), ('P2F', ((channel_id(1,4,1)), ('send', ('VAL', 3)))))))
    #waits(pump, a2z)
    waits(pump)
    
    z2a.write( ('A2P', ((sid,1), ('P2F', ((channel_id(1,3,1)), ('send', ('VAL', 3)))))))
    #waits(pump, a2z)
    waits(pump)

    z2a.write( ('A2W', ('get-leaks',)) )
    #msgs = waits(pump, a2z, p2z)
    #log.debug('\033[91m [Leaks] \033[0m {}'.format( '\n'.join(str(m) for m in msgs.msg)))
    waits(pump)

    # execute one of the VALs
    z2a.write( ('A2W', ('exec', 4, 1)))
    #waits(pump, a2z, p2z)
    waits(pump)

    # excute a VAL
    z2a.write( ('A2W', ('exec', 4, 0)))
    #waits(pump, a2z, p2z)
    waits(pump)

    # force execute the first ECHO
    for _ in range(10):
        z2w.write( ('poll',) )
        #waits(pump, a2z, p2z)
        waits(pump)

    for _ in range(1):
        # execute ECHO messages from 2->1, 2->3, 2->4
        z2a.write( ('A2W', ('exec', 4, 0)))
        #waits(pump, a2z, p2z)
        waits(pump)

#    for _ in range(4):
#        z2w.write( ('poll',) )
#        #waits(pump, a2z, p2z)
#        waits(pump)
#        
#    for _ in range(2):
#        # execute ECHO messages from 2->1, 2->3, 2->4
#        z2a.write( ('A2W', ('exec', 4, 0)))
#        #waits(pump, a2z, p2z)
#        waits(pump)
#
#    for _ in range(9):
#        # execute ECHO messages from 2->1, 2->3, 2->4
#        z2a.write( ('A2W', ('exec', 7, 0)))
#        #print(waits(pump, a2z, p2z))
#        waits(pump)
#
#    for _ in range(1):
#        z2a.write( ('A2W', ('exec', 7, 0)))
#        #print(waits(pump, a2z, p2z))
#        waits(pump)
#
#    z2a.write( ('A2W', ('exec', 7, 0)))
#    #print('someoutput', waits(pump, a2z, p2z))
#    waits(pump)

    gevent.kill(g1)
    gevent.kill(g2)

    print('Transcript', transcript)
    return transcript

#    log.debug('\033[91m send first 1 -> 1 VAL, get +3 ECHO messages \033[0m')
#    for _ in range(5):
#        z2w.write( ('poll',) )
#        log.info(waits(pump, a2z, p2z))
#
#    log.debug('\033[91m +3 ECHO + 1 = 4 polls to send next 1 -> 2 VAL message +3 ECHO msgs \033[0m')
#    for _ in range(4):
#        z2w.write( ('poll',) )
#        log.info(waits(pump, a2z, p2z))
#
#    log.debug('\033[91m +3 ECHO + 1 = 4 polls to send last 1 -> 3 VAL message +3 ECHO msgs \033[0m')
#    for _ in range(4):
#        z2w.write( ('poll',) )
#        log.info(waits(pump, a2z, p2z))
#    
#    log.debug('\033[91m +3 ECHO + 1 = 3 polls to send last 1 -> 4 VAL message +3 ECHO msgs \033[0m')
#    for _ in range(4):
#        z2w.write( ('poll',) )
#        log.info(waits(pump, a2z, p2z))
#
#    log.debug('\033[91m +3 ECHO +1 = 4 polls to send 1 -> 2 ECHO msg, +0 READY msgs \033[0m')
#    for _ in range(4):
#        z2w.write( ('poll',) )
#        log.info(waits(pump, a2z, p2z))
#
#    log.debug('\033[91m +0 READY +1 = 1 polls to send 1 -> 3 ECHO msg, +0 READY msgs \033[0m')
#    for _ in range(1):
#        z2w.write( ('poll',) )
#        log.info(waits(pump, a2z, p2z))
#
#    log.debug('\033[91m +0 READY +1 = 1 polls to send 1 -> 4 ECHO msg, +0 READY msgs \033[0m')
#    for _ in range(1):
#        z2w.write( ('poll',) )
#        log.info(waits(pump, a2z, p2z))
#
#    log.debug('\033[91m +0 READY +1 = 1 polls to send 2 -> 1 ECHO msg, +0 READY msgs \033[0m')
#    for _ in range(1):
#        z2w.write( ('poll',) )
#        log.info(waits(pump, a2z, p2z))
#
#    log.debug('\033[91m +0 READY +1 = 1 polls to send 2 -> 3 ECHO msg, +3 READY msgs \033[0m')
#    for _ in range(1):
#        z2w.write( ('poll',) )
#        log.info(waits(pump, a2z, p2z))
#    
#    log.debug('\033[91m +3 READY +1 = 4 polls to send 2 -> 4 ECHO msg, +3 READY msgs \033[0m')
#    for _ in range(4):
#        z2w.write( ('poll',) )
#        log.info(waits(pump, a2z, p2z))
#    
###    log.debug('\033[91m DELAYING \033[0m')
###    z2a.write( ('A2W', ('delay', 3)) )
###    log.info(waits(pump, a2z))
###
#    log.debug('\033[91m +3 READY +1 = 4 polls to send 3 -> 1 ECHO msg, +3 READY msgs \033[0m')
#    for _ in range(4):
#        z2w.write( ('poll',) )
#        log.info(waits(pump, a2z, p2z))
#
#    log.debug('\033[91m +3 READY +1 = 4 polls to send 3 -> 2 ECHO msg, +3 READY msgs \033[0m')
#    for _ in range(4):
#        z2w.write( ('poll',) )
#        log.info(waits(pump, a2z, p2z))
#
#    log.debug('\033[91m +3 READY +1 = 4 polls to send 3 -> 4 ECHO msg, +0 READY msgs \033[0m')
#    for _ in range(4):
#        z2w.write( ('poll',) )
#        log.info(waits(pump, a2z, p2z))
#
#    log.debug('\033[91m +0 READY +1 = 1 polls to send 4 -> 1 ECHO msg, +0 msgs \033[0m')
#    z2w.write( ('poll',) )
#    log.info(waits(pump, a2z, p2z))
#    
#    log.debug('\033[91m +0 READY +1 = 1 polls to send 4 -> 2 ECHO msg, +0 msgs \033[0m')
#    z2w.write( ('poll',) )
#    log.info(waits(pump, a2z, p2z))
#    
#    log.debug('\033[91m +0 READY +1 = 1 polls to send 4 -> 3 ECHO msg, +0 msgs \033[0m')
#    z2w.write( ('poll',) )
#    log.info(waits(pump, a2z, p2z))
#    
#    log.debug('\033[91m +0 READY +1 = 3 polls to send 3 -> 1 READY msg, +0 msgs \033[0m')
#    z2w.write( ('poll',) )
#    log.info(waits(pump, a2z, p2z))
#
#    log.debug('\033[91m +0 READY +1 = 3 polls to send 3 -> 2 READY msg, +0 msgs \033[0m')
#    z2w.write( ('poll',) )
#    log.info(waits(pump, a2z, p2z))
#
#    log.debug('\033[91m +0 READY +1 = 3 polls to send 3 -> 4 READY msg, +0 msgs \033[0m')
#    z2w.write( ('poll',) )
#    log.info(waits(pump, a2z, p2z))
#
#    log.debug('\033[91m +0 READY +1 = 3 polls to send 4 -> 1 READY msg, +0 msgs \033[0m')
#    z2w.write( ('poll',) )
#    log.info(waits(pump, a2z, p2z))
#
#    log.debug('\033[91m +0 READY +1 = 3 polls to send 4 -> 2 READY msg, +0 msgs \033[0m')
#    z2w.write( ('poll',) )
#    log.info(waits(pump, a2z, p2z))
#
#    log.debug('\033[91m +0 READY +1 = 3 polls to send 4 -> 3 READY msg, +0 msgs \033[0m')
#    z2w.write( ('poll',) )
#    log.info(waits(pump, a2z, p2z))
#
#    log.debug('\033[91m +0 READY +1 = 3 polls to send 1 -> 2 READY msg, +0 msgs \033[0m')
#    z2w.write( ('poll',) )
#    log.info(waits(pump, a2z, p2z))
#
#    log.debug('\033[91m +0 READY +1 = 3 polls to send 1 -> 3 READY msg, +0 msgs \033[0m')
#    z2w.write( ('poll',) )
#    log.info(waits(pump, a2z, p2z))
#
#    log.debug('\033[91m +0 READY +1 = 3 polls to send 1 -> 4 READY msg, +0 msgs \033[0m')
#    z2w.write( ('poll',) )
#    log.info(waits(pump, a2z, p2z))
#
#    log.debug('\033[91m +0 READY +1 = 3 polls to send 2 -> 1 READY msg, +0 msgs \033[0m')
#    z2w.write( ('poll',) )
#    log.info(waits(pump, a2z, p2z))
#
#    log.debug('\033[91m +0 READY +1 = 3 polls to send 2 -> 3 READY msg, +0 msgs \033[0m')
#    z2w.write( ('poll',) )
#    log.info(waits(pump, a2z, p2z))
#
#    log.debug('\033[91m +0 READY +1 = 3 polls to send 2 -> 4 READY msg, +0 msgs \033[0m')
#    z2w.write( ('poll',) )
#    log.info(waits(pump, a2z, p2z))

def distinguisher(t_ideal, t_real):
    print('\n\t\033[93m Ideal transcript\033[0m')
    for i in t_ideal: print(i)

    print('\n\t\033[93m real transcript\033[0m')
    for i in t_real: print(i)

    if t_ideal == t_real:
        print("\033[92m[Distinguisher] They're the same\033[0m")
    else:
        print("\033[91m[Distinguisher] They're different\033[0m")

if __name__=='__main__':
    print('\n\t\t\033[93m [IDEAL WORLD] \033[0m\n')
    t1 = execWrappedUC(
        env2, 
        [('F_bracha',Syn_Bracha_Functionality)], 
        wrappedPartyWrapper('F_bracha'),
        Syn_FWrapper, 
        brachaSimulator(Syn_Bracha_Protocol),
        poly=Polynomial([100,2,3,4,5,6])
    )
    
    print('\n\t\t\033[93m [REAL WORLD] \033[0m\n')
    t2 = execWrappedUC(
        env2, 
        [('F_chan',Syn_Channel)], 
        wrappedProtocolWrapper(Syn_Bracha_Protocol),
        Syn_FWrapper, 
        DummyWrappedAdversary, 
        poly=Polynomial([100,2,3,4,5,6,7])
    )

    distinguisher(t1, t2)
