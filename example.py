import elelementary as el

elel_file = el.load_elel('example.elel') #load the elelmentart block file
sps_file = el.load_sps('example.sps') # load the special file

elel_file.bind(sps_file) # bind the special file the elel file to apply style and logic

elel_file.open() # launch the elel file as a program