import time

class Light:
    def __init__(self):
        # colour_id 0 = RED
        self.__colour_id = 0

    ## loop continuously updates the LED colours
    def loop(self, exit_event):
        while not exit_event.is_set():
            self.__updateColour()
            if self.__colour_id == 0:
                print("Traffic light is RED")
            time.sleep(5)

    ## __updateColour checks __colour_id and updates the variable accordingly
    def __updateColour(self):
        if self.__colour_id == 0:
            self.__colour_id = 1
        elif self.__colour_id == 1:
            self.__colour_id = 2
        else:
            self.__colour_id = 0
        
    ## is_red sets the __colour_id to 0    
    def is_red(self):
        return self.__colour_id == 0
