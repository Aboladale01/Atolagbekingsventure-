from flask import Blueprint, request, jsonify
from models.database import db, Subscriber, AffiliateClick, NewsUpdate
from datetime import datetime

api_bp = Blueprint('api', __name__, url_prefix='/api')

@api_bp.route('/subscribe', methods=['POST'])
def subscribe():
    """Subscribe to newsletter"""
    data = request.get_json()
    email = data.get('email')
    name = data.get('name', '')
    
    if not email:
        return jsonify({'error': 'Email is required'}), 400
    
    # Check if subscriber already exists
    existing = Subscriber.query.filter_by(email=email).first()
    if existing:
        return jsonify({'error': 'Email already subscribed'}), 409
    
    subscriber = Subscriber(email=email, name=name)
    db.session.add(subscriber)
    db.session.commit()
    
    return jsonify({
        'id': subscriber.id,
        'email': subscriber.email,
        'name': subscriber.name,
        'subscribed_at': subscriber.subscribed_at.isoformat()
    }), 201

@api_bp.route('/subscribers', methods=['GET'])
def get_subscribers():
    """Get all active subscribers"""
    subscribers = Subscriber.query.filter_by(is_active=True).all()
    return jsonify([{
        'id': sub.id,
        'email': sub.email,
        'name': sub.name,
        'subscribed_at': sub.subscribed_at.isoformat()
    } for sub in subscribers])

@api_bp.route('/affiliate/click', methods=['POST'])
def track_affiliate_click():
    """Track affiliate link clicks"""
    data = request.get_json()
    affiliate_id = data.get('affiliate_id')
    link = data.get('link')
    
    if not affiliate_id or not link:
        return jsonify({'error': 'affiliate_id and link are required'}), 400
    
    click = AffiliateClick(
        affiliate_id=affiliate_id,
        link=link,
        ip_address=request.remote_addr,
        user_agent=request.headers.get('User-Agent')
    )
    
    db.session.add(click)
    db.session.commit()
    
    return jsonify({
        'id': click.id,
        'affiliate_id': click.affiliate_id,
        'clicked_at': click.clicked_at.isoformat()
    }), 201

@api_bp.route('/affiliate/stats/<affiliate_id>', methods=['GET'])
def get_affiliate_stats(affiliate_id):
    """Get affiliate statistics"""
    clicks = AffiliateClick.query.filter_by(affiliate_id=affiliate_id).all()
    total_clicks = len(clicks)
    
    return jsonify({
        'affiliate_id': affiliate_id,
        'total_clicks': total_clicks,
        'clicks': [{
            'id': click.id,
            'link': click.link,
            'clicked_at': click.clicked_at.isoformat()
        } for click in clicks]
    })

@api_bp.route('/news', methods=['GET'])
def get_news():
    """Get all active news updates"""
    news = NewsUpdate.query.filter_by(is_active=True).order_by(NewsUpdate.created_at.desc()).all()
    return jsonify([{
        'id': n.id,
        'title': n.title,
        'content': n.content,
        'created_at': n.created_at.isoformat()
    } for n in news])

@api_bp.route('/news', methods=['POST'])
def create_news():
    """Create a new news update"""
    data = request.get_json()
    title = data.get('title')
    content = data.get('content', '')
    
    if not title:
        return jsonify({'error': 'Title is required'}), 400
    
    news = NewsUpdate(title=title, content=content)
    db.session.add(news)
    db.session.commit()
    
    return jsonify({
        'id': news.id,
        'title': news.title,
        'content': news.content,
        'created_at': news.created_at.isoformat()
    }), 201

@api_bp.route('/news/<int:news_id>', methods=['DELETE'])
def delete_news(news_id):
    """Deactivate a news update"""
    news = NewsUpdate.query.get(news_id)
    
    if not news:
        return jsonify({'error': 'News not found'}), 404
    
    news.is_active = False
    db.session.commit()
    
    return jsonify({'message': 'News deleted successfully'}), 200
