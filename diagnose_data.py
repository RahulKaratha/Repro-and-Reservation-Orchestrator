from app import create_app, db
from app.models.bug import Bug
from app.models.user import User
import json

app = create_app()
with app.app_context():
    # 1. Check Bugs
    count = Bug.query.count()
    print(f"Total Bugs in DB: {count}")
    
    # 2. Check Roles
    mgr = User.query.filter_by(role='Manager').first()
    print(f"Sample Manager: {mgr.email if mgr else 'None'} (ID: {mgr.id if mgr else 'N/A'})")
    
    # 3. Simulate get_bugs logic for Manager
    bugs = Bug.query.all()
    repro = [b for b in bugs if b.bug_type == 'repro']
    test = [b for b in bugs if b.bug_type == 'test']
    print(f"Simulated API Result -> Repro: {len(repro)}, Test: {len(test)}")
    
    # 4. Check if any bugs are unassigned
    unassigned = Bug.query.filter_by(engineer_id=None).count()
    print(f"Unassigned Bugs: {unassigned}")
