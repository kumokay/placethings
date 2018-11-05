import msgpackrpc
import os
import math
import time

car_text = """
                     ___..............._
             __.. ' _'.""""""\\""""""""- .`-._ 
 ______.-'         (_) |      \\           ` \\`-. _
/_       --------------'-------\\---....______\\__`.`  -..___
| T      _.----._           Xxx|x...           |          _.._`--. _
| |    .' ..--.. `.         XXX|XXXXXXXXXxx==  |       .'.---..`.     -._
\_j   /  /  __  \  \        XXX|XXXXXXXXXXX==  |      / /  __  \ \        `-.
 _|  |  |  /  \  |  |       XXX|""'            |     / |  /  \  | |          |
|__\_j  |  \__/  |  L__________|_______________|_____j |  \__/  | L__________J
     `'\ \      / ./__________________________________\ \      / /___________\\
     `.`----'.'   dp                                `.`----'.'
          `""""'                                         `""""'
"""

person_text = """
      ////\\\\
      |      |
     @  O  O  @
      |  ~   |         \__
       \ -- /          |\ |
     ___|  |___        | \|
    /          \      /|__|
   /            \    / /
  /  /| .  . |\  \  / /
 /  / |      | \  \/ /
<  <  |      |  \   /
 \  \ |  .   |   \_/
  \  \|______|
    \_|______|
      |      |
      |  |   |
      |  |   |
      |__|___|
      |  |  |
      (  (  |  Elissa Potier
      |  |  |
      |  |  |
     _|  |  |
 cccC_Cccc___)
"""



class FileServer(object):
    def __init__(self):
        self.cnt = 0
        self.result = 'new result is not available 1'

    def get_result(self, ts):
        return '{}, {}'.format(self.result, self.cnt)

    def push(self, data, ts):
        print('notification {} at {} 111'.format(self.cnt, ts))
        self.cnt += 1
        if 'car' in data:
            print(car_text)
            self.result = 'car!'
        elif 'person' in data:
            print(person_text)
            self.result = 'person!'
        else:
            print('nothing!')
            self.result = 'nothing found!'
        print(self.result)
        # save the file
        return 'received {} bytes'.format(len(self.result))


# print(display_text)
server = msgpackrpc.Server(FileServer())
server.listen(msgpackrpc.Address('172.17.51.1', 18900))
server.start()
