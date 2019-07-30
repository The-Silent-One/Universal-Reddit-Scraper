import praw
from prawcore import NotFound
import csv
import datetime as dt

c_id = "###"
c_secret = "###"
u_a = "###"
usrnm = "###"
passwd = "###"

date = dt.datetime.now().strftime("%m-%d-%Y")

categories = ["Hot","New","Controversial","Top","Rising","Search"]

max_comments = 5

line_mul = 52
path = "./output/"

def existence(reddit,sub_list):
    found = []
    not_found = []

    for sub in sub_list:
        try:
            reddit.subreddits.search_by_name(sub, exact = True)
            found.append(sub)
        except NotFound:
            not_found.append(sub)

    return found,not_found

def title():
    print("="*line_mul)
    print("\n\tReddit Scraper\n")
    print("="*line_mul)

def confirm_subs(reddit,sub_list):
    print("\nChecking if subreddit(s) exist...\n")
    found,not_found = existence(reddit,sub_list)
    if found:
        print("\nThe following subreddits were found:")
        print("-"*line_mul)
        print(*not_found, sep = "\n")
        print("-"*line_mul)
        
    if not_found:
        print("\nThe following subreddits were not found and will be skipped:")
        print("-"*line_mul)
        print(*not_found, sep = "\n")
        print("-"*line_mul)
        
    subs = [sub for sub in found]
    return subs

def connect():
    try:
        reddit = praw.Reddit(client_id = c_id ,
                             client_secret = c_secret ,
                             user_agent = u_a ,
                             username = usrnm ,
                             password = passwd)
        return reddit
    
    except praw.exceptions.APIException as e:
        print("\nThere was a server-side error.")
        print(e.error_type)
        print(e.message)
        print(e.field)

    except praw.exceptions.ClientException:
        print("\nThere was a client-side error.")
        
def getSubreddits(reddit):
    while True:
        try:
            search_for = str(input(" Enter a list of subreddits to search separated by a space or a .txt file:\n"))
            if(".txt" in search_for.strip()):
                f = open(search_for,"r")
                search_for = " ".join([ i.strip() for i in f.readlines()])
                f.close()
            if not search_for :
                raise ValueError
            sub = [ s.strip() for s in search_for.split(" ") ]
            sub_list = [subreddit for subreddit in search_for.split(" ")]
            found,not_found = existence(reddit,sub_list)
            if found:
                print("\nThe following subreddits were found and will be scraped:")
                print("-"*line_mul)
                print(*found, sep = "\n")
            if not_found:
                print("\nThe following subreddits were not found and will be skipped:")
                print("-"*line_mul)
                print(*not_found, sep = "\n")
            confirm = str(input("\nConfirm selection? [Y/N] ")).strip()
            if confirm.lower():
                return found
            else:
                raise ValueError
        except Exception:
            print("Wrong input.")

def createDict(subs):
    return dict((sub,[]) for sub in subs)

def getSettings(subs,master):
    while True:
        try:
            search_for = str(input("\nWhat to search for or a .txt file:\n")).strip()
            if not search_for:
                raise ValueError
            else:
                if ( ".txt" in search_for.strip()):
                    f = open(search_for,"r")
                    search_for = " ".join([ i.strip()
                                            for i in f.readlines()])
                    f.close()
                for sub in subs:
                    for sub_n,values in master.items():
                        if sub_n == sub:
                            for search in search_for.split(" "):
                                settings = [5,search]
                                master[sub].append(settings)
                break
        except Exception:
            print("Wrong input! Try again.")

def printSettings(master):
    print("\n------------------Current settings for each subreddit-------------------")
    print("\n{:<25}{:<17}{:<30}".format("Subreddit","Category","Number of results / Keyword(s)"))
    print("-"*line_mul)
    for sub,settings in master.items():
        for each in settings:
            cat_i = each[0]
            specific = each[1]
            print("\n{:<25}{:<17}{:<30}".format(sub,categories[cat_i],specific))
    confirm = input("\nConfirm options? [Y/N] ").strip()
    if confirm.lower() == "y":
        return True
    else:
        return False

def getPosts(reddit,sub,cat_i,search_for):
    print("\nGetting posts for r/%s..." % sub)
    subreddit = reddit.subreddit(sub)
    return subreddit.search("%s" % search_for)

def getTopComments(post):
    return " , ".join([ comment.body for comment in post.comments[:max_comments]])

def sortPosts(collected):
    print("Sorting posts...")
    overview = {"Title" : [] , "Text" : [] , "Comments" : []}

    for post in collected:
        overview["Title"].append(post.title)
        overview["Text"].append(post.selftext)
        overview["Comments"].append(getTopComments(post))

    return overview

def writeCSV(sub,overview,x):
    fname = str(("%s-%s-%s-%s.csv") % ( sub , "Search" , str(x) , date ))
    results = open(path+fname,"w")
    writer = csv.writer(results, delimiter = ",")
    writer.writerow(overview.keys())
    writer.writerows(zip(*overview.values()))
    print("CSV file %s for r/%s created." % (fname , sub))
    results.close()
    
def get_sort_write(reddit,master):
    for sub,settings in master.items():
        x = 1
        for each in settings:
            cat_i = each[0]
            search_for = each[1]
            collected = getPosts(reddit,sub,cat_i,search_for)
            overview = sortPosts(collected)
            writeCSV(sub,overview,x)
            x=x+1
def main():
    title()
    reddit = connect()
    if reddit:
        subs = getSubreddits(reddit)
        master = createDict(subs)
        getSettings(subs,master)
        if(printSettings(master)):
            get_sort_write(reddit,master)
        else:
            print("\nClosing\n")
    else:
        print("\ncould not connect\n")

main()
