# Bulk URL Formatter
Bulk URL Formatter is intended to solve the problem of converting a list of URLs into a format that is analytically useful. The research project that it was developed for can be found at: https://irregularhorizons.substack.com/p/the-dugin-international. As examples, it will: 
1) Convert a link to a specific post on a social media platform to the URL for the poster's profile.
2) Convert short URLs to the URLs that they shorten.
3) Remove subdirectories from URLs, leaving only domains.

Here is an example of an input file:

<img width="344" alt="raw" src="https://user-images.githubusercontent.com/110642777/235369260-46e94233-f8ee-4f81-97ec-f760d1a0a1d0.png">

...and here is an example of an output file:

<img width="309" alt="cleaned" src="https://user-images.githubusercontent.com/110642777/235369277-19f19d6c-85ea-4bfb-8190-21995620d4f1.png">


When necessary, the tool extracts required information from the source code of webpages.

It should be noted that as this tool was created for cleaning links scraped from Telegram chats, the non-URL filter will not discard non-URLs that are not typical of Telegram link scrapes. This can be made to suit your needs by modifying the REGEX on line 132, as seen below:

<img width="488" alt="Screenshot 2023-04-28 at 1 09 20 AM" src="https://user-images.githubusercontent.com/110642777/235059465-9a4b6f35-60e4-434f-8c87-424918cf3862.png">

If you prefer to use this tool as a Jupyter Notebook you can find that at: https://github.com/agile-enigma/Blog-Research-Projects/blob/main/The%20Dugin%20International/format%2Banalyze_links_GitHub.ipynb

# Usage
This tool can either be run from the command line as a script, or imported as a module. 

To run it from the command line simply type "python3 url_formatter.py" along with the desired options and when prompted provided the full path to the .txt file containing newline-separated URLs as well as the identifier that you'd like to use for ouput file-naming purposes. The options are as follows:

<img width="352" alt="Screenshot 2023-04-30 at 1 20 42 AM" src="https://user-images.githubusercontent.com/110642777/235337006-2250052b-9e1d-40b9-86a9-07120316ee29.png">


The -u/--unshorten option runs the unshorten() method, which unshortens URLs. The -c/--clean option will run the program's clean() method, which does the work of cleaning URLs. Both command line options will output their results to a text file located in the directory that the script is executed from. These options can be run together, in which case the script will first run the unshorten() method and then the clean() method.

To use the tool as a module, first create a formatter object by typing "example_name = url_formatter.formatter(SOME_LIST)", where SOME_LIST is a list containing the unformatted/unshortened URLs that you would like to convert. As noted, Bulk URL Formatter has two methods, unshorten() and clean(). 

After creating a url_formatter object executing a method is as simple as typing either "example_name.unshorten()" or "example_name.clean()". The unshorten() method will return a list containing both URLs that weren't originally shortened as well as URLS that it unshortened. The clean() method will return a list containing cleaned URLs. If the unshorten() method wasn't previously executed, clean() will discard shortened URLs. If unshorten() was previously executed, unshortened URLs will be included in the list processed by clean().

If your list contains shortened URLs, it is advised that you run the unshorten() method first.

# Built-in Integrity Check and Troubleshooting Features 

Bulk URL Formatter contains features that enable users to assess the integrity of results and troubleshoot any issues that might arise.

Attributes that may be of interest to the user include: 

1) known_shorteners: contains the list of shorteners used to filter for shortened URLs
2) clean_errors_df: pandas dataframe containing error messages and associated URLs produced while executing the clean() method
3) unshorten_errors_df: pandas dataframe containing error messages and associated URLs produced while executing the unshorten() method
4) joined_errors_df: pandas dataframe combining clean_errors_df and unshorten_errors_df
5) garbage_df: pandas dataframe containing counts for the number of lines that were discarded owing to an error, a failure of the program to extract target information from source code, or to their not being URLs. This data frame aggregates the garbage bins listed below.

The platform-specific garbage bins are as follows:


<img width="289" alt="Screenshot 2023-05-10 at 12 09 53 AM" src="https://github.com/agile-enigma/Digital-Media-Analysis-Tools/assets/110642777/1806e425-51de-4be5-84cc-835416b8c943">


In addition, the clean() method will print metrics for URL processing, which include: 

1) The total number of URLs that were successfully cleaned.
2) The total number of lines that could either not be converted into a useful format or were not links and were consequently discarded.
3) Discarded social media URLs as a percentage of total links (including succesfully converted URLs and URLs that could not be cleaned).
4) A breakdown of discarded social media URLs by platform.
5) The total number of shortened URLs that could not be unshortened.

The image below provides an example of these metrics:


<img width="937" alt="Screenshot 2023-05-10 at 12 10 43 AM" src="https://github.com/agile-enigma/Digital-Media-Analysis-Tools/assets/110642777/76b3aab9-a10b-4c18-b775-7c7a92fcbb94">

The unshorten() method will indicate how many shortened URLs were detected, and how many were successfully unshortened:

<img width="594" alt="Screenshot 2023-04-30 at 1 55 23 AM" src="https://user-images.githubusercontent.com/110642777/235338107-2600410c-adc0-4ca1-bd0b-36437672f4d9.png">
 

