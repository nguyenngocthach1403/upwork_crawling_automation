from bs4 import BeautifulSoup
from src.parsers.parser import parse_upwork_time
from src.parsers.upwork_job_detail import UpworkJobDetailParser

def parse_job_from_html(html):
    """
    Extract data from jobs detail
    """
    soup = BeautifulSoup(html, "html.parser")
    print(soup)
    print(soup.find('a', attrs={'data-test': 'slider-open-in-new-window'}))

    # Lấy job_id
    job_card = soup.find(attrs={'data-ev-sublocation': "jobdetails"})

    # Get job_link
    try: 
        a_tag = soup.find('a', attrs={'data-test': 'UpLink'})
        print(f"----> {a_tag}")
    except:
        job_link = None

    # Get job_id
    try: 
        job_id = job_card.get('data-ev-opening_uid') if job_card else None
    except:
        job_id = None

    # Get job_title
    try: 
        job_title = job_card.find('h4').get_text(strip=True) if job_card else None
    except:
        job_title = None

    # Get skill list
    try:
        job_skill_list_tag = job_card.find('div[class="skills-list"]').find_all('span')
        job_skill_list = [x.get_text() for x in job_skill_list_tag if x]
    except:
        job_skill_list = []

    return {
        "job_id": job_id,
        "title": job_title,
        "job_link": job_link,
        "skill_list": job_skill_list
    }


def parse_job_list_from_html(html):
    """
    Get job_id list from search page
    
    :param html: Str
    :return: List[dict]
    """

    soup = BeautifulSoup(html, "html.parser")

    # Lấy job_id
    job_card_tags = soup.find_all('article')

    jobs = []

    for _ in job_card_tags:
        job_id = _.get('data-ev-job-uid')

        if not job_id:
            continue

        try: 
            posted_at = _.find("small", {"data-test": "job-pubilshed-date"}).get_text()
            posted_at = parse_upwork_time(posted_at)
        except:
            posted_at = None

        jobs.append({"job_id": job_id, "posted_at": posted_at})

    return jobs if len(jobs) != 0 else []





def crawl_job_detail(page):
    """
    Crawl job from detail job
    Return: dict || None
    """

    html = page.inner_html()

    # job_parser = 

    job_data = parse_job_from_html(html)

    return job_data


def crawl_jobs(page):
    """
    Crawl jobs from detail job
    Return: List[dict]
    """

    html = page.content()
    ### Lấy danh sách job_id và so sách xem job nào cần được lấy
    ## Lấy danh sách job_id
    job_id_list = parse_job_list_from_html(html)

    ## So sánh với các job trong lấy được trong database
    # Lấy danh sách dữ job đã thu thấp được từ lần gần nhất
    return job_id_list 


    

