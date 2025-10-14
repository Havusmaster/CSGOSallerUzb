from datetime import datetime
from typing import Dict, List, Optional
import uuid


class Database:
    """In-memory database for products and auctions"""
    
    def __init__(self):
        self.products: Dict[str, dict] = {}
        self.auctions: Dict[str, dict] = {}
        self.purchases: Dict[str, dict] = {}
    
    # Product methods
    def add_product(self, name: str, price: float, category: str, 
                   description: str, photo_url: str, link: str, 
                   float_value: Optional[float] = None) -> str:
        """Add a new product"""
        product_id = str(uuid.uuid4())
        self.products[product_id] = {
            "id": product_id,
            "name": name,
            "price": price,
            "category": category,
            "description": description,
            "photo_url": photo_url,
            "link": link,
            "float": float_value,
            "status": "available",  # available, sold
            "created_at": datetime.now().isoformat()
        }
        return product_id
    
    def get_product(self, product_id: str) -> Optional[dict]:
        """Get product by ID"""
        return self.products.get(product_id)
    
    def get_all_products(self, category: Optional[str] = None, 
                        status: Optional[str] = None) -> List[dict]:
        """Get all products with optional filters"""
        products = list(self.products.values())
        
        if category:
            products = [p for p in products if p["category"] == category]
        
        if status:
            products = [p for p in products if p["status"] == status]
        
        return sorted(products, key=lambda x: x["created_at"], reverse=True)
    
    def update_product(self, product_id: str, **kwargs) -> bool:
        """Update product fields"""
        if product_id not in self.products:
            return False
        
        self.products[product_id].update(kwargs)
        return True
    
    def delete_product(self, product_id: str) -> bool:
        """Delete a product"""
        if product_id in self.products:
            del self.products[product_id]
            return True
        return False
    
    def set_product_status(self, product_id: str, status: str) -> bool:
        """Set product status (available/sold)"""
        return self.update_product(product_id, status=status)
    
    # Auction methods
    def add_auction(self, name: str, starting_price: float, category: str,
                   description: str, photo_url: str, link: str,
                   float_value: Optional[float] = None) -> str:
        """Add a new auction lot"""
        auction_id = str(uuid.uuid4())
        self.auctions[auction_id] = {
            "id": auction_id,
            "name": name,
            "starting_price": starting_price,
            "current_price": starting_price,
            "category": category,
            "description": description,
            "photo_url": photo_url,
            "link": link,
            "float": float_value,
            "status": "active",  # active, closed
            "bids": [],
            "created_at": datetime.now().isoformat()
        }
        return auction_id
    
    def get_auction(self, auction_id: str) -> Optional[dict]:
        """Get auction by ID"""
        return self.auctions.get(auction_id)
    
    def get_all_auctions(self, status: Optional[str] = None) -> List[dict]:
        """Get all auctions with optional status filter"""
        auctions = list(self.auctions.values())
        
        if status:
            auctions = [a for a in auctions if a["status"] == status]
        
        return sorted(auctions, key=lambda x: x["created_at"], reverse=True)
    
    def add_bid(self, auction_id: str, user_id: int, amount: float) -> bool:
        """Add a bid to an auction"""
        if auction_id not in self.auctions:
            return False
        
        auction = self.auctions[auction_id]
        if auction["status"] != "active":
            return False
        
        if amount <= auction["current_price"]:
            return False
        
        auction["bids"].append({
            "user_id": user_id,
            "amount": amount,
            "timestamp": datetime.now().isoformat()
        })
        auction["current_price"] = amount
        return True
    
    def close_auction(self, auction_id: str) -> bool:
        """Close an auction"""
        return self.update_auction(auction_id, status="closed")
    
    def update_auction(self, auction_id: str, **kwargs) -> bool:
        """Update auction fields"""
        if auction_id not in self.auctions:
            return False
        
        self.auctions[auction_id].update(kwargs)
        return True
    
    def delete_auction(self, auction_id: str) -> bool:
        """Delete an auction"""
        if auction_id in self.auctions:
            del self.auctions[auction_id]
            return True
        return False
    
    # Purchase tracking
    def record_purchase(self, product_id: str, user_id: int) -> str:
        """Record a purchase attempt"""
        purchase_id = str(uuid.uuid4())
        self.purchases[purchase_id] = {
            "id": purchase_id,
            "product_id": product_id,
            "user_id": user_id,
            "status": "pending",  # pending, confirmed, cancelled
            "timestamp": datetime.now().isoformat()
        }
        return purchase_id
    
    def get_purchase(self, purchase_id: str) -> Optional[dict]:
        """Get purchase by ID"""
        return self.purchases.get(purchase_id)
    
    def update_purchase_status(self, purchase_id: str, status: str) -> bool:
        """Update purchase status"""
        if purchase_id in self.purchases:
            self.purchases[purchase_id]["status"] = status
            return True
        return False
