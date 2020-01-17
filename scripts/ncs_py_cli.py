#!/usr/bin/env python3
from __future__ import print_function
import ncs
import IPython

if __name__ == '__main__':
    m = ncs.maapi.Maapi()
    m.start_user_session('admin', 'system', [])
    trans = m.start_trans(ncs.RUNNING, ncs.READ_WRITE)

    x = ncs.maagic.get_root(trans)

    print("Your maagic object 'x -> %s' is now prepared... go have some fun!" %
          (str(x)))
    IPython.embed(display_banner=False)