"""
Telescraper
Developed by Zack Whitson
Telegram: @definitezer0
X (Twitter): @Delirium_Pulse
Website: www.zackwhitson.com
Upwork: https://www.upwork.com/freelancers/~01b74427823660e746
"""
import sys
import asyncio
import qasync
from PyQt6.QtWidgets import QApplication
from gui import MainWindow
from client_manager import ClientManager

def main():
    app = QApplication(sys.argv)
    
    # Create the event loop
    loop = qasync.QEventLoop(app)
    asyncio.set_event_loop(loop)
    
    client_manager = ClientManager()
    window = MainWindow(client_manager)
    window.show()
    
    with loop:
        loop.run_forever()

if __name__ == "__main__":
    main()
