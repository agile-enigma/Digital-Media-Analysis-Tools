# Bulk URL Formatter
Bulk URL Formatter is intended to solve the problem of converting a list of URLs into a format that is analytically useful. As examples, it will: 
1) Convert a link to a specific post on a social media platform to the URL for the poster's account.
2) Convert short URLs to the URLs that they shorten.
3) Remove subdirectories from URLs, leaving only the domain.


It should be noted that as this tool was created for cleaning links scraped from Telegram chats, the non-link filter will not discard non-links that are not typical of Telegram link scrapes. This can be made to suit your needs by modifying the REGEX on line 94, as seen below:

<img width="488" alt="Screenshot 2023-04-28 at 1 09 20 AM" src="https://user-images.githubusercontent.com/110642777/235059465-9a4b6f35-60e4-434f-8c87-424918cf3862.png">


# Usage
This tool can either be run from the command line as a script, or imported as a module. 

To run it as a script simply type 'python3 url_formatter.py' and when prompted provided the full path to the .txt file containing newline-separated URLs as well as the identifier that you'd like to use for ouput file-naming purposes.

To access the tool's .clean() function as a module type 'formatted_links = url_formatter.formatter(SOME_LIST).clean()' after importing it, where SOME_LIST is a list containing the unformatted URLs that you would like to format. This will return another list consisting of the formatted links.

In addition, this tool will print metrics for the conversion, which include: 

1) The total number of URLs that were successfully converted.
2) The total number of lines that were could either not be converted into a useful format or were not links and were consequently discarded.
3) Discarded social media links as a percentage of total links (including succesfully converted links and links that could not be converted).
4) The total number of shortened URLs that could not be unshortened.
5) A breakdown of discarded social media links by platform.


These metrics allow the user to better assess the confidence that should be attached to the integrity of the final results. The image below is an example of these metrics:

<img width="999" alt="Screenshot 2023-04-28 at 1 01 55 AM" src="https://user-images.githubusercontent.com/110642777/235058409-150d9a16-5edc-4f19-a9d2-4cc62cb38762.png">

