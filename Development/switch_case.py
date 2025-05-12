# This code runs only in python 3.10 or above versions

def num_to_str(argument):
    match argument:
        case 0: 
            return "Menu"
        case 1:
            return "Camera"
        case 2:
            return "List"
        case 3:
            return "Auto Scroll"
        case 4:
            return "Options"
        case default:
            return "Menu"




num_to_str(2)