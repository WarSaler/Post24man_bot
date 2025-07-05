from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime

from ..config import config

Base = declarative_base()

class NewsArticle(Base):
    __tablename__ = "news_articles"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    source_group = Column(String(255), nullable=False)
    source_message_id = Column(Integer, nullable=True)
    original_content = Column(Text, nullable=False)
    processed_content = Column(Text, nullable=True)
    is_approved = Column(Boolean, default=False)
    is_posted = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    posted_at = Column(DateTime, nullable=True)
    
    def __repr__(self):
        return f"<NewsArticle(id={self.id}, source={self.source_group}, approved={self.is_approved}, posted={self.is_posted})>"


class DBHelper:
    def __init__(self):
        self.engine = create_engine(config.DATABASE_URL)
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
        
    def add_news_article(self, source_group, original_content, source_message_id=None):
        session = self.Session()
        article = NewsArticle(
            source_group=source_group,
            source_message_id=source_message_id,
            original_content=original_content
        )
        session.add(article)
        session.commit()
        article_id = article.id
        session.close()
        return article_id
    
    def update_processed_content(self, article_id, processed_content):
        session = self.Session()
        article = session.query(NewsArticle).filter(NewsArticle.id == article_id).first()
        if article:
            article.processed_content = processed_content
            session.commit()
            success = True
        else:
            success = False
        session.close()
        return success
    
    def approve_article(self, article_id):
        session = self.Session()
        article = session.query(NewsArticle).filter(NewsArticle.id == article_id).first()
        if article:
            article.is_approved = True
            session.commit()
            success = True
        else:
            success = False
        session.close()
        return success
    
    def mark_as_posted(self, article_id):
        session = self.Session()
        article = session.query(NewsArticle).filter(NewsArticle.id == article_id).first()
        if article:
            article.is_posted = True
            article.posted_at = datetime.utcnow()
            session.commit()
            success = True
        else:
            success = False
        session.close()
        return success
    
    def get_pending_articles(self, limit=10):
        session = self.Session()
        articles = session.query(NewsArticle).filter(
            NewsArticle.is_approved == False,
            NewsArticle.processed_content != None
        ).order_by(NewsArticle.created_at.desc()).limit(limit).all()
        result = [(article.id, article.source_group, article.original_content, article.processed_content) 
                 for article in articles]
        session.close()
        return result
        
    def get_approved_not_posted_articles(self, limit=5):
        session = self.Session()
        articles = session.query(NewsArticle).filter(
            NewsArticle.is_approved == True,
            NewsArticle.is_posted == False
        ).order_by(NewsArticle.created_at.asc()).limit(limit).all()
        result = [(article.id, article.processed_content) for article in articles]
        session.close()
        return result
        
    def get_article_by_id(self, article_id):
        session = self.Session()
        article = session.query(NewsArticle).filter(NewsArticle.id == article_id).first()
        result = None
        if article:
            result = {
                "id": article.id,
                "source_group": article.source_group,
                "original_content": article.original_content,
                "processed_content": article.processed_content,
                "is_approved": article.is_approved,
                "is_posted": article.is_posted,
                "created_at": article.created_at
            }
        session.close()
        return result

# Создание экземпляра помощника базы данных
db = DBHelper() 