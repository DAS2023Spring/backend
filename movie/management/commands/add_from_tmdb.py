import re

import cssutils
import requests
from bs4 import BeautifulSoup
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.management import BaseCommand

from movie.models import Movie


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument(
            "url",
        )

    def handle(self, *args, **options):
        url = options["url"]
        response = requests.get(
            url, headers={
                "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/113.0",
            }
        )
        html = response.text
        soup = BeautifulSoup(html, "html.parser")
        name, release_date = self.get_name_and_release_date(soup)
        header_image = self.get_header_image(soup)
        logo_image = self.get_logo_image(soup)
        overview = self.get_overview(soup)
        director = self.get_director(soup)
        Movie.objects.create(
            name=name.strip(),
            director=director.strip(),
            created_year=release_date.strip(),
            length_minutes=self.get_length_minutes(soup),
            imdb_rating=self.get_rating(soup),
            logo=SimpleUploadedFile("img.jpg", logo_image),
            header_image=SimpleUploadedFile("header.jpg", header_image),
            story=overview.strip(),
        )

    def get_name_and_release_date(self, soup: BeautifulSoup):
        release_date_span = soup.find("span", class_="release_date")
        release_date = release_date_span.text.strip("()")
        name = release_date_span.previous_sibling.previous_sibling.text
        return name, release_date

    def get_header_image(self, soup: BeautifulSoup):
        rules = cssutils.CSSParser().parseString(soup.find("style").prettify()).cssRules
        for rule in rules:
            if hasattr(rule, "selectorText") and rule.selectorText == "div.header.large.first":
                url = "https://www.themoviedb.org" + rule.style.backgroundImage.split("(", 1)[1].rstrip(")")
                return self.download_image(url)
        raise Exception

    def get_logo_image(self, soup: BeautifulSoup):
        url = soup.find("img", class_="poster").get_attribute_list("data-src")[0]
        url = "https://www.themoviedb.org" + url
        return self.download_image(url)

    def get_overview(self, soup: BeautifulSoup):
        return soup.find("div", class_="overview").findChild("p").text

    def get_director(self, soup: BeautifulSoup):
        for el in soup.find_all("p", class_="character"):
            if "director" in el.text.lower():
                return el.find_previous("a").text

    def get_length_minutes(self, soup: BeautifulSoup):
        t = soup.find("span", class_="runtime").text.strip()
        h, m = re.fullmatch("(\d+)h ?(\d+)?m?", t).groups()
        m = m or 0
        return int(h) * 60 + int(m)

    def get_rating(self, soup: BeautifulSoup):
        return int(soup.find("div", class_="percent").find("span").attrs["class"][-1].split("-")[-1][1:])

    def download_image(self, url):
        response = requests.get(
            url, headers={
                "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/113.0",
            }
        )
        return response.content
