from src.services.telegram import TelegramNotifier
from src.loaders.account_loader import load_accounts
from src.loaders.keywork_loader import load_keywords_for_account


from src.db.database_manager import DatabaseManager
from src.crawlers.crawler import CrawlerMainLoop


def main():
    db = DatabaseManager("output/upwork.db")
    db.initialize()
    accounts = load_accounts()
    
    for account in accounts:
        keyworks = load_keywords_for_account(account['account_id'])
        account['keywords'] = keyworks

    crawler = CrawlerMainLoop(account=accounts[0], db_manager=db)

    try:
        crawler.crawling_loop()
    finally:
        db.close()

if __name__ == "__main__":
    main()