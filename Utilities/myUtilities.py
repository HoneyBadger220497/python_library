class progressBar():
    def __init__(self,total,**kwargs):

        attributes = {
            "total": total,       # total number of iterations
            "prefix": "Progress", # prefix string (Str)
            "suffix": "Complete", # suffix string (Str)
            "decimals": 1,        # positive number of decimals
            "length": 50,         # character length of bar (Int)
            "fill": "█",          # bar fill character (Str)
            "printEnd": "\r"      # printEnd character (e.g. "\r", "\r\n")
            }

        for (param,default) in attributes.items():
            setattr(self,param,kwargs.get(param,default))

    def update(self,i):
        percent = ("{0:."+str(self.decimals)+"f}").format(100*(i/float(self.total)))
        filledlength = int(self.length * i // self.total)
        bar = self.fill * filledlength + '-' * (self.length - filledlength)

        print(f'\r{self.prefix} |{bar}| {percent}% {self.suffix}', end = self.printEnd)
        # Print New Line on Complete
        if i == self.total:
            print()

    def set_total(self,total):
        self.total = total
