from ast import literal_eval
from uc import UCFunctionality
from uc.utils import read_one, read
import sys
import logging
from poly import F53, randomWithZero, polyFromCoeffs, eval_poly, random_degree
from collections import defaultdict

log = logging.getLogger(__name__)

opcodes = [
    'INPUT',
    'OPEN',
    'LIN',
    'CONST',
    'MULT',
    'RAND'
]

def do_abb_op(read_secret, store_fresh, inputs, op):
    op,args = op
    if op == 'MULT':
        x,y = args
        x = read_secret(x)
        y = read_secret(y)
        xy = store_fresh(x*y)
        return xy
    #elif op == 'LIN':
    elif op == 'OPEN':
        sh = args
        x = read_secret(sh)
        return polyFromCoeffs([x])
    elif op == 'INPUT':
        x = inputs[0]
        inputs = inputs[1:]
        k = store_fresh(x)
        return k
    else: return 0 

def do_mpc_op(has_mult, read_sharing, store_fresh, inputs, op, t, itm):
    print('\n Do MPC OP: {}\n'.format(op))
    op,args = op
    if op == 'MULT':
        x,y = args
        if has_mult:
            xphi = read_sharing(x)
            yphi = read_sharing(y)
            phi = randomWithZero(t, eval_poly(xphi, 0) * eval_poly(yphi, 0), itm)
            print('\n t',t)
            xy = store_fresh(phi)
            print('\n**** xy in MULT: {}, type: {}****\n'.format(xy, type(xy)))
            return xy
        else: raise Exception("no MULT")
    #elif op == 'LIN':
    elif op == 'OPEN':
        k = args
        phi = read_sharing(k)
        return phi
    elif op == 'CONST': 
        v = args
        phi = polyFromCoeffs([v])
        k = store_fresh(phi)
        return k
    elif op == 'RAND':
        a = random_degree(t, itm)
        b = random_degree(t, itm)
        ab = randomWithZero(t, (eval_poly(a,0) * eval_poly(b,0)), itm)
        ka = store_fresh(a)
        kb = store_fresh(b)
        kab = store_fresh(ab)
        return (ka, kb, kab)
    elif op == 'INPUT':
        x = inputs[0]
        inputs = inputs[1:]
        phi = randomWithZero(t, x, itm)
        k = store_fresh(phi)
        return k
    else:
        raise Exception("Not a real opcode: {}".format(op))



def FMPC_(has_mpc, has_mult):
    def _f(k, bits, crupt, sid, channels, pump):
        return fMPC_(k, bits, crupt, sid, channels, pump, has_mpc, has_mult)
    return _f

class fMPC_(UCFunctionality):
    def __init__(self, k, bits, crupt, sid, channels, pump, has_mpc, has_mult):
        UCFunctionality.__init__(self, k, bits, crupt, sid, channels, pump)
        self.ssid = sid[0]
        sid = literal_eval(sid[1])
        self.n = sid[0]
        self.input_party = sid[1]

        self.has_mpc = has_mpc
        self.has_mult = has_mult


        # log of operations and results
        self.ops = []

        # inputs provided by the input party
        self.inputs = []  # [Fq]

        # Maps share IDs to secrets
        # -- In MPC mode, these will be degree-t polys , in
        # -- ABB mode they will only be constant (degree-0)
        # self.share_table = {}
        self.share_table = defaultdict(lambda: None)

        # fresh handle
        self.freshCtr = 0

        # counters views by each of the parties
        self.initCtrs = [ (i,0) for i in range(self.n) ]
        self.counters = dict(self.initCtrs)

        self.party_msgs['log'] = self.party_log
        self.party_msgs['input'] = self.party_input
        self.party_msgs['op'] = self.party_op
        self.party_msgs['myshare'] = self.party_myshare

    def fresh(self):
        x = self.freshCtr
        self.freshCtr += 1
        return x

    def commit(self, op, outp):
        self.ops.append( (op, outp) )
        self.write( 'f2p', (self.input_party, ('OpOutput', outp)) )

    def party_op(self, sender, op):
        if sender == self.input_party and self.has_mpc:
            def _storeFresh(phi):
                sh = self.fresh()
                self.share_table[sh] = phi
                return sh
            def _readSharing(sh):
                return self.share_table[sh]
            result = do_mpc_op(self.has_mult, _readSharing, _storeFresh, self.inputs, op, 1, self)
            self.commit(op, result)
        elif self.has_mpc:
            # follow mode by honest parties
            c = self.counters[sender]
            _op,res = self.ops[c]
            if op == _op:
                self.counters[sender] += 1
                self.write('f2p', (sender, ('OpRes', res)))
            else:
                self.write('f2p', (sender, ('WrongFollow',)))
        else:
            # in the ABB mode, only store constant polynomials  
            def _storeFresh(phi):
                sh = self.fresh()
                self.share_table[sh] = polyFromCoeffs([x])
                return sh
            def _readSecret(sh):
                phi = self.share_table[sh]
                return eval_poly(phi, 0)
            res = do_abb_op(_readSecret, _storeFresh, self.inputs, op)
            self.pump.write('')
    
    def party_log(self, sender):
        self.write('f2p', (sender, ('Log', self.ops)))

    def party_input(self, sender, x):
        if sender == self.input_party:
            self.inputs += [x]
            self.write('f2p', (sender, ('OK',))) 
        else: self.pump.write('')

    def party_myshare(self, sender, sh):
        if self.has_mpc: 
            ms = self.share_table[sh]
            if ms is not None:
                self.write('f2p', (sender, ('myshare', ms)))
            else:
                self.write('f2p', (sender, ('WrongFollow',)))
        else: raise Exception('MYSHARE with no MPC')


fMPC = FMPC_(True, True)
fMPC_sansMULT = FMPC_(True, False)
fABB = FMPC_(False, True)
