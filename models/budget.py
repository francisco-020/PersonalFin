from . import db

class Budget(db.Model):
    __tablename__ = 'budgets' # Explicitly name the table
    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(50), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    date = db.Column(db.DateTime, default=db.func.current_timestamp())

    def to_dict(self):
        return{
            "id": self.id,
            "category": self.category,
            "amount": self.amount,
            "date": self.date.strftime('%Y-%m-%d %H: %M: %S')
        }