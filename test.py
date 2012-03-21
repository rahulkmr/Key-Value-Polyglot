import pylibmc

mc = pylibmc.Client(["127.0.0.1"])

# set
for i in range(10000):
    mc.set(str(i), i) # This hashmap syntax writes to memcached
# get
for i in range(10000):
    val = mc.get(str(i))        # Hashmap syntax reads from memcached
    assert(int(val) == i)
