from bs4 import BeautifulSoup
import requests
import time
import os
import os.path
from os import path
import sys
from more_itertools import last


ENTRIES_FILE = "entries.tmp"
DOWNLOAD_VIDEOS = True


def coom(file_path):

    file = open(ENTRIES_FILE, "r+").readlines()

    for entry in file:

        images, videos = [], []

        post = entry.split("\n")[0].split("/")[-1]

        print("== Post: " + post)

        result = requests.get("https://coomer.party" + str(entry).strip())
        postPage = BeautifulSoup(result.content, "html.parser")

        try :
            postfiles = postPage.find("div", class_="post__files")
            images = postfiles.find_all("a")
        except:
            pass

        if DOWNLOAD_VIDEOS:
            try:
                entryAttachments = postPage.find("ul", class_="post__attachments")
                videos = entryAttachments.find_all("a")

                for n, video in enumerate(videos):

                    path_file = f'{file_path}/{post}_{str(n)}.mp4'
                    if path.exists(path_file):
                        print("File exists. continue")
                        continue

                    try:
                        video_src = video["href"]
                        print(f'Downloading video {video_src}')
                    except:
                        print("Error in ripping a video")
                        continue

                    video_data = requests.get("https://data1.coomer.party" + video_src).content
                    with open(path_file, 'wb') as handler:
                        handler.write(video_data)
            except:
                pass

        # save images to disk
        for n, image in enumerate(images):

            path_file = f'{file_path}/{post}_{str(n)}.jpg'
            if path.exists(path_file):
                print("Image exists. continue")
                continue

            try:
                image_src = image["href"]
                print(f'Downloading image {image_src}')
            except:
                continue
            img_data = requests.get("https://www.coomer.party" + image_src).content
            with open(path_file, 'wb') as handler:
                handler.write(img_data)
    print("End")


def _get_pages_number(page):
    try:
        nextPageBtn = page.find(title="Next page").parent
        maxPageLink = nextPageBtn.find_previous("li")
        link = maxPageLink.find("a")["href"]
        lastPage = str(link).split("=")[-1]
        lastPage = int(lastPage) / 25 + 1
    except:
        lastPage = 1
    return lastPage

def ScanningPosts(handle):

    URL = f'https://coomer.party/onlyfans/user/{handle}'
    try:
        result = requests.get(URL)
        mainPage = BeautifulSoup(result.content, "html.parser")
    except:
        print("URL error. Make sure it is formatted correctly")

    posts = []

    lastPage = _get_pages_number(mainPage)

    print("PAGES #" + str(lastPage))

    # Finds all Entry links on current page
    def fetchPagesEntryLinks():
        # find the entry link html code
        tagOfPosts = mainPage.find_all("h2", class_="post-card__heading")
        for post_ in tagOfPosts:
            link = post_.find("a")
            # add said entry link to posts list
            posts.append(link["href"])
            print("Discovered entry: " + str(link["href"]))

    # fetch first page links then iterate through pages until last page

    for pageNumber in range(0, int(lastPage)):
        fetchPagesEntryLinks()
        pageNumber += 25
        print("Fetching posts on page " + str((pageNumber / 25)))
        time.sleep(1)
        result = requests.get(f'{URL}?o={str(pageNumber)}')
        print(result)
        mainPage = BeautifulSoup(result.content, "html.parser")

    postlistFile = open(ENTRIES_FILE, "w")
    for entry in posts:
        postlistFile.write(entry + "\n")
    postlistFile.close()


#def main(handle: str, output_dir: str):
def main():

    # url = input("Please Enter the URL of the creator from coomer.party: ")

    print("Usage: ")
    print("$ python Coomer.party-scraper [handle] [output-dir]")
    print("eg: python Coomer.party-scraper belledelphine ~/Images/")

    if (len(sys.argv) != 3):
        exit()

    handle, output_dir = sys.argv[1], sys.argv[2]

    if (output_dir[-1]=='/'):
        output_dir=output_dir[0:-1]

    file_path = f'{output_dir}/{handle}'
    if os.path.isdir(file_path):
        pass
    else:
        os.mkdir(file_path)
    ScanningPosts(handle)
    coom(file_path)


if __name__ == "__main__":
    main()
    #typer.run(main)
