from flask import Blueprint, render_template, request, jsonify
from models.database import db, ChatMessage, NewsUpdate

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """Home page route"""
    news_updates = NewsUpdate.query.filter_by(is_active=True).order_by(NewsUpdate.created_at.desc()).limit(5).all()
    return render_template('index.html', news_updates=news_updates)

@main_bp.route('/about')
def about():
    """About page route"""
    return render_template('about.html')

@main_bp.route('/chat', methods=['POST'])
def chat():
    """Chat endpoint"""
    data = request.get_json()
    user_message = data.get('message', '')
    
    if not user_message:
        return jsonify({'error': 'Message cannot be empty'}), 400
    
    # Create chat message record
    chat_msg = ChatMessage(
        user_message=user_message,
        bot_response='Processing your message...',
        session_id=request.headers.get('X-Session-ID')
    )
    
    db.session.add(chat_msg)
    db.session.commit()
    
    return jsonify({
        'id': chat_msg.id,
        'message': user_message,
        'response': chat_msg.bot_response
    })

@main_bp.route('/news')
def news():
    """News page route"""
    news_updates = NewsUpdate.query.filter_by(is_active=True).order_by(NewsUpdate.created_at.desc()).all()
    return render_template('news.html', news_updates=news_updates)

@main_bp.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({'status': 'healthy'}), 200
