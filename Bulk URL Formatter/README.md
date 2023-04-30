# Bulk URL Formatter
Bulk URL Formatter is intended to solve the problem of converting a list of URLs into a format that is analytically useful. As examples, it will: 
1) Convert a link to a specific post on a social media platform to the URL for the poster's profile.
2) Convert short URLs to the URLs that they shorten.
3) Remove subdirectories from URLs, leaving only domains.

When necessary, the tool extracts required information from the the source code of webpages.

It should be noted that as this tool was created for cleaning links scraped from Telegram chats, the non-link filter will not discard non-links that are not typical of Telegram link scrapes. This can be made to suit your needs by modifying the REGEX on line 132, as seen below:

<img width="488" alt="Screenshot 2023-04-28 at 1 09 20 AM" src="https://user-images.githubusercontent.com/110642777/235059465-9a4b6f35-60e4-434f-8c87-424918cf3862.png">


# Usage
This tool can either be run from the command line as a script, or imported as a module. 

To run it as a script simply type 'python3 url_formatter.py' along with the desired options and when prompted provided the full path to the .txt file containing newline-separated URLs as well as the identifier that you'd like to use for ouput file-naming purposes. The options are as follows:

<img width="352" alt="Screenshot 2023-04-30 at 1 20 42 AM" src="https://user-images.githubusercontent.com/110642777/235337006-2250052b-9e1d-40b9-86a9-07120316ee29.png">


The -c/-clean option will run the program's clean() method, which does the work of cleaning URLs. The -u/--unshorten option runs the unshorten() method, which unshortens URLs. Both will output their results to a text file located in the directory that the script is executed from. Both options can ge run together, in which case the script will first run the unshorten() method and then the clean() method.

To use the tool as a module, first create a url_formatter object by typing "example_name = url_formatter.formatter(SOME_LIST)", where SOME_LIST is a list containing the unformatted/unshortened URLs that you would like to convert. As noted, Bulk URL Formatter has two methods, unshorten() and clean(). After creating a url_formatter object executing a method is as simple as typing either "example_name.unshorten()" or "example_name.clean()". These methods will return a list containing the unshortened or cleaned links.

# Built-In Integrity Check and Troubleshooting Features 

Attributes that may be of interest to the user include: 

1) known_shorteners: contains the list of shorteners used to filter for shortened URLs
2) clean_errors_df: pandas dataframe containing errors and associated URLs produced while executing the clean() method
3) unshorten_errors_df: pandas dataframe containing errors and associated URLs produced while executing the unshorten() method
4) joined_errors_df: pandas dataframe combining clean_errors_df and unshorten_urls_df
5) garbage_df: pandas dataframe containing counts for the number of lines that were discarded owing to an error, a failure of the program to extract target information from source code, or to their not being URLs. These are broken down by platform.

The platform-specific garbage bins are as follows:

<img width="301" alt="Screenshot 2023-04-30 at 1 52 28 AM" src="https://user-images.githubusercontent.com/110642777/235337988-aab41480-daa6-40a3-ad2a-e075f7891c8c.png">


In addition, the clean() method will print metrics for URL processing, which include: 

1) The total number of URLs that were successfully converted.
2) The total number of lines that were could either not be converted into a useful format or were not links and were consequently discarded.
3) Discarded social media links as a percentage of total links (including succesfully converted links and links that could not be converted).
4) The total number of shortened URLs that could not be unshortened.
5) A breakdown of discarded social media links by platform.

The image below provides an example of these metrics:

<img width="765" alt="Screenshot 2023-04-30 at 1 23 37 AM" src="https://user-images.githubusercontent.com/110642777/235337120-c0810c42-a22b-438c-b32e-d01a523ff2c2.png">

The unshorten() method will indicate how many shortened URLs were detected, and how many were successfully unshortened:

<img width="594" alt="Screenshot 2023-04-30 at 1 55 23 AM" src="https://user-images.githubusercontent.com/110642777/235338107-2600410c-adc0-4ca1-bd0b-36437672f4d9.png">


These metrics allow the user to better assess the integrity of the final results. 

