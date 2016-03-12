# WildbowCrawler

## written by J. Alex Ruble (Calamitizer)

([GitHub repository](https://github.com/Calamitizer/WildbowCrawler))

## Overview

This is a Python script that web-scrapes the serial fictions of Wildbow (J.C. McCrae) and bundles them into local `.txt` files for offline / e-reader viewing.

## Usage Guide

(Note: sysargs are not yet implemented, so this is subject to change.)

Navigate to the downloaded directory (*e*.*g*. `~/Downloads/WildbowCrawler/`) in your terminal, then input the command

```
python main.py <storyname> <formatkey> <italics> <arcsep> <chapsep>
```

with arguments

1. `<storyname>` -- This is the name of the story to be locally archived. This is case-insensitive; your files will be capitalized correctly either way. Presently, this should be one of
  * `worm`
  * `pact`
  * `twig`
2. `<formatkey>` -- This is the keyword for which file structure the results will be placed in. Select one of
  * `single` -- this will create the `<storyname>` directory, containing `<storyname>.txt` with the full text of the story.
  * `per-arc` -- this will create the `<storyname>` directory, containing one `<arcnumber>_<arcname>.txt` file for each arc (*e*.*g*. `1_Gestation.txt`).
3. `<italics>` -- This is the string that will delimit italicized text (as the output is plaintext). `*` and `_` are reasonable options; choose `none` if you insist upon no demarcation.
4. `<arcsep>` and `<chapsep>` -- These are the strings inserted at the beginning of each arc and chapter, respectively, for CTRL+F purposes. Choose `none` for the empty string.

Some example usages follow.

```
python main.py worm per-arc * [ARC] [CHAPTER]
python main.py pact single _ #A #C
python main.py twig per-arc none none Chapter:
```

## Changelog / To-Do List

To be written once a stable working release is pushed. Instead, have a to-do list!

* Finish test-running the code for necessary unicode substitutions
* Strip dumb social media snippets
* Support Pact and Twig
* Implement sysargs
* Write `Crawler.quit()`
* Figure out packaging for imported modules
* Go back in time to prevent the birth of anyone somewhat responsible for unicode

## Jolly Cooperation

Contributions to and optimizations of this (small) project are welcome if you'd like. Kindly alert me if you notice any anomalies in transcription, including disordering, jumbling, skipping and the like -- no, I am not rereading Worm to write this crawler. Also, let me know if (probably unicode-related) bugs arise upon further Twig publication.

## Implementation

This code is written in Python 2.7.3. The non-standard library modules used are `requests` (for HTML request handling) and `bs4` (for HTML parsing).

## Wildbow-Related Links

[Wildbow's personal blog](https://wildbow.wordpress.com/)  
[Worm](https://parahumans.wordpress.com/)  
[Pact](https://pactwebserial.wordpress.com/)  
[Twig](https://twigserial.wordpress.com/)  
[/r/parahumans](https://reddit.com/r/parahumans) (for discussion of all Wildbow's work)  
[Wildbow's Patreon](https://www.patreon.com/Wildbow)

In my opinion, Wildbow is a very gifted writer. Support him if Worm gets picked up for publishing!

## Author

You can reach the author (Alex Ruble) most easily via GitHub ([Calamitizer](https://github.com/calamitizer)), email ([jaruble@ncsu.edu](mailto:jaruble@ncsu.edu)), or Twitter ([@aknifeallblade](https://twitter.com/aknifeallblade)).

## License

This software has no associated copyrights whatsoever (*i*.*e*. an [unlicense](http://unlicense.org/)). See `LICENSE.txt` for the full description.
