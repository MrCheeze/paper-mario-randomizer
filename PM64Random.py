import random
import os
import json

infile = 'Paper Mario (USA).z64'
outfile = 'Paper Mario (USA) - Randomized.z64'

os.system('copy "%s" "%s"' % (infile, outfile))
f=open(outfile,'rb+')

roomdata = json.load(open('roomdata.json'))

roomnames = list(roomdata.keys())
roomnames.remove('end_00')
roomnames.remove('end_01')
roomnames.remove('gv_01')
roomnames.remove('mgm_03')
roomnames.remove('tst_11')
roomnames.remove('tst_12')
roomnames.remove('tst_13')
roomnames.remove('tst_20')

roomnames.remove('hos_04')
roomnames.remove('hos_05')
roomnames.remove('hos_10')
roomnames.remove('mac_05')

rooms = []

#make sure this is a paper mario rom with proper endianness
f.seek(0x20)
assert(f.read(11) == b'PAPER MARIO')

#code patch: start with goombario out
f.seek(0x808A8)
f.write((0xA0820012).to_bytes(4,'big'))
f.write((0xA082000A).to_bytes(4,'big')) # enable action command
f.write((0x2402FFFF).to_bytes(4,'big'))
f.seek(0x808E4)
f.write((0xA0800000).to_bytes(4,'big'))
#have every party member
f.write((0xA0A20014).to_bytes(4,'big'))
#enable menus
f.seek(0x168074)
f.write((0x2406FF81).to_bytes(4,'big'))
#don't start the game from mario's house
#f.seek(0x168080)
#f.write((0x24020000).to_bytes(4,'big'))

for i in range(421):
    f.seek(0x6B450 + i*0x20)
    nameptr = int.from_bytes(f.read(4), 'big') - 0x80024C00
    f.seek(4, os.SEEK_CUR)
    roomptr = int.from_bytes(f.read(4), 'big')
    f.seek(nameptr)
    name = f.read(8).decode().strip('\0')
    already_randomized = {}
    for warpptr in roomdata[name]['warp_ptrs']:
        if warpptr in already_randomized:
            randroom = already_randomized[warpptr]
        else:
            randroom = random.choice(roomnames)
            already_randomized[warpptr] = randroom
        rand_entrance = random.choice(roomdata[randroom]['entrances'])
        
        f.seek(roomptr + warpptr - 0x80240000 + 0xC)
        warproom_ptr = int.from_bytes(f.read(4), 'big')
        f.write(rand_entrance.to_bytes(4,'big'))
        f.seek(roomptr + warproom_ptr - 0x80240000)
        f.write(randroom.encode()+b'\0')
    for itemptr in roomdata[name]['items']:
        f.seek(roomptr + itemptr - 0x80240000)
        randitem = random.randint(1,0x16C)
        if 0 < int.from_bytes(f.read(4), 'big') < 0x200:
            f.seek(-4, os.SEEK_CUR)
            f.write(randitem.to_bytes(4,'big'))

    

f.close()
os.system('rn64crc\\rn64crc.exe "%s" -u' % outfile)
