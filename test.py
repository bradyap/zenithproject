import time

#convert unix timestamp to human readable time
def unixToTimestamp(unix):
    return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(unix))

def main():
    print("running...")
    userIn = input("please enter input:")
    print(unixToTimestamp(int(userIn)))

if __name__ == '__main__':
    main()

