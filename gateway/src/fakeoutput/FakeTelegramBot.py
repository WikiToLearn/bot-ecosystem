
class FakeTelegramBot(object):
    def sendMessage(self,t_channel,t_msg):
        print("FakeTelegramBot: {} > {}".format(t_channel,t_msg))
