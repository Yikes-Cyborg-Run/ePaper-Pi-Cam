##################################################################################################

def config_menu(old_value, items, up, down, func):
    # NOTES:
	# OK, so we need to pass in the item that is going to be edited,
	# and also need the current setting
    global config_font, h
    limit=len(items)-1
    if up==False: h+=1
    elif down==False: h-=1
    elif func==False:
        # SAVE CONFIG
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
            print(i)
    return items[h] # return the old value if no btn press, so that menu doesn't rebuild

##################################################################################################

menu_items=['True', 'False']

h=0

timestamp_photo=config_menu("~~~ Menu Title ~~~", menu_items, False, True, True)

print("SELECTION:"+str(selection))