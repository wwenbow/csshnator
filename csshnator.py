import gtk, sys, getopt, math, subprocess
from configobj.configobj import ConfigObj
from os.path import expanduser

def main(argv):
    login = ''
    cluster_name = ''
    try:
        opts, args = getopt.getopt(argv,"hl:c:",["login=","cluster="])
    except getopt.GetoptError:
        print 'test.py -l <login> -c <cluster>'
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

    # TODO remove this
    nrows = 5
    ncols = 5

    #Construct layout
    cssh_layout = {
            'window0': {
                    'position': '0:0',
                    'type': 'Window',
                    'parent': "",
                    'size': '1366, 768'
                }
            }

    rowparent = 'window0'
    for row in range(1, nrows):
        splitpos = height/nrows
        splitratio = float(1.0/(nrows + 1 - row))
        cssh_layout['row' + str(row)] = {
                    'type': 'VPaned',
                    'order': min(row-1,1),
                    'position': splitpos,
                    'ratio': splitratio,
                    'parent': rowparent,
                }
        rowparent = 'row' + str(row)
        colparent = rowparent
        nchild_col = 1
        if (row == nrows-1):
            nchild_col = 2
        for child_col in range(0, nchild_col):
            cssh_layout['term' + str(row) + str(child_col)] = {
                    'profile': 'default',
                    'type': 'Terminal',
                    'order': child_col,
                    'parent': rowparent,
                    }
            print cssh_layout
        #    for col in range(1, ncols):
        #        splitpos = width/ncols
        #        cssh_layout['col' + str(row) + str(col)] = {
        #                    'type': 'HPaned',
        #                    'position': splitpos,
        #                    'order': child_col,
        #                    'parent': colparent,
        #                }
        #        colparent = 'col' + str(row) + str(col)
        #        nchild_term = 1
        #        if (col == ncols-1):
        #            nchild_term= 2
        #        for child_term in range(0, nchild_col):
        #            cssh_layout['term' + str(row) + str(col) + str(child_term)] = {
        #                        'profile': 'default',
        #                        'type': 'Terminal',
        #                        'order': child_term,
        #                        'parent': colparent,
        #                    }
        #            print cssh_layout



    #Write to config and launch terminator
    terminator_config['layouts']['cssh_config_tmp'] = cssh_layout
    terminator_config.write()
    subprocess.call(["terminator", "-l", "cssh_config_tmp"])

    #Clean up
    del terminator_config['layouts']['cssh_config_tmp']
    terminator_config.write()

if __name__ == "__main__":
    main(sys.argv[1:])
