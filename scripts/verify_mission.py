
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from models.user import Kurum

def verify():
    app = create_app()
    with app.app_context():
        kurum = Kurum.query.filter(Kurum.kisa_ad.ilike('KMF')).first()
        if kurum:
            print(f"Kurum: {kurum.kisa_ad}")
            print(f"Amac (Mission): {kurum.amac}")
            print(f"Vizyon: {kurum.vizyon}")
        else:
            print("KMF not found.")

if __name__ == "__main__":
    verify()
