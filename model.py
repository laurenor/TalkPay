"""Models and database functions"""

from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()


##############################################################################
# Model definitions

class User(db.Model):
    """User of the app"""

    __tablename__ = 'users'

    user_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    linkedin_id = db.Column(db.String)
    first_name = db.Column(db.String(64))
    last_name = db.Column(db.String(64))
    headline = db.Column(db.String(64))
    industry = db.Column(db.String(64))
    location = db.Column(db.String(64))
    gender = db.Column(db.String)



    # todo: need to decide if only allows for facebook login, if so, we could take out the password part
    # todo: change the datatype of user_id column to big integer

    positions = db.relationship("Position", backref=db.backref("user"), cascade="all, delete, delete-orphan")


    def __repr__(self):
        """Provide helpful representation when printed"""
        return "<User user_id=%s name=%s>" % (self.user_id, self.first_name + self.last_name)

    @classmethod
    def create(cls, linkedin_id, first_name, last_name, headline=None, industry=None, location=None, gender=None):
        new_user = cls(linkedin_id=linkedin_id, first_name=first_name, last_name=last_name, headline=headline, industry=industry, location=location, gender=gender)
        db.session.add(new_user)
        db.session.commit()
        return new_user

    def update_user_profile(self, first_name=None, last_name=None, headline=None, industry=None, location=None, gender=None):
        if first_name != self.first_name:
            self.first_name = first_name
        if last_name != self.last_name:
            self.last_name = last_name
        if headline != self.headline:
            self.headline = headline
        if industry != self.industry:
            self.industry = industry
        if location != self.location:
            self.location = location
        if gender != self.gender:
            self.gender = gender

        db.session.commit()



class Position(db.Model):
    """Positions of the app"""

    __tablename__ = 'positions'

    position_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    company = db.Column(db.String)
    start_date = db.Column(db.DATETIME)
    title = db.Column(db.String)
    salary = db.Column(db.Integer)

    def __repr__(self):
        return "<Position position_id=%s user_id=%s title=%s>" % (self.position_id, self.user_id, self.title)
    @classmethod
    def create(cls, user_id, company=None, start_date=None, title=None, salary=None):
        new_position = cls(user_id=user_id, company=company, start_date=start_date, title=title, salary=salary)
        db.session.add(new_position)
        db.session.commit()


    def update_position(self, company=None, start_date=None, title=None, salary=None):
        if company != self.company:
            self.company = company
        if start_date != self.start_date:
            self.start_date = start_date
        if title != self.title:
            self.title = title
        if salary != self.salary:
            self.salary = salary
        db.session.commit()



##############################################################################
# Helper functions

def connect_to_db(app):
    """Connect the database to app."""

    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///talkpay.db'
    db.app = app
    db.init_app(app)


if __name__ == "__main__":

    from server import app
    connect_to_db(app)
    print "Connected to DB."