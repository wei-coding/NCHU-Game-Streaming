import Audio, socket
def main():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    port = 12346
    sender = Audio.AudioSender(s,port)
    recoder = Audio.AudioRecoder()
if __name__=='__main__':
    main()