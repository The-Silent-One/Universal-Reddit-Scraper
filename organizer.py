from glob import glob
import csv
path = "output/"

class Post:

    def __repr__(self):
        return "Title:\n{}\nText:\n{}\nComments:\n{}\n".format(
            self.title , self.text , self.comments)
    
    def __eq__(self,other):
        return self.title == other.title

    def clean(self):
        self.text = self.text.replace("&nbsp;","")
        self.text = self.text.replace("&#x200B;","")
        self.text = self.text.replace("**","")
        self.text = self.text.replace("\n\n","")
        for i in range(len(self.comments)):
            if("I'm a bot" in self.comments[i]):
                self.comments.remove(self.comments[i])
                continue
            self.comments[i] = self.comments[i].replace("&nbsp;","")
            self.comments[i] = self.comments[i].replace("&#x200B;","")
            self.comments[i] = self.comments[i].replace("**","")
            self.comments[i] = self.comments[i].replace("\n\n","")

    def __init__(self,row):
        self.title = row[0]
        self.text = row[1]
        self.comments = row[2].split('","')
        self.clean()            

    def toList(self):
        return [ self.title , self.text ] + [c for c in self.comments]
    
def walker(path):
    combined = []
    for file in glob(path+"*.csv"):
        f = open(file,'r')
        reader = csv.reader(f,delimiter=",")
        for row in reader:
            p = Post(row)
            if( p not in combined ):
                combined.append(p)
        f.close()
    
    return combined

def writer(combined):
    f = open("data.csv","w")
    w = csv.writer(f,delimiter=",",quotechar='"', quoting=csv.QUOTE_MINIMAL)
    for i in combined:
        w.writerow(i.toList())
    f.close()
combined = walker(path)
print(len(combined))
writer(combined)
