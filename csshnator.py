import gtk, sys, getopt, math, subprocess
from configobj.configobj import ConfigObj
from os.path import expanduser

def main(argv):
    login = ''
    cluster_name = ''
    try:
        opts, args = getopt.getopt(argv,"hl:c:",["login=","cluster="])
    except getopt.GetoptError:
        print 'csshnator.py -l <login> -c <cluster>'
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print 'test.py -l <login> -c <cluster>'
            sys.exit()
        elif opt in ("-l", "--login"):
            login = arg
        elif opt in ("-c", "--cluster"):
            cluster_name = arg

    home = expanduser("~")
    window = gtk.Window()

    # the screen contains all monitors
    screen = window.get_screen()
    width = gtk.gdk.screen_width()
    height = gtk.gdk.screen_height()

    terminator_config = ConfigObj(home + '/.config/terminator/config');
    cssh_config = ConfigObj('.csshnatorrc');

    cluster_nodes = cssh_config[cluster_name].split()
    nnodes = len(cluster_nodes)

    #Compute geometry
    nrows = round(math.sqrt(nnodes))
    ncols = math.ceil(nnodes/nrows)

    nrows = int(nrows)
    ncols = int(ncols)

    # TODO calculate geometry better so don't need to create extra splits for
    # less than 3 nodes
    ncols = max(ncols, 2) #atlease 2 columns to make geometry easier

    #Construct layout
    vpane_name  = 'vpane'
    hpane_name  = 'hpane'
    term_name   = 'term'
    window_name = 'window'

    cssh_layout = {
            window_name + '0': {
                'position': '0:0',
                'type': 'Window',
                'parent': "",
                }
            }

    # VPaned/ Horizontal splits
    paneparent = window_name + '0'
    for vpane in range(0, nrows - 1):
        panepos = height/nrows # not used as far as I can tell
        paneratio = float(1.0/(nrows - vpane)) # 1/n ... 1/3,1/2
        panename = vpane_name + str(vpane);
        cssh_layout[panename] = {
                'type': 'VPaned',
                'order': min(vpane,1), #first pane order 0, all others order 1
                'position': panepos,
                'ratio': paneratio,
                'parent': paneparent,
                }
        paneparent = panename

    # HPaned / Veritcal Split
    for row in range(0, nrows):
        # First split, parent is VPaned
        order = 0
        paneparent = vpane_name + str(row)
        if (row == (nrows - 1)): # last row order is 1 last row parent is second to last
            order = 1
            paneparent = vpane_name + str(row - 1)
        panepos = width/ncols
        paneratio = float(1.0/(ncols))
        panename = hpane_name + str(row) + str(0); #hpaned00 ~ hpanedn0
        cssh_layout[panename] = {
                'type': 'HPaned',
                'position': panepos,
                'ratio': paneratio,
                'order': order,
                'parent': paneparent,
                }
        # Other panes parent is previous pane
        paneparent = panename
        for hpane in range(1, ncols - 1):
            panepos = width/ncols
            paneratio = float(1.0/(ncols - hpane))
            panename = hpane_name + str(row) + str(hpane); #hpaned00 ~ hpanednn
            cssh_layout[panename] = {
                    'type': 'HPaned',
                    'position': panepos,
                    'ratio': paneratio,
                    'order': 1,
                    'parent': paneparent,
                    }
            paneparent = panename

    # Child terminals parents are Hpanes
    node_ind = 0;
    for row in range(0, nrows):
        for col in range(0, ncols):
            node = cluster_nodes[node_ind] #get the node for this terminal
            order = 0
            termparent = hpane_name + str(row) + str(col) #parent is hpane
            command = 'ssh ' + login + '@' + node #ssh command
            #command = 'echo ' + login + '@' + node  + ' && bash '#for debugging
            if (node_ind >= nnodes):
                command = 'exit' #exit the terminal if there is no node for this

            if (col == (ncols - 1)): #last col order 1 and col-1 parent
                order = 1
                termparent = hpane_name + str(row) + str(col - 1)

            term = term_name + str(row) + str(col)
            cssh_layout[term] = {
                    'command': command,
                    'profile': 'default',
                    'type': 'Terminal',
                    'order': order,
                    'parent': termparent,
                    }

    #Write to config and launch terminator
    configname = 'cssh_config_' + cluster_name
    terminator_config['layouts'][configname] = cssh_layout
    terminator_config.write()
    subprocess.call(["terminator", "-l", "cssh_config_tmp"])

    #Clean up
    #del terminator_config['layouts']['cssh_config_tmp']
    #terminator_config.write()

if __name__ == "__main__":
    main(sys.argv[1:])
