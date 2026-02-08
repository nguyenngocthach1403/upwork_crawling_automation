class HomePageSelectors:
    """
    HomePageSelectors là lớp dùng để quản lý các selectors string trong mỗi trang nếu khi 
    trang web có cập nhật và thay đổi chỉ cần sửa ở đây
    """
    BRAND_LOGO = '[data-cy="brand"]'
    FALLBACK_LOGO = '.nav-logo'
    SEARCH_INPUT = 'input[placeholder="Search for jobs"]'
    CAROUSEL = '[data-test="carousel-slide"]'

class SearchPageSelector:
    """
    Docstring for SearchPageSelector
    """
    BRAND_LOGO = '[data-cy="brand"]'
    FALLBACK_LOGO = '.nav-logo'
    SEARCH_INPUT = 'input[placeholder="Search for jobs"]'
    CAROUSEL = '[data-test="carousel-slide"]'
    ARTICLE = 'article'
    FILTER_SELECT = '[aria-labelledby="jobs-sort-dropdown"]'