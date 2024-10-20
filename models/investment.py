from . import db
from flask_login import current_user

class Investment(db.Model):
    __tablename__ = 'investments'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    investment_type = db.Column(db.String(50), nullable=False)  # This stores stock symbol like "AAPL"
    amount_invested = db.Column(db.Float, nullable=False)
    current_value = db.Column(db.Float, nullable=True)
    date_invested = db.Column(db.DateTime, default=db.func.current_timestamp())
    
    def to_dict(self):
        return {
            'id': self.id,
            'investment_type': self.investment_type,  # Stock symbol saved here
            'amount_invested': self.amount_invested,
            'current_value': self.current_value,
            'date_invested': self.date_invested,
            'user_id': self.user_id
        }
