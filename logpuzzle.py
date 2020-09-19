#!/usr/bin/env python2
"""
Log Puzzle exercise

Copyright 2010 Google Inc.
Licensed under the Apache License, Version 2.0
http://www.apache.org/licenses/LICENSE-2.0

Given an Apache logfile, find the puzzle URLs and download the images.

Here's what a puzzle URL looks like (spread out onto multiple lines):
10.254.254.28 - - [06/Aug/2007:00:13:48 -0700] "GET /~foo/puzzle-bar-aaab.jpg
HTTP/1.0" 302 528 "-" "Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US;
rv:1.8.1.6) Gecko/20070725 Firefox/2.0.0.6"
"""

__author__ = "Sarah Beverton"

import os
import re
import sys
import urllib.request
import argparse


def read_urls(filename):
    """Returns a list of the puzzle URLs from the given log file,
    extracting the hostname from the filename itself, sorting
    alphabetically in increasing order, and screening out duplicates.
    """
    puzzle_urls = []
    site_pattern = re.compile(r'_(\S+)')
    site = site_pattern.search(filename)
    site = site.group(1)
    with open(filename, 'r') as f:
        puzzle_text = f.readlines()
        pattern = re.compile(r'(\S+puzzle\S+)')
        for line in puzzle_text:
            url = pattern.search(line)
            if url:
                puzzle_urls.append(url.group(1))
    puzzle_urls = list(dict.fromkeys(puzzle_urls))

    # if it is from the place puzzle, sort by last group of chars
    place_pattern = re.compile(r'\S+puzzle\S+-\S+-(\S+)')
    for url in puzzle_urls:
        place = place_pattern.search(url)
        if place:
            puzzle_urls = sorted(puzzle_urls, key=lambda
                                 x: place_pattern.search(x).group(1))
        else:
            puzzle_urls = sorted(puzzle_urls)
    puzzle_urls = ['http://' + site + url for url in puzzle_urls]
    return puzzle_urls


def download_images(img_urls, dest_dir):
    """Given the URLs already in the correct order, downloads
    each image into the given directory.
    Gives the images local filenames img0, img1, and so on.
    Creates an index.html in the directory with an <img> tag
    to show each local image file.
    Creates the directory if necessary.
    """
    # Create the directory for the images and index
    try:
        os.mkdir(dest_dir)
    except FileExistsError as exc:
        print(exc)

    # Retrieve each image from the url and name it img[index]
    for i, url in enumerate(img_urls):
        print("Retrieving...", url)
        urllib.request.urlretrieve(url, dest_dir + '/img' + str(i))

    # Create the index.html file
    index_path = os.path.join(dest_dir, 'index.html')

    # Create string of images
    image_string = ''
    for i, url in enumerate(img_urls):
        image_string += '<img src="' + 'img' + str(i) + '">'

    # Write html file
    with open(index_path, 'w') as index_file:
        index_file.write('<html>\n<body>\n' +
                         image_string + '\n</body>\n</html>')


def create_parser():
    """Creates an argument parser object."""
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--todir',
                        help='destination directory for downloaded images')
    parser.add_argument('logfile', help='apache logfile to extract urls from')

    return parser


def main(args):
    """Parses args, scans for URLs, gets images from URLs."""
    parser = create_parser()

    if not args:
        parser.print_usage()
        sys.exit(1)

    parsed_args = parser.parse_args(args)

    img_urls = read_urls(parsed_args.logfile)

    if parsed_args.todir:
        download_images(img_urls, parsed_args.todir)
    else:
        print('\n'.join(img_urls))


if __name__ == '__main__':
    main(sys.argv[1:])
