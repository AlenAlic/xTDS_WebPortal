from flask import render_template, url_for, redirect
from flask_login import login_required
from ntds_webportal.news import bp
from ntds_webportal.models import News
from sqlalchemy import desc


@bp.route('/news_items', methods=['GET'])
@login_required
def news_items():
    items = News.query.order_by(desc(News.timestamp)).all()
    return render_template('news/news_items.html', items=items)


@bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    items = News.query.order_by(News.timestamp).all()
    return render_template('news/create.html', items=items)


@bp.route('/update/<int:news_id>', methods=['GET', 'POST'])
@login_required
def update(news_id):
    return render_template('news/update.html')


@bp.route('/delete/<int:news_id>', methods=['DELETE'])
@login_required
def delete(news_id):
    return redirect(url_for('news.items'))
