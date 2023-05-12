import re
import sys
import requests
import getopt
import pandas as pd
from bs4 import BeautifulSoup
import urlexpander


class formatter:
    """ Produces a class object from a provided URLs list and initializes with attributes common to both unshorten() and clean().
"""
    
    def __init__(self, raw_links):
        self.raw_links = raw_links

        """ known_shorteners contains a list of url shorteners that will
        be used to extract shortened URLs from raw_links. """
        self.known_shorteners = urlexpander.constants.all_short_domains.copy()
        self.known_shorteners += ["youtu.be", "shorturl.me"]

        # produce a list containing only shortened URLs
        self.shortened_urls_list = [
            link for link in self.raw_links
            if urlexpander.is_short(link, list_of_domains=self.known_shorteners)
        ]
        self.shortened_urls_garbage = []

        # these two pandas dataframes will store error messages in a searchable format for formatter's two methods
        self.unshorten_errors_df = pd.DataFrame({"url": [], "error_message": [], "platform": []})
        self.clean_errors_df = pd.DataFrame({"url": [], "error_message": [], "platform": []})

        self.headers = {
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)\
        AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.5615.121 Safari/537.36"
        }

        self.unshorten_executed = False
        self.clean_executed = False

    def unshorten(self):
        """Unshortens shortened URLs contained in self.shortened_urls_list. After completion unshorten()
returns 'self.raw_with_expansion', a list combining unshortened URLs with URLs that weren't
originally shortened.
        
If not exectuted prior to running clean(), clean() will discard shortened URLs.
        
workflow:
        
unshorten URLs using requests--> extract non-social media URLs from 'raw_links' into 'self.not_shortened_links'
-->produce 'self.raw_with_expansion', a list combining unshortened URLs with 'self.not_shortened_links'-->
set 'self.unshorten_executed' to True-->print success metric-->return 'self.raw_with_expansion'
"""
        
        self.not_shortened_links = []
        self.expanded_urls_list = []
        self.shortened_urls_garbage = []

        self.unshorten_errors_df = pd.DataFrame({"url": [], "error_message": [], "platform": []})

        def unshorten_url(url):
            if not re.match("https?://", url):
                url = "https://" + url
            session = requests.Session()  # so connections are recycled
            try:
                resp = session.head(url, allow_redirects=True)
                unshortened_url = re.sub("https?://(www\.)?", "", resp.url)
                self.expanded_urls_list.append(unshortened_url)
            except Exception as error:
                # if there is an error attempt to extract unshortened URL from error message
                if len(re.findall("(?<=host=').*(?=', port)", str(error))) != 0:
                    unshortened_url = re.findall("(?<=host=').*(?=', port)", str(error))
                    unshortened_url = re.sub("https?://(www\.)?", "", unshortened_url[0])
                    self.expanded_urls_list.append(unshortened_url)
                else:
                    #if this is unsuccessful discard shortened URL
                    self.shortened_urls_garbage.append(url)
                    self.unshorten_errors_df.loc[len(self.unshorten_errors_df.index)] = [url, error, "shortened_url"]

        for url in self.shortened_urls_list:
            unshorten_url(url)

        # substract shortened URLs from raw_links to produce not_shortened_links
        for link in self.raw_links:
            if not urlexpander.is_short(link, list_of_domains=self.known_shorteners):
                self.not_shortened_links.append(link)

        # combine not_shortened_links with expanded_urls_list
        self.raw_with_expansion = self.not_shortened_links + self.expanded_urls_list
        self.raw_with_expansion = [re.sub("https?://(www\.)?", "", i) for i in self.raw_with_expansion]

        self.unshorten_executed = True
        print(
            f"\n{len(self.shortened_urls_list)} shortened URLs were detected, of which \
{len(self.expanded_urls_list)} were successfully unshortened.\n"
        )

        self.joined_errors_df = self.unshorten_errors_df._append(self.clean_errors_df, ignore_index=True)

        return self.raw_with_expansion

    def clean(self):
        """ clean() reformats URLs into an analytically useful format. For non-social media URLs,
this involves extracting domain names; for social media URLs, this includes converting a link to
a specific post to the URL for the account of the user that posted it.
        
Additionally, it will collate any errors and discarded URLs and print metrics to the screen after completion.
        
workflow:
        
if unshorten() not executed discard shortened URLs--> extract social media URls--> sort and process social media
URLs--> format non-social media URLs--> format special-case social media URLs--> produce error and discard metrics
--> return list of cleaned URLs
"""
        
        self.clean_errors_df = pd.DataFrame({"url": [], "error_message": [], "platform": []})

        if self.unshorten_executed is False:
            self.raw_with_expansion = self.raw_links.copy()
            self.raw_with_expansion = [i for i in self.raw_with_expansion if i not in self.shortened_urls_list]
            self.raw_with_expansion = [re.sub("https?://(www\.)?", "", i) for i in self.raw_with_expansion]

        # categorize and format social media links
        self.sm_urls_list = []
        self.non_sm_urls_list = []
        self.sm_other_urls_list = []
        self.fb_watch_list = []
        self.youtube_watch_list = []
        self.vk_list = []

        self.tiktok_garbage = []
        self.ig_garbage = []
        self.youtube_garbage = []
        self.facebook_garbage = []
        self.twitter_garbage = []
        self.bitchute_garbage = []
        self.odysee_garbage = []
        self.rumble_garbage = []
        self.gettr_garbage = []
        self.mail_garbage = []
        self.non_url_garbage = []

        self.sm_platforms_re = "^(m\.|mobile\.)?(odysee|vk\.|instagram|twitter|facebook|fb\.watch|\
youtube\.com|t\.me|tiktok\.|vm\.tiktok|bitchute|gettr\.com|reddit\.|rumble\.com|gab\.com|4chan\.org).*"
        self.sm_filter = re.compile(self.sm_platforms_re)
        self.sm_with_expansion = [i for i in self.raw_with_expansion if self.sm_filter.match(i)]

        for link in self.raw_with_expansion:
            if re.match("(css|photos|messages|#go_to_message|\)\[\^)", link): # this REGEX discards non-URLs typical of Telegram URL scrapes
                self.non_url_garbage.append(link)
            elif re.match("mailto", link):
                self.mail_garbage.append(link)
            elif link in self.sm_with_expansion:
                continue
            else:
                self.non_sm_urls_list.append(re.sub("/.*", "", link))

        self.sm_with_expansion = [re.sub("^(m\.|mobile\.)", "", i) for i in self.sm_with_expansion
                                  if not re.match("m\.tiktok\.com", i)]
        for link in self.sm_with_expansion:
            if re.match("(instagram\.com/p/|instagram\.com/tv)", link): # these are discarded because usernames cannot be extracted from them
                self.ig_garbage.append(link)
            elif re.search(
                "(twitter\.com/.*/status|facebook\.com/.*/posts|reddit\.com/r/.*/comments)", link):
                link = re.sub("(/status.*|/posts.*|/comments.*)", "", link)
                self.sm_urls_list.append(link)
            elif re.match("twitter\.com/hashtag", link):
                self.twitter_garbage.append(link)
            elif re.search("facebook\.com/.*/videos", link):
                link = re.sub("/videos.*", "", link)
                self.sm_urls_list.append(link)
            elif re.match("(facebook\.com/watch|fb\.watch)", link):
                self.fb_watch_list.append(link) # place in a special list for later processing
            elif re.match("facebook\.com/story", link):
                self.facebook_garbage.append(link)
            elif re.match("t\.me/", link):
                link = re.findall("t\.me/[-+_a-zA-Z0-9]*", link)
                self.sm_urls_list.append(link[0])
            elif re.search("youtube\.com/c/", link):
                link = re.sub("/c/", "/@", link)
                self.sm_urls_list.append(link)
            elif re.search("youtube\.com/channel", link):
                try:
                    page_content = requests.get("https://" + link, headers=self.headers).content
                    if (len(re.findall('(?<="webCommandMetadata":{"url":"/).*(?=/featured)', str(page_content)))!= 0):
                        link = re.findall('(?<="webCommandMetadata":{"url":"/).*(?=/featured)', str(page_content))
                        link = "youtube.com/" + link[0]
                        self.sm_urls_list.append(link)
                    else:
                        self.youtube_garbage.append(link)
                except Exception as error:
                    self.clean_errors_df.loc[len(self.clean_errors_df.index)] = [
                        link,
                        error,
                        "youtube",
                    ]
                    self.youtube_garbage.append(link)
            elif re.match("youtube\.com/results", link):
                self.youtube_garbage.append(link)
            elif re.match("(youtube\.com/watch|youtube\.com/live)", link):
                self.youtube_watch_list.append(link) # place in a special list for later processing
            elif re.match("odysee\.com/[^@]", link):
                try:
                    page_content = requests.get("https://" + link, headers=self.headers).content
                    if (len(re.findall('(?<="og:url" content="https://)[\.@-_/a-zA-Z0-9]+', str(page_content)))!= 0):
                        link = re.findall('(?<="og:url" content="https://)[\.@-_/a-zA-Z0-9]+', str(page_content))[0]
                        self.sm_urls_list.append(link)
                    else:
                        self.odysee_garbage.append(link)
                except Exception as error:
                    link = re.sub("https://", "", link)
                    self.clean_errors_df.loc[len(self.clean_errors_df.index)] = [
                        link,
                        error,
                        "odysee",
                    ]
                    self.odysee_garbage.append(re.sub("https://", "", link))
            elif re.match("odysee\.com/@", link):
                link = re.sub(":.*", "", link)
                self.sm_urls_list.append(link)
            elif re.match("bitchute\.com", link):
                try:
                    page_content = requests.get("https://" + link, headers=self.headers).content
                    link = re.findall('(?<=channel/)[-_a-zA-Z0-9]+(?=/")', str(page_content))
                    link = "bitchute.com/" + str(link[0])
                    self.sm_urls_list.append(link)
                except Exception as error:
                    self.clean_errors_df.loc[len(self.clean_errors_df.index)] = [
                        link,
                        error,
                        "bitchute",
                    ]
                    self.bitchute_garbage.append(link)
            elif re.match("vk\.com", link):
                self.vk_list.append(link) # place in a special list for later processing
            elif re.match("rumble\.com", link):
                if re.match("(rumble\.com/user/|rumble\.com/c/)", link):
                    self.sm_urls_list.append(link)
                else:
                    try:
                        page_content = requests.get("https://" + link, headers=self.headers).content
                        soup = BeautifulSoup(page_content, "html.parser")
                        if soup.find("a", class_="media-by--a").get("href") != "":
                            user_channel = soup.find("a", class_="media-by--a").get("href")
                            link = "rumble.com" + user_channel
                            self.sm_urls_list.append(link)
                        else:
                            self.rumble_garbage.append(link)
                    except Exception as error:
                        link = re.sub("https://", "", link)
                        self.clean_errors_df.loc[len(self.clean_errors_df.index)] = [
                            link,
                            error,
                            "rumble",
                        ]
                        self.rumble_garbage.append(link)
            elif re.match("gettr\.com", link):
                if re.match("gettr\.com/user/", link):
                    self.sm_urls_list.append(link)
                else:
                    try:
                        page_content = requests.get("https://" + link, headers=self.headers).content
                        soup = BeautifulSoup(page_content, "html.parser")
                        if (len(re.findall(".*(?= on GETTR)", soup.title.get_text()))!= 0):
                            user = re.findall(".*(?= on GETTR)", soup.title.get_text())[0]
                            link = "gettr.com/user/" + user
                            self.sm_urls_list.append(link)
                        else:
                            self.gettr_garbage.append(link)
                    except Exception as error:
                        link = re.sub("https://", "", link)
                        self.clean_errors_df.loc[len(self.clean_errors_df.index)] = [
                            link,
                            error,
                            "gettr",
                        ]
                        self.gettr_garbage.append(link)
            elif re.match("(vm\.tiktok|m\.tiktok|tiktok)", link):
                if re.match("(vm\.|m\.)", link):
                    link = requests.head("https://" + link, allow_redirects=True).url
                    link = re.sub("https://www\.", "", link)
                    link = re.sub("/video.*", "", link)
                    if link != "tiktok.com/":
                        self.sm_urls_list.append(link)
                    else:
                        self.tiktok_garbage.append(link)
                elif link.startswith("tiktok.com/@"):
                    link = re.sub("\?.*", "", link)
                    self.sm_urls_list.append(link)
                else:
                    self.tiktok_garbage.append(link)
            else:
                self.sm_other_urls_list.append(re.sub("/$", "", link))

        self.sm_other_urls_list = [re.sub("\?.*", "", i) for i in self.sm_other_urls_list]
        self.sm_urls_list = self.sm_urls_list + self.sm_other_urls_list

        # format yt_watch links
        self.yt_watch_garbage = []
        for link in self.youtube_watch_list:
            try:
                page = requests.get("https://" + link, headers=self.headers)
                page_content = page.content
                soup = BeautifulSoup(page_content, "html.parser")
                content = soup.find("span", attrs={"itemprop": "author"})
                if content.find("link", attrs={"href": re.compile("https?://")}) != "":
                    link = content.find("link", attrs={"href": re.compile("https?://")})
                    link = re.sub("https?://(www\.)?", "", link.get("href"))
                    self.sm_urls_list.append(link)
                else:
                    self.yt_watch_garbage.append(link)
            except Exception as error:
                self.clean_errors_df.loc[len(self.clean_errors_df.index)] = [
                    link,
                    error,
                    "youtube_watch",
                ]
                self.yt_watch_garbage.append(link)

        # format fb_watch links
        self.fb_watch_garbage = []
        for link in self.fb_watch_list:
            try:
                page = requests.get("https://" + link, headers=self.headers)
                page_content = page.content
                soup = BeautifulSoup(page_content, "html.parser")
                content = soup.find("link", attrs={"hreflang": "x-default"})
                if content.get("href") != "":
                    link = content.get("href")
                    link = re.sub("https?://(www\.)?", "", link)
                    link = re.sub("/videos.*", "", link)
                    self.sm_urls_list.append(link)
                else:
                    self.fb_watch_garbage.append(re.sub("https://", "", link))
            except Exception as error:
                link = re.sub("https://", "", link)
                self.clean_errors_df.loc[len(self.clean_errors_df.index)] = [
                    link,
                    error,
                    "fb_watch",
                ]
                self.fb_watch_garbage.append(link)

        # format vk links
        self.vk_garbage = []
        for link in self.vk_list:
            try:
                if re.search("vk\.com/video/@", link):
                    link = re.sub("/video/@", "/", link)
                    link = re.sub("\?.*", "", link)
                    self.sm_urls_list.append(link)
                elif re.search("vk\.com/video", link):
                    page_content = requests.get("https://" + link).content
                    soup = BeautifulSoup(page_content, "html.parser")
                    href_list = soup.find_all("a")
                    if str(href_list[3].get("href")) != "":
                        link = "vk.com" + str(href_list[3].get("href"))
                        self.sm_urls_list.append(link)
                    else:
                        self.vk_garbage.append(link)
                elif re.search("vk\.com/wall", link):
                    page_content = requests.get("https://" + link).content
                    soup = BeautifulSoup(page_content, "html.parser")
                    soup_find = soup.find("a").get("href")
                    link = "vk.com" + soup_find
                    self.sm_urls_list.append(link)
                elif re.search("vk\.com/.*\?\w(=photo|=wall)", link):
                    link = re.sub("\?.*", "", link)
                    self.sm_urls_list.append(link)
                elif re.search("vk\.com/\w+$", link):
                    page_content = requests.get("https://" + link).content
                    soup = BeautifulSoup(page_content, "html.parser")
                    soup_find = soup.find("link", attrs={"rel": "canonical"})
                    if re.findall("vk\.com/[-_a-zA-Z0-9]+", str(soup_find))[0] != "":
                        link = re.findall("vk\.com/[-_a-zA-Z0-9]+", str(soup_find))[0]
                        self.sm_urls_list.append(link)
                    else:
                        self.vk_garbage.append(link)
                elif re.search("vk\.com/[\w\.]+$", link):
                    sm_urls_list.append(link)
                else:
                    self.vk_garbage.append(link)
            except Exception as error:
                self.clean_errors_df.loc[len(self.clean_errors_df.index)] = [
                    link,
                    error,
                    "vk",
                ]
                self.vk_garbage.append(link)

        # compile and sort final links list
        self.formatted_links = self.sm_urls_list + self.non_sm_urls_list
        self.formatted_links = [i.lower() for i in self.formatted_links]
        self.formatted_links = [re.sub("^www\.", "", i) for i in self.formatted_links]
        self.formatted_links.sort()

        # compile garbage and print garbage stats
        self.final_sm_garbage = (
            self.facebook_garbage
            + self.ig_garbage
            + self.yt_watch_garbage
            + self.vk_garbage
            + self.fb_watch_garbage
            + self.youtube_garbage
            + self.bitchute_garbage
            + self.odysee_garbage
            + self.rumble_garbage
            + self.gettr_garbage
            + self.twitter_garbage
            + self.tiktok_garbage
        )

        """ final_overall_garbage will tell us how many lines were put in a garbage
        list while converting raw_links to formatted_links. We want this to equal final_difference. """
        if self.unshorten_executed is True:
            self.final_overall_garbage = len(
                self.final_sm_garbage
                + self.non_url_garbage
                + self.shortened_urls_garbage
                + self.mail_garbage
            )
        else:
            self.final_overall_garbage = len(
                self.final_sm_garbage
                + self.non_url_garbage
                + self.shortened_urls_list
                + self.mail_garbage
            )

        """ final_difference will tell us how many lines were discarded in the process
        of converting raw_links to formatted_links """
        self.final_difference = len(self.raw_links) - len(self.formatted_links)

        """ garbage_less_difference will tell us how many of the lines that were discarded
        in the process of converting raw_links to  formatted_links are unaccounted for
        by final_overall_garbage. We want this to equal zero. """
        self.garbage_less_difference = (self.final_overall_garbage - self.final_difference)

        self.garbage_df = pd.DataFrame(
            {
                "type": [
                    "non_url_garbage",
                    "facebook",
                    "instagram",
                    "youtube",
                    "yt_watch",
                    "fb_watch",
                    "vkontakte",
                    "bitchute",
                    "odysee",
                    "rumble",
                    "gettr",
                    "tiktok",
                    "shortened_urls",
                ],
                "count": [
                    len(self.non_url_garbage),
                    len(self.facebook_garbage),
                    len(self.ig_garbage),
                    len(self.youtube_garbage),
                    len(self.yt_watch_garbage),
                    len(self.fb_watch_garbage),
                    len(self.vk_garbage),
                    len(self.bitchute_garbage),
                    len(self.odysee_garbage),
                    len(self.rumble_garbage),
                    len(self.gettr_garbage),
                    len(self.tiktok_garbage),
                    len(self.shortened_urls_garbage),
                ],
            }
        )

        self.garbage_df = self.garbage_df.sort_values("count", ascending=False)

        print(
            f"\n\n{len(self.formatted_links)} URLs in total were successfully cleaned."
            + "\n\n"
            + f"{self.garbage_less_difference} URLs were lost and are unaccounted for by final_overall_garbage."
            + "\n\n"
            + f"{len(self.final_sm_garbage)} URLs are included in final_sm_garbage, which is "
            + f"{round((len(self.final_sm_garbage) / len(self.formatted_links + self.final_sm_garbage))*100, 2)}% of "
            + f"formatted_links + final_sm_garbage."
            + "\n\n"
            + f"{self.final_difference} lines in total were discarded in the cleaning process, "
            + f"of which {len(self.non_url_garbage)} were non-URLs."
            + "\n\n"
            + f"{len(self.clean_errors_df)} errors were produced in the cleaning process."
        )

        if self.unshorten_executed is False:
            print(
                f"\n{len(self.shortened_urls_list)} shortened_urls were identified, which were \
not unshortened owing to formatter.unshorten() not having been executed."
            )

        print("\nThe number of lines included in each garbage bin are:\n\n {0}\n".format(
                self.garbage_df.to_string(index=False)))

        self.clean_executed = True

        self.joined_errors_df = self.unshorten_errors_df._append(self.clean_errors_df, ignore_index=True)

        return self.formatted_links


if __name__ == "__main__":

    def main():
        help_menu = "\nBulk URL Formatter converts URLs to a format that is analytically useful. \
\nFor detailed information on usage and additional features see the README.\
        \n\nUsage: python3 url_formatter.py [OPTIONS]\
        \n\nOptions:\n\t--help/-h: display this help menu\n\t--unshorten/-u: unshorten shortened URLs\
        \n\t--clean/-c: clean URLs\n"

        argv = sys.argv[1:]
        try:
            opts, args = getopt.getopt(argv, "uch", ["unshorten", "clean", "help"])

            u = False
            c = False
            h = False
            for opt, arg in opts:
                if opt in ["-u", "--unshorten"]:
                    u = True
                if opt in ["-c", "--clean"]:
                    c = True
                if opt in ["-h", "--help"]:
                    h = True

            if h is True:
                print(help_menu)
            else:
                raw_links = []
                raw_links_path = input("\nPlease enter path to raw links file: ")
                identifier = input(
                    "\nPlease enter an identifier for the output filename: "
                )

                with open(raw_links_path, "r") as file:
                    lines = file.readlines()
                    for line in lines:
                        raw_links.append(line.replace("\n", ""))
                # if options u and c are provided, first run unshorten() and then clean()
                if u is True and c is True:
                    formatter_obj = formatter(raw_links)
                    formatter_obj.unshorten()
                    cleaned_links = formatter_obj.clean()
                    with open(identifier + "_cleaned_unshortened_links.txt", "w") as file:
                        for link in cleaned_links:
                            file.write(link + "\n")
                elif u is True:
                    formatter_obj = formatter(raw_links)
                    expanded_links = formatter_obj.unshorten()
                    with open(identifier + "_unshortened_links.txt", "w") as file:
                        for link in expanded_links:
                            file.write(link + "\n")
                elif c is True:
                    formatter_obj = formatter(raw_links)
                    cleaned_links = formatter_obj.clean()
                    with open(identifier + "_cleaned_links.txt", "w") as file:
                        for link in cleaned_links:
                            file.write(link + "\n")
        except Exception as error:
            print(error)

    main()
