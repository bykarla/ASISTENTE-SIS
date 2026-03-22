import socket
import time

def is_port_open(ip, port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(2)
    try:
        s.connect((ip, port))
        return True
    except:
        return False
    finally:
        s.close()

if __name__ == "__main__":
    print("Waiting for port 8000 to open...")
    for i in range(120): # Wait 10 minutes
        if is_port_open("127.0.0.1", 8000):
            print("Port 8000 is open!")
            break
        if i % 10 == 0:
            print(f"Still waiting... ({i*5}s)")
        time.sleep(5)
    else:
        print("Timeout waiting for port 8000.")
