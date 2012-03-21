import pylibmc

mc = pylibmc.Client(["127.0.0.1"])

# Check \r\n in data
mc.set('br', 'one\r\ntwo')
assert(mc.get('br') == 'one\r\ntwo')

# set
for i in range(500):
    mc.set(str(i), i) # This hashmap syntax writes to memcached
# get
for i in range(500):
    val = mc.get(str(i))        # Hashmap syntax reads from memcached
    assert(int(val) == i)
