##################################################################################################
"""
def menu(items, up, down, func):
    global config_font, photo_array, h
    current=items[h]
    print(str(len(items)))
    if up==False: h+=1
    elif down==False: h-=1
    elif func==False:
        selection=items[h]
        return selection

    # Check menu increment
    if h>len(items)-1: h=0
    elif h<0: h=len(items)-1
    new=items[h]    

    # Highlight menu item
    if new!=current:
        for i in items:
            if i==items[h] and i!='Menu':
                print("> "+i)
            elif i!="Menu":
                print(i)

##################################################################################################
"""

def menu(menu_title, items, up, down, func):
	global config_font, photo_array, h
	old=items[h]
	limit=len(items)-1
	if up==False: h+=1
	elif down==False: h-=1
	elif func==False:
		return items[h] # → selection
    # Check menu increment
	if h>limit: h=0
	elif h<0: h=limit
	new=items[h]

	# Highlight menu item
	print("New: "+new+" Old: "+old)
	if new!=old:
		print(menu_title)
        # Loop through items
		for i in items:
			if i==items[h] and i!='Menu':
				i="> "+i
			if i!="Menu":
				print(i)
	return items[h] # return the old value if no btn press, so that menu doesn't rebuild

menu_items=['Menu', 'Camera', 'Options', 'List', 'Autoscroll', 'Time Lapse', 'Delete']

h=1

selection=menu("~~~ Menu Title ~~~", menu_items, False, True, True)

print("SELECTION:"+str(selection))