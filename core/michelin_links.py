from __future__ import annotations

def italy_all_starred_url() -> str:
    return "https://guide.michelin.com/en/it/restaurants/all-starred"

def italy_directory_url() -> str:
    return "https://guide.michelin.com/en/it/restaurants"

def news_and_views_url() -> str:
    return "https://guide.michelin.com/en/articles/news-and-views"

def what_is_a_michelin_star_url() -> str:
    return "https://guide.michelin.com/en/article/features/what-is-a-michelin-star"

def city_search_phrase(city: str) -> str:
    return f"{city.strip()} (Italy)"
