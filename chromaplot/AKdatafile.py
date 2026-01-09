'''
ChromaPlot Version 0.1.1
Authors: Billy Hobbs and Felipe Ossa
© 2024 Billy Hobbs. All rights reserved.
'''

import csv
from io import StringIO

class AKdatafile:
    def __init__(self, datafilename):
        self.datafilename = datafilename
        self.datalines = []
        self.colnoerror = []
        self.colnocheck = []
        self.cc = None
        self.ce = None

        # Try a sensible list of encodings (handles °C in cp1252, UTF-16 with/without BOM, etc.)
        tried = []
        for enc in ("utf-8-sig", "utf-16", "utf-16-le", "utf-16-be", "cp1252", "latin-1"):
            try:
                with open(datafilename, "r", encoding=enc) as d:
                    self.datalines = d.readlines()
                break
            except Exception as e:
                tried.append((enc, str(e)))
                continue
        if not self.datalines:
            with open(datafilename, "rb") as d:
                raw = d.read()
            self.datalines = raw.decode("latin-1", errors="replace").splitlines(True)

    def _clean_field(self, s: str) -> str:
        s = s.strip()
        if len(s) >= 2 and ((s[0] == s[-1] == '"') or (s[0] == s[-1] == "'")):
            s = s[1:-1].strip()
        return s

    def _is_header_titles(self, tokens):
        joined = " ".join(tokens).lower()
        return any(k in joined for k in ("uv", "cond", "flow", "pressure", "temp", "fraction", "logbook"))

    def _is_header_units(self, tokens):
        units = {"ml", "mau", "mS/cm".lower(), "%", "%b", "mpa", "ml/min", "°c".lower(), "(fractions)", "(set marks)", "fraction", "logbook"}
        tset = {t.lower() for t in tokens}
        return any(u in tset for u in units)

    def _autodetect_headers(self):
        # Find consecutive (titles, units) lines
        for idx in range(min(10, max(0, len(self.datalines) - 1))):
            t1, _, _ = self.readline(self.datalines[idx])
            t2, _, _ = self.readline(self.datalines[idx + 1])
            if self._is_header_titles(t1) and self._is_header_units(t2):
                return idx, idx + 1
        return 1, 2

    '''Base function, splits each line by tab (or comma) delimiters and removes \n 
    characters, generates a list word which is used by other functions to parse
    the data file'''
    def readline(self, inline):
        word = inline.split('\t')
        if len(word) <= 1:
            reader = csv.reader(StringIO(inline))
            word = next(reader)
        colno = len(word)
        colnoerror = False
        if colno % 2 != 0:
            colno -= 1
            colnoerror = True
        word = [self._clean_field(w) for w in word[:colno]]
        return word, colno, colnoerror

    '''Initiates outer dictionary using column headings for the from the 
    extracted line'''
    def initodict(self, inlist, colno, colnoerror):
        odictkeys = []
        for i in range(0, colno, 2):
            odictkeys.append(inlist[i])
            values = [{} for x in range(0, colno, 2)]
            odict = dict(zip(odictkeys, values))
        return odictkeys, odict, colno, colnoerror

    '''Initiates inner dictionaries with empty lists, list keys are taken
    from column headins for extracted line'''
    def initidict(self, inlist, colno, colnoerror, indictkeys, indict, icols=2):
        maxcols = min(colno, 2 * len(indictkeys))
        for i in range(0, maxcols, 2):
            keys = [self._clean_field(inlist[i]), self._clean_field(inlist[i + 1])]
            values = [[] for _ in range(icols)]
            indict[indictkeys[i // 2]] = dict(zip(keys, values))
        return colno, colnoerror

    '''This fills in the initated lists and ignores blank values, note this 
    code block has issues running properly if UTF16 file format is used 
    directly not sure why. This will also use try and except to convert all
    numerical data into floats, hence faciliate plotting with numpy later'''
    def popcurves(self, inlist, colno, colnoerror, indictkeys, indict):
        maxcols = min(colno, 2 * len(indictkeys))
        for i in range(0, maxcols, 2):
            if i + 1 >= len(inlist):
                break
            if inlist[i] == "" and inlist[i + 1] == "":
                continue
            entry = indictkeys[i // 2]
            curvekeys = list(indict[entry].keys())

            def to_num(x):
                if x == "":
                    return None
                try:
                    return float(x)
                except ValueError:
                    return x  # keep strings for Fractions/Logbook

            v1 = to_num(inlist[i])
            v2 = to_num(inlist[i + 1])
            if v1 is not None:
                indict[entry][curvekeys[0]].append(v1)
            if v2 is not None:
                indict[entry][curvekeys[1]].append(v2)
        return colno, colnoerror

    '''This puts all the code together two argumnets h1 and h2 are taken which
    specifiy the lines with the column headings that form the keys for the 
    dictionary structures, checks in place to make sure that a) column numbers
    in data are even and b) all lines contain the same number of columns'''
    def genAKdict(self, h1=None, h2=None):
        if h1 is None or h2 is None:
            h1, h2 = self._autodetect_headers()

        curvelist, odict, cc, ce = self.initodict(*self.readline(self.datalines[h1]))
        self.colnoerror.append(ce); self.colnocheck.append(cc)

        cc, ce = self.initidict(*self.readline(self.datalines[h2]), curvelist, odict)
        self.colnoerror.append(ce); self.colnocheck.append(cc)

        for line in self.datalines[h2 + 1:]:
            cc, ce = self.popcurves(*self.readline(line), curvelist, odict)
            self.colnoerror.append(ce); self.colnocheck.append(cc)

        self.cc = self.colnocheck.count(self.colnocheck[0]) == len(self.colnocheck)
        self.ce = all(self.colnoerror)

        if "UV" not in odict:
            uv_candidates = [k for k in odict.keys() if "uv" in k.lower()]
            if uv_candidates:
                odict["UV"] = odict[uv_candidates[0]]
        return odict