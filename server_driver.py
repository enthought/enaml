from uuid import uuid4
import json
import zmq


first = [
    {
        'session': None,
        'username': 'chris.colbert',
        'msg_id': uuid4().hex,
        'msg_type': 'enaml_discover',
        'version': '1.0',
    },
    {},
    {},
    {},
]


second = [
    {
        'session': None,
        'username': 'chris.colbert',
        'msg_id': uuid4().hex,
        'msg_type': 'enaml_begin_session',
        'version': '1.0',
    },
    {},
    {},
    {
        'name': 'test-view',
    },
]


third = [
    {
        'session': None,
        'username': 'chris.colbert',
        'msg_id': uuid4().hex,
        'msg_type': 'enaml_snapshot',
        'version': '1.0',
    },
    {},
    {},
    {},
]


fourth = [
    {
        'session': None,
        'username': 'chris.colbert',
        'msg_id': uuid4().hex,
        'msg_type': 'enaml_end_session',
        'version': '1.0',
    },
    {},
    {},
    {},
]


def pack(message):
    return [json.dumps(part) for part in message]

def unpack(mpmsg):
    return [json.loads(part) for part in mpmsg]


import time

if __name__ == '__main__':
    ctxt = zmq.Context()
    sock = ctxt.socket(zmq.DEALER)
    sock.connect('tcp://127.0.0.1:8888')
    #print '-------------'
    t1 = time.time()
    sock.send_multipart(pack(first))
    first_reply = unpack(sock.recv_multipart())
    t2 = time.time()
    print 'first', t2 - t1
    #pprint.pprint(first_reply)
    #print '-------------'
    t3 = time.time()
    sock.send_multipart(pack(second))
    second_reply = unpack(sock.recv_multipart())
    t4 = time.time()
    print 'second', t4 - t3
    #pprint.pprint(second_reply)
    #print '-------------'
    t5 = time.time()
    third[0]['session'] = second_reply[-1]['session']
    sock.send_multipart(pack(third))
    third_reply = unpack(sock.recv_multipart())
    t6 = time.time()
    print 'third', t6 - t5
    #pprint.pprint(third_reply)
    #print '-------------'
    t7 = time.time()
    fourth[0]['session'] = second_reply[-1]['session']
    sock.send_multipart(pack(fourth))
    fourth_reply = unpack(sock.recv_multipart())
    #pprint.pprint(fourth_reply)
    t8 =  time.time()
    print 'fourth', t8 - t7

