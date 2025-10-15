from datetime import datetime
from typing import Dict, List, Optional

class Database:
    def __init__(self):
        self.products: Dict[str, dict] = {}
        self.auctions: Dict[str, dict] = {}
        self.purchases: List[dict] = []
        self.next_product_id = 1
        self.next_auction_id = 1
        
    # Products
    def add_product(self, category: str, name: str, price: float, 
                   description: str, image_url: str, float_value: Optional[float] = None) -> str:
        product_id = f"prod_{self.next_product_id}"
        self.next_product_id += 1
        
        self.products[product_id] = {
            "id": product_id,
            "category": category,
            "name": name,
            "price": price,
            "description": description,
            "image_url": image_url,
            "float_value": float_value,
            "status": "available",
            "created_at": datetime.now().isoformat()
        }
        return product_id
    
    def get_product(self, product_id: str) -> Optional[dict]:
        return self.products.get(product_id)
    
    def get_all_products(self) -> List[dict]:
        return list(self.products.values())
    
    def get_products_by_category(self, category: str) -> List[dict]:
        return [p for p in self.products.values() if p["category"] == category]
    
    def update_product_status(self, product_id: str, status: str) -> bool:
        if product_id in self.products:
            self.products[product_id]["status"] = status
            return True
        return False
    
    def delete_product(self, product_id: str) -> bool:
        if product_id in self.products:
            del self.products[product_id]
            return True
        return False
    
    # Auctions
    def add_auction(self, category: str, name: str, start_price: float,
                   description: str, image_url: str, end_time: str,
                   float_value: Optional[float] = None) -> str:
        auction_id = f"auct_{self.next_auction_id}"
        self.next_auction_id += 1
        
        self.auctions[auction_id] = {
            "id": auction_id,
            "category": category,
            "name": name,
            "current_price": start_price,
            "description": description,
            "image_url": image_url,
            "float_value": float_value,
            "end_time": end_time,
            "bids": [],
            "status": "active",
            "created_at": datetime.now().isoformat()
        }
        return auction_id
    
    def get_auction(self, auction_id: str) -> Optional[dict]:
        return self.auctions.get(auction_id)
    
    def get_all_auctions(self) -> List[dict]:
        return list(self.auctions.values())
    
    def add_bid(self, auction_id: str, user_id: int, amount: float) -> bool:
        if auction_id in self.auctions:
            auction = self.auctions[auction_id]
            if amount > auction["current_price"]:
                auction["bids"].append({
                    "user_id": user_id,
                    "amount": amount,
                    "timestamp": datetime.now().isoformat()
                })
                auction["current_price"] = amount
                return True
        return False
    
    # Purchases
    def add_purchase(self, user_id: int, item_id: str, item_type: str, amount: float):
        self.purchases.append({
            "user_id": user_id,
            "item_id": item_id,
            "item_type": item_type,
            "amount": amount,
            "timestamp": datetime.now().isoformat()
        })

# Глобальный экземпляр базы данных
db = Database()
