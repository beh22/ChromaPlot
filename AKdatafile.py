class AKdatafile:
    def __init__ (self, datafilename):
        self.datafilename = datafilename
        self.datalines = []
        self.colnoerror = []
        self.colnocheck = []
        self.cc = None
        self.ce = None
        
        try:
            with open(datafilename, 'r', encoding='UTF-8') as d:
                self.datalines = d.readlines()
        except:
            with open(datafilename, 'r', encoding='UTF-16') as d:
                self.datalines = d.readlines()

    '''Base function, splits each line by tab delimiters and removes \n 
    characters, generates a list word which is used by other functions to parse
    the data file'''
    def readline (self, inline): 
        word = inline.split('\t')
        colno = len(word)
        colnoerror = False
        if colno % 2 != 0:
            colno = colno - 1
            colnoerror = True
        for i in range(colno):
            word[i] = word[i].rstrip()
        return word, colno, colnoerror

    '''Initiates outer dictionary using column headings for the from the 
    extracted line'''
    def initodict (self, inlist, colno, colnoerror):
        odictkeys = []
        for i in range(colno)[::2]:
            odictkeys.append(inlist[i])
            values = [{} for x in range(colno)[::2]]
            odict = dict(zip(odictkeys, values))
        return odictkeys, odict, colno, colnoerror

    '''Initiates inner dictionaries with empty lists, list keys are taken
    from column headins for extracted line'''
    def initidict (self, inlist, colno, colnoerror, indictkeys, indict, icols=2):
        for i in range(colno)[::2]:
            keys = [inlist[i], inlist[i+1]]
            values = [[] for x in range(icols)]
            indict[indictkeys[int(i/2)]] = dict(zip(keys, values))
        return colno, colnoerror

    '''This fills in the initated lists and ignores blank values, note this 
    code block has issues running properly if UTF16 file format is used 
    directly not sure why. This will also use try and except to convert all
    numerical data into floats, hence faciliate plotting with numpy later'''
    def popcurves(self, inlist, colno, colnoerror, indictkeys, indict):
        for i in range(colno)[::2]:
            if inlist[i] == '' and inlist[i+1] == '':
                pass
            else:
                entry = indictkeys[int(i/2)]
                curvekeys = [*indict[entry].keys()]
                try:
                    value1 = float(inlist[i]) if inlist[i] else None
                except ValueError:
                    value1 = inlist[i] if inlist[i] else None
                try:
                    value2 = float(inlist[i+1]) if inlist[i+1] else None
                except ValueError:
                    value2 = inlist[i+1] if inlist[i+1] else None
                
                if value1 is not None:
                    indict[entry][curvekeys[0]].append(value1)
                if value2 is not None:
                    indict[entry][curvekeys[1]].append(value2)
        return colno, colnoerror

    '''This puts all the code together two argumnets h1 and h2 are taken which
    specifiy the lines with the column headings that form the keys for the 
    dictionary structures, checks in place to make sure that a) column numbers
    in data are even and b) all lines contain the same number of columns'''
    def genAKdict (self, h1, h2):
        curvelist, odict, cc, ce = self.initodict(*self.readline(self.datalines[h1]))
        self.colnoerror.append(ce)
        self.colnocheck.append(cc)
        cc, ce = self.initidict(*self.readline(self.datalines[h2]), curvelist, odict)
        self.colnoerror.append(ce)
        self.colnocheck.append(cc)
        for line in self.datalines[h2+1:]:
            cc, ce = self.popcurves(*self.readline(line), curvelist, odict)
            self.colnoerror.append(ce)
            self.colnocheck.append(cc)
        self.cc = self.colnocheck.count(self.colnocheck[0]) == len(self.colnocheck)
        self.ce = all(self.colnoerror)
        # These lines should fix loading in data from the purple akta, but currently cause more problems than they solve
        # uvkey = [x for x in odict.keys() if 'UV' in x] 
        # odict['UV'] = odict[uvkey[0]]
        # del odict[uvkey[0]]
        return odict