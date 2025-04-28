from time_project import db
from time_project.models import User
db.drop_all()
db.create_all()
user1 = User(
    username="渡辺喜介",
    users_id="kisuke0122",
    password="123",
    administrator="1",
    employment_type="fulltime",        
    fixed_wage=1000000               
)
user1.fixed_wage = 1000000
db.session.add(user1)
db.session.commit()