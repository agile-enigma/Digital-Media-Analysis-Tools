import os, csv, re, requests, pandas as pd, urlexpander
from bs4 import BeautifulSoup
import warnings
warnings.filterwarnings('ignore')


class formatter:
    def __init__(self, raw_links):
        self.raw_links = raw_links

    def clean(self):
        self.headers = {"user-agent" : "Mozilla/5.0 (Windows NT 10.0; Win64; x64)\
        AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.5615.121 Safari/537.36"}

        self.not_shortened_links = []
        self.expanded_urls_list = []
        self.shortened_urls_garbage = []

        #known_shorteners contains a list of url shorteners that will
        #be used to extract shortened URLs from raw_links
        self.known_shorteners = urlexpander.constants.all_short_domains.copy()
        self.known_shorteners += ['youtu.be', 'shorturl.me']

        #produce a list containing only shortened URLs
        self.shortened_urls_list = [link for link in self.raw_links if urlexpander.is_short(link, list_of_domains=self.known_shorteners)]

        #errors_df is a pandas dataframe containing error messages
        self.errors_df = pd.DataFrame({'url': [],
                                  'error_message': [],
                                  'platform': []})

        #produce a list consisting of expanded URLs
        # expanded_urls_list = urlexpander.expand(shortened_urls_list[:50])
        def unshorten_url(url):
            if not re.match('https?://', url):
                url = 'https://' + url
            session = requests.Session()  # so connections are recycled
            try:
                resp = session.head(url, allow_redirects=True)
                unshortened_url = re.sub('https?://(www\.)?', '', resp.url)
                self.expanded_urls_list.append(unshortened_url)
            except Exception as error:
                print(error)
                print(url)
                if len(re.findall("(?<=host=').*(?=', port)", str(error))) != 0:
                    unshortened_url = re.findall("(?<=host=').*(?=', port)", str(error))
                    unshortened_url = re.sub('https?://(www\.)?', '', unshortened_url[0])
                    self.expanded_urls_list.append(unshortened_url)
                else:
                    self.shortened_urls_garbage.append(url)
                    self.errors_df.loc[len(errors_df.index)] = [url, error, 'shortened_url']

        for url in self.shortened_urls_list:
            unshorten_url(url)

        #substract shortened URLs from raw_links to produce not_shortened_links
        for link in self.raw_links:
            if not urlexpander.is_short(link, list_of_domains=self.known_shorteners):
                self.not_shortened_links.append(link)

        #combine not_shortened_links with expanded_urls_list
        self.raw_with_expansion = self.not_shortened_links + self.expanded_urls_list
        self.raw_with_expansion = [re.sub('https?://(www\.)?', '', i) for i in self.raw_with_expansion]

        #discarded = len(self.raw_links) - len(raw_with_expansion + shortened_urls_garbage)
        #print(f'{discarded} links have been lost up to this point')

        #categorize and format social media links
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
        self.garbage = []


        self.sm_platforms_re = '^(m\.|mobile\.)?(odysee|vk\.|instagram|twitter|facebook|fb\.watch|youtube\.com|t\.me|tiktok\.|vm\.tiktok|bitchute|gettr\.com|reddit\.|rumble\.com|gab\.com|4chan\.org).*'
        self.sm_filter = re.compile(self.sm_platforms_re)
        self.sm_with_expansion = [i for i in self.raw_with_expansion if self.sm_filter.match(i)]

        for link in self.raw_with_expansion:
            if re.match('(css|photos|messages|#go_to_message|\)\[\^)', link):
                self.garbage.append(link)
            elif re.match('mailto', link):
                self.mail_garbage.append(link)
            elif link in self.sm_with_expansion:
                continue
            else:
                self.non_sm_urls_list.append(re.sub('/.*', '', link))


        self.sm_with_expansion = [re.sub('^(m\.|mobile\.)', '', i) for i in self.sm_with_expansion if not re.match('m\.tiktok\.com', i)]
        for link in self.sm_with_expansion:
            if re.match('(instagram\.com/p/|instagram\.com/tv)', link):
                self.ig_garbage.append(link)
            elif re.search('(twitter\.com/.*/status|facebook\.com/.*/posts|reddit\.com/r/.*/comments)', link):
                link = re.sub('(/status.*|/posts.*|/comments.*)', '', link)
                self.sm_urls_list.append(link)
            elif re.match('twitter\.com/hashtag', link):
                self.twitter_garbage.append(link)
            elif re.search('facebook\.com/.*/videos', link):
                link = re.sub('/videos.*', '', link)
                self.sm_urls_list.append(link)
            elif re.match('(facebook\.com/watch|fb\.watch)', link):
                self.fb_watch_list.append(link)
            elif re.match('facebook\.com/story', link):
                self.facebook_garbage.append(link)
            elif re.match('t\.me/', link):
                link = re.findall('t\.me/[-+_a-zA-Z0-9]*', link)
                self. sm_urls_list.append(link[0])
            elif re.search('youtube\.com/c/', link):
                link = re.sub('/c/', '/@', link)
                self.sm_urls_list.append(link)
            elif re.search('youtube\.com/channel', link):
                try:
                    page_content = requests.get('https://' + link, headers=headers).content
                    if len(re.findall('(?<="webCommandMetadata":{"url":"/).*(?=/featured)', str(page_content))) != 0:
                        link = re.findall('(?<="webCommandMetadata":{"url":"/).*(?=/featured)', str(page_content))
                        link = 'youtube.com/' + link[0]
        #                 print('yt channel: ' + link)
                        self.sm_urls_list.append(link)
                    else:
                        self.youtube_garbage.append(link)
                except Exception as error:
                    self.errors_df.loc[len(errors_df.index)] = [link, error, 'youtube']
        #                 print(error)
                    self.youtube_garbage.append(link)
            elif re.match('youtube\.com/results', link):
                self.youtube_garbage.append(link)
            elif re.match('(youtube\.com/watch|youtube\.com/live)', link):
                self.youtube_watch_list.append(link)
            elif re.match('odysee\.com/[^@]', link):
                try:
                    page_content = requests.get('https://' + link, headers=headers).content
                    if len(re.findall('(?<="og:url" content="https://)[\.@-_/a-zA-Z0-9]+', str(page_content))) != 0:
                        link = re.findall('(?<="og:url" content="https://)[\.@-_/a-zA-Z0-9]+', str(page_content))[0]
                        self.sm_urls_list.append(link)
                    else:
                        self.odysee_garbage.append(link)
                except Exception as error:
                    link = re.sub('https://', '', link)
                    self.errors_df.loc[len(errors_df.index)] = [link, error, 'odysee']
                    self.odysee_garbage.append(re.sub('https://', '', link))
            elif re.match('odysee\.com/@', link):
                link = re.sub(':.*', '', link)
                self.sm_urls_list.append(link)
            elif re.match('bitchute\.com', link):
                try:
                    page_content = requests.get('https://' + link, headers=headers).content
                    link = re.findall('(?<=channel/)[-_a-zA-Z0-9]+(?=/")', str(page_content))
                    link = 'bitchute.com/' + str(link[0])
                    self.sm_urls_list.append(link)
                except Exception as error:
                    self.errors_df.loc[len(errors_df.index)] = [link, error, 'bitchute']
                    self.bitchute_garbage.append(link)
            elif re.match('vk\.com', link):
                self.vk_list.append(link)
            elif re.match('rumble\.com', link):
                if re.match('(rumble\.com/user/|rumble\.com/c/)', link):
                    self.sm_urls_list.append(link)
                else:
                    try:
                        page_content = requests.get('https://' + link, headers=headers).content
                        soup = BeautifulSoup(page_content, 'html.parser')
                        if soup.find('a', class_='media-by--a').get('href') != '':
                            user_channel = soup.find('a', class_='media-by--a').get('href')
                            link = 'rumble.com' + user_channel
                            self.sm_urls_list.append(link)
                        else:
                            self.rumble_garbage.append(link)
                    except Exception as error:
                        link = re.sub('https://', '', link)
                        self.errors_df.loc[len(self.errors_df.index)] = [link, error, 'rumble']
                        self.rumble_garbage.append(link)
            elif re.match('gettr\.com', link):
                if re.match('gettr\.com/user/', link):
                    self.sm_urls_list.append(link)
                else:
                    try:
                        page_content = requests.get('https://' + link, headers=headers).content
                        soup = BeautifulSoup(page_content, 'html.parser')
                        if len(re.findall('.*(?= on GETTR)', soup.title.get_text())) != 0:
                            user = re.findall('.*(?= on GETTR)', soup.title.get_text())[0]
                            link = 'gettr.com/user/' + user
                            self.sm_urls_list.append(link)
                        else:
                            self.gettr_garbage.append(link)
                    except Exception as error:
                        link = re.sub('https://', '', link)
                        self.errors_df.loc[len(errors_df.index)] = [link, error, 'gettr']
                        self.gettr_garbage.append(link)
            elif re.match('(vm\.tiktok|m\.tiktok|tiktok)', link):
                if re.match('(vm\.|m\.)', link):
                    link = requests.head('https://' + link, allow_redirects=True).url
                    link = re.sub('https://www\.', '', link)
                    link = re.sub('/video.*', '', link)
                    if link != 'tiktok.com/':
                        self.sm_urls_list.append(link)
                    else:
                        self.tiktok_garbage.append(link)
                elif link.startswith('tiktok.com/@'):
                    link = re.sub('\?.*', '', link)
                    self.sm_urls_list.append(link)
                else:
                    self.tiktok_garbage.append(link)
            else:
        #             print('sm other: ' + link)
                self.sm_other_urls_list.append(re.sub('/$', '', link))


        self.sm_other_urls_list = [re.sub('\?.*', '', i) for i in self.sm_other_urls_list]
        self.sm_urls_list = self.sm_urls_list + self.sm_other_urls_list


        #format yt_watch links
        self.yt_watch_garbage = []
        for link in self.youtube_watch_list:
            try:
                page = requests.get('https://' + link, headers=headers)
                page_content = page.content
                soup = BeautifulSoup(page_content, "html.parser")
                content = soup.find('span', attrs={'itemprop': 'author'})
                if content.find('link', attrs={'href': re.compile('https?://')}) != '':
                    link = content.find('link', attrs={'href': re.compile('https?://')})
                    link = re.sub('https?://(www\.)?', '', link.get('href'))
                    self.sm_urls_list.append(link)
                else:
                    self.yt_watch_garbage.append(link)
            except Exception as error:
                self.errors_df.loc[len(self.errors_df.index)] = [link, error, 'youtube_watch']
        #         print('yt watch error: ' + str(error))
                self.yt_watch_garbage.append(link)


        #format fb_watch links
        self.fb_watch_garbage = []
        for link in self.fb_watch_list:
            link = 'https://' + link
            try:
                page = requests.get(link, headers=headers)
                page_content = page.content
                soup = BeautifulSoup(page_content, "html.parser")
                content = soup.find('link', attrs={'hreflang': 'x-default'})
                if content.get('href') != '':
                    link = content.get('href')
                    link = re.sub('https?://(www\.)?', '', link)
                    link = re.sub('/videos.*', '', link)
                    self.sm_urls_list.append(link)
                else:
                    self.fb_watch_garbage.append(re.sub('https://', '', link))
            except Exception as error:
                link = re.sub('https://', '', link)
                self.errors_df.loc[len(errors_df.index)] = [link, error, 'fb_watch']
        #         print('fb watch error: ' + str(error))
                self.fb_watch_garbage.append(link)

        #format vk links
        self.vk_garbage = []
        for link in self.vk_list:
            try:
                if re.search('vk\.com/video/@', link):
                    link = re.sub('/video/@', '/', link)
                    link = re.sub('\?.*', '', link)
                    self.sm_urls_list.append(link)
                elif re.search('vk\.com/video', link):
                    page_content = requests.get('https://' + link).content
                    soup = BeautifulSoup(page_content, 'html.parser')
                    href_list = soup.find_all('a')
                    if str(href_list[3].get('href')) != '':
                        link = 'vk.com' + str(href_list[3].get('href'))
        #                 print(link)
                        self.sm_urls_list.append(link)
                    else:
                        self.vk_garbage.append(link)
                elif re.search('vk\.com/\w+$', link):
                    page_content = requests.get('https://' + link).content
                    soup = BeautifulSoup(page_content, 'html.parser')
                    soup_find = soup.find('link', attrs={'rel': 'canonical'})
                    if re.findall('vk\.com/[-_a-zA-Z0-9]+', str(soup_find))[0] != '':
                        link = re.findall('vk\.com/[-_a-zA-Z0-9]+', str(soup_find))[0]
        #                 print(link)
                        self.sm_urls_list.append(link)
                    else:
                        self.vk_garbage.append(link)
                else:
                    self.vk_garbage.append(link)
            except Exception as error:
                self.errors_df.loc[len(errors_df.index)] = [link, error, 'vk']
                self.vk_garbage.append(link)
        #         print('error:', link)


        #compile and sort final links list
        self.formatted_links = self.sm_urls_list + self.non_sm_urls_list
        self.formatted_links = [i.lower() for i in self.formatted_links]
        self.formatted_links = [re.sub('^www\.', '', i) for i in self.formatted_links]
        self.formatted_links.sort()

        #compile garbage and print garbage stats
        self.final_sm_garbage = self.facebook_garbage + self.ig_garbage + self.yt_watch_garbage + self.vk_garbage + self.fb_watch_garbage + self.youtube_garbage + self.bitchute_garbage + self.odysee_garbage + self.rumble_garbage + self.gettr_garbage + self.twitter_garbage + self.tiktok_garbage

        #final_overall_garbage will tell us how many lines were put in a garbage
        #list while converting raw_links to formatted_links.
        #We want this to equal final_difference.
        self.final_overall_garbage = len(self.final_sm_garbage + self.garbage + self.shortened_urls_garbage + self.mail_garbage)

        #final_difference will tell us how many lines were discarded in the process
        #of converting raw_links to formatted_links
        self.final_difference = len(self.raw_links) - len(self.formatted_links)

        #garbage_less_difference will tell us how many of the lines that were discarded
        #in the process of converting raw_links to  formatted_links are unaccounted for
        #by final_overall_garbage. We want this to equal zero.
        self.garbage_less_difference = self.final_overall_garbage - self.final_difference

        self.garbage_df = pd.DataFrame({
            'type': ['garbage', 'facebook', 'instagram', 'youtube', 'yt_watch', 'fb_watch', 'vkontakte', \
                     'bitchute', 'odysee', 'rumble', 'gettr', 'tiktok', 'shortened_urls'],
            'count': [len(self.garbage), len(self.facebook_garbage), len(self.ig_garbage), len(self.youtube_garbage), len(self.yt_watch_garbage), \
                      len(self.fb_watch_garbage), len(self.vk_garbage), len(self.bitchute_garbage), len(self.odysee_garbage), len(self.rumble_garbage), \
                      len(self.gettr_garbage), len(self.tiktok_garbage), len(self.shortened_urls_garbage)]
        })

        self.garbage_df = self.garbage_df.sort_values('count', ascending=False)

        print("{0} links were successfully converted.\n\n{1} links were lost and are unaccounted for by \
final_overall_garbage.\n\n{2} URLs are included in final_sm_garbage, which is {3}% of \
formatted_links + final_sm_garbage.\n\n{4} lines in total were discarded in the process of \
converting raw_links to formatted_links, of which {5} were non-links.\n\n{6} shortened_urls \
could not be converted and were discarded".format(str(len(self.formatted_links)), str(self.garbage_less_difference),\
                                                  str(len(self.final_sm_garbage)),round((len(self.final_sm_garbage)/\
                                                                                    len(self.formatted_links + self.final_sm_garbage))*100, 2),\
                                                  str(self.final_difference), len(self.garbage), len(self.shortened_urls_garbage)))

        return self.formatted_links

if __name__ == '__main__':
    raw_links = []
    raw_links_path = input('\nPlease enter path to raw links file: ')
    identifier = input('\nPlease enter an identifier for the output file: ')

    with open(raw_links_path, 'r') as file:
        lines = file.readlines()
        for line in lines:
            raw_links.append(line.replace("\n", ""))

    formatted_links = formatter(raw_links).clean()

    with open(identifier + '_cleaned_links.txt', 'w') as file:
        for link in formatted_links:
            file.write(link + '\n')

