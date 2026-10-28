"""
Indian Food Database — 30+ common items for the NutriPulse RAG pipeline.
Run this script once to seed IndianFoodItem table AND ChromaDB vector store.
"""
import os
import sys

# Ensure backend directory is on path
sys.path.insert(0, os.path.dirname(__file__))

INDIAN_FOODS = [
    # Staples
    {
        "food_name": "Roti (Whole Wheat Chapati)",
        "serving_unit": "1 Roti (30g)",
        "serving_size_g": 30,
        "calories": 71,
        "protein_g": 2.7,
        "carbs_g": 14.0,
        "fat_g": 0.9,
        "fiber_g": 1.8,
        "tags": "Staple, Vegetarian, North Indian",
        "description": "Thin whole wheat flatbread, a staple in Indian households. Low fat, moderate carbs.",
        "is_vegetarian": True,
    },
    {
        "food_name": "Basmati Rice (Cooked)",
        "serving_unit": "1 Katori (150g)",
        "serving_size_g": 150,
        "calories": 195,
        "protein_g": 4.0,
        "carbs_g": 42.0,
        "fat_g": 0.5,
        "fiber_g": 0.5,
        "tags": "Staple, Vegetarian, Carbs",
        "description": "Long-grain aromatic rice, widely consumed across India.",
        "is_vegetarian": True,
    },
    {
        "food_name": "Dal Tadka (Yellow Lentils)",
        "serving_unit": "1 Katori (200g)",
        "serving_size_g": 200,
        "calories": 180,
        "protein_g": 11.0,
        "carbs_g": 28.0,
        "fat_g": 4.5,
        "fiber_g": 7.0,
        "tags": "High-Fiber, High-Protein, Vegetarian, North Indian",
        "description": "Tempered yellow lentils cooked with spices — excellent protein source for vegetarians.",
        "is_vegetarian": True,
    },
    # South Indian
    {
        "food_name": "Idli",
        "serving_unit": "2 Idlis (100g)",
        "serving_size_g": 100,
        "calories": 132,
        "protein_g": 4.5,
        "carbs_g": 26.0,
        "fat_g": 0.6,
        "fiber_g": 1.2,
        "tags": "South Indian, Vegetarian, Low-Fat, Breakfast",
        "description": "Steamed rice and lentil cakes, very light and easy to digest.",
        "is_vegetarian": True,
    },
    {
        "food_name": "Masala Dosa",
        "serving_unit": "1 Dosa (150g)",
        "serving_size_g": 150,
        "calories": 168,
        "protein_g": 4.0,
        "carbs_g": 30.0,
        "fat_g": 4.0,
        "fiber_g": 2.0,
        "tags": "South Indian, Vegetarian, Breakfast, Street Food",
        "description": "Crispy fermented rice and lentil crepe stuffed with spiced potato filling.",
        "is_vegetarian": True,
    },
    {
        "food_name": "Sambar",
        "serving_unit": "1 Katori (200g)",
        "serving_size_g": 200,
        "calories": 120,
        "protein_g": 6.0,
        "carbs_g": 18.0,
        "fat_g": 3.0,
        "fiber_g": 4.5,
        "tags": "South Indian, Vegetarian, High-Fiber, Low-Calorie",
        "description": "Tamarind-based lentil stew with vegetables and spices.",
        "is_vegetarian": True,
    },
    {
        "food_name": "Upma",
        "serving_unit": "1 Plate (200g)",
        "serving_size_g": 200,
        "calories": 220,
        "protein_g": 5.5,
        "carbs_g": 38.0,
        "fat_g": 5.5,
        "fiber_g": 2.5,
        "tags": "South Indian, Breakfast, Vegetarian",
        "description": "Savory semolina dish cooked with vegetables and tempered spices.",
        "is_vegetarian": True,
    },
    # High-Protein
    {
        "food_name": "Paneer Bhurji",
        "serving_unit": "1 Katori (150g)",
        "serving_size_g": 150,
        "calories": 270,
        "protein_g": 18.0,
        "carbs_g": 8.0,
        "fat_g": 19.0,
        "fiber_g": 1.0,
        "tags": "High-Protein, Vegetarian, North Indian",
        "description": "Scrambled cottage cheese cooked with onions, tomatoes and spices. High protein vegetarian option.",
        "is_vegetarian": True,
    },
    {
        "food_name": "Paneer Tikka",
        "serving_unit": "6 pieces (150g)",
        "serving_size_g": 150,
        "calories": 260,
        "protein_g": 17.0,
        "carbs_g": 10.0,
        "fat_g": 17.0,
        "fiber_g": 1.5,
        "tags": "High-Protein, Vegetarian, Starter, North Indian",
        "description": "Marinated cottage cheese cubes grilled in tandoor. Great for high-protein vegetarian diets.",
        "is_vegetarian": True,
    },
    {
        "food_name": "Chicken Tikka",
        "serving_unit": "4 pieces (150g)",
        "serving_size_g": 150,
        "calories": 240,
        "protein_g": 30.0,
        "carbs_g": 5.0,
        "fat_g": 11.0,
        "fiber_g": 0.5,
        "tags": "High-Protein, Non-Vegetarian, Low-Carb, North Indian",
        "description": "Tandoor-grilled chicken marinated in spiced yogurt. Excellent high-protein, low-fat option.",
        "is_vegetarian": False,
    },
    {
        "food_name": "Egg White Omelette (2 eggs)",
        "serving_unit": "1 Omelette (100g)",
        "serving_size_g": 100,
        "calories": 70,
        "protein_g": 14.0,
        "carbs_g": 1.5,
        "fat_g": 0.5,
        "fiber_g": 0,
        "tags": "High-Protein, Low-Fat, Low-Carb, Breakfast",
        "description": "Pure egg white omelette — ideal for high-protein, low-calorie diets.",
        "is_vegetarian": True,
    },
    {
        "food_name": "Moong Dal Cheela",
        "serving_unit": "2 Cheelas (120g)",
        "serving_size_g": 120,
        "calories": 180,
        "protein_g": 12.0,
        "carbs_g": 26.0,
        "fat_g": 3.5,
        "fiber_g": 4.0,
        "tags": "High-Protein, Vegetarian, Breakfast, Weight-Loss",
        "description": "Protein-rich green moong lentil pancakes, popular as a healthy breakfast.",
        "is_vegetarian": True,
    },
    {
        "food_name": "Chole (Chickpea Curry)",
        "serving_unit": "1 Katori (200g)",
        "serving_size_g": 200,
        "calories": 210,
        "protein_g": 12.0,
        "carbs_g": 32.0,
        "fat_g": 5.0,
        "fiber_g": 9.0,
        "tags": "High-Protein, High-Fiber, Vegetarian, North Indian",
        "description": "Spiced chickpea curry — high in plant protein and fiber.",
        "is_vegetarian": True,
    },
    {
        "food_name": "Rajma (Kidney Bean Curry)",
        "serving_unit": "1 Katori (200g)",
        "serving_size_g": 200,
        "calories": 215,
        "protein_g": 13.0,
        "carbs_g": 35.0,
        "fat_g": 3.5,
        "fiber_g": 8.0,
        "tags": "High-Protein, High-Fiber, Vegetarian, North Indian",
        "description": "Spiced red kidney bean curry. Rich in protein and complex carbs.",
        "is_vegetarian": True,
    },
    {
        "food_name": "Boiled Eggs (2)",
        "serving_unit": "2 Eggs (100g)",
        "serving_size_g": 100,
        "calories": 155,
        "protein_g": 13.0,
        "carbs_g": 1.1,
        "fat_g": 11.0,
        "fiber_g": 0,
        "tags": "High-Protein, Low-Carb, Breakfast",
        "description": "Classic boiled eggs — complete protein with all essential amino acids.",
        "is_vegetarian": True,
    },
    # Street Food
    {
        "food_name": "Pav Bhaji",
        "serving_unit": "1 Plate (250g)",
        "serving_size_g": 250,
        "calories": 400,
        "protein_g": 9.5,
        "carbs_g": 58.0,
        "fat_g": 14.0,
        "fiber_g": 5.0,
        "tags": "Street Food, Vegetarian, Mumbai",
        "description": "Mashed vegetable curry served with buttered bread rolls.",
        "is_vegetarian": True,
    },
    {
        "food_name": "Vada Pav",
        "serving_unit": "1 Piece (120g)",
        "serving_size_g": 120,
        "calories": 295,
        "protein_g": 6.0,
        "carbs_g": 44.0,
        "fat_g": 9.5,
        "fiber_g": 2.5,
        "tags": "Street Food, Vegetarian, Mumbai",
        "description": "Deep-fried potato fritter in a bread roll — Mumbai's iconic street food.",
        "is_vegetarian": True,
    },
    {
        "food_name": "Pani Puri (6 pieces)",
        "serving_unit": "6 pieces (100g)",
        "serving_size_g": 100,
        "calories": 210,
        "protein_g": 4.0,
        "carbs_g": 35.0,
        "fat_g": 6.0,
        "fiber_g": 2.0,
        "tags": "Street Food, Vegetarian, Snack",
        "description": "Crispy hollow puri filled with spiced tamarind water and chickpeas.",
        "is_vegetarian": True,
    },
    # Curries & Mains
    {
        "food_name": "Butter Chicken (Murgh Makhani)",
        "serving_unit": "1 Katori (200g)",
        "serving_size_g": 200,
        "calories": 310,
        "protein_g": 24.0,
        "carbs_g": 12.0,
        "fat_g": 18.0,
        "fiber_g": 1.5,
        "tags": "Non-Vegetarian, High-Protein, North Indian, Curry",
        "description": "Tender chicken in rich tomato-cream sauce. High protein with moderate fat.",
        "is_vegetarian": False,
    },
    {
        "food_name": "Palak Paneer",
        "serving_unit": "1 Katori (200g)",
        "serving_size_g": 200,
        "calories": 250,
        "protein_g": 14.0,
        "carbs_g": 12.0,
        "fat_g": 16.0,
        "fiber_g": 4.0,
        "tags": "High-Protein, Vegetarian, North Indian, Iron-Rich",
        "description": "Cottage cheese in creamy spinach gravy — iron and protein-rich vegetarian dish.",
        "is_vegetarian": True,
    },
    {
        "food_name": "Aloo Gobi",
        "serving_unit": "1 Katori (200g)",
        "serving_size_g": 200,
        "calories": 150,
        "protein_g": 4.5,
        "carbs_g": 24.0,
        "fat_g": 5.0,
        "fiber_g": 4.0,
        "tags": "Vegetarian, North Indian, Low-Calorie",
        "description": "Spiced potato and cauliflower stir-fry — light and nutritious.",
        "is_vegetarian": True,
    },
    {
        "food_name": "Fish Curry (Rohu/Catla)",
        "serving_unit": "1 Katori (200g)",
        "serving_size_g": 200,
        "calories": 220,
        "protein_g": 26.0,
        "carbs_g": 6.0,
        "fat_g": 10.0,
        "fiber_g": 0.5,
        "tags": "High-Protein, Non-Vegetarian, Low-Carb, East Indian",
        "description": "Spiced freshwater fish curry — excellent source of lean protein and omega-3.",
        "is_vegetarian": False,
    },
    # Snacks & Breakfast
    {
        "food_name": "Greek Yogurt (Dahi)",
        "serving_unit": "1 Bowl (200g)",
        "serving_size_g": 200,
        "calories": 120,
        "protein_g": 12.0,
        "carbs_g": 9.0,
        "fat_g": 3.0,
        "fiber_g": 0,
        "tags": "High-Protein, Vegetarian, Breakfast, Snack, Probiotic",
        "description": "Plain thick curd / dahi — probiotic, high protein, low calorie snack.",
        "is_vegetarian": True,
    },
    {
        "food_name": "Sprout Salad",
        "serving_unit": "1 Bowl (150g)",
        "serving_size_g": 150,
        "calories": 100,
        "protein_g": 8.0,
        "carbs_g": 14.0,
        "fat_g": 1.0,
        "fiber_g": 5.0,
        "tags": "High-Protein, High-Fiber, Vegetarian, Weight-Loss, Snack",
        "description": "Mixed bean and lentil sprouts with lemon and spices — protein-dense, low calorie.",
        "is_vegetarian": True,
    },
    {
        "food_name": "Poha (Flattened Rice)",
        "serving_unit": "1 Plate (200g)",
        "serving_size_g": 200,
        "calories": 200,
        "protein_g": 4.5,
        "carbs_g": 38.0,
        "fat_g": 4.0,
        "fiber_g": 2.5,
        "tags": "Breakfast, Vegetarian, Maharashtra",
        "description": "Light flattened rice cooked with onion, peanuts and spices.",
        "is_vegetarian": True,
    },
    {
        "food_name": "Sattu Drink",
        "serving_unit": "1 Glass (250ml)",
        "serving_size_g": 250,
        "calories": 160,
        "protein_g": 10.0,
        "carbs_g": 26.0,
        "fat_g": 2.0,
        "fiber_g": 4.0,
        "tags": "High-Protein, Vegetarian, Pre-Workout, Bihar",
        "description": "Roasted Bengal gram flour drink — traditional high-protein energizer from Bihar.",
        "is_vegetarian": True,
    },
    {
        "food_name": "Roasted Makhana (Foxnuts)",
        "serving_unit": "1 Cup (30g)",
        "serving_size_g": 30,
        "calories": 106,
        "protein_g": 4.0,
        "carbs_g": 20.0,
        "fat_g": 0.5,
        "fiber_g": 0.5,
        "tags": "Snack, Vegetarian, Low-Fat, High-Protein",
        "description": "Light roasted lotus seeds — guilt-free, low fat, high protein snack.",
        "is_vegetarian": True,
    },
    {
        "food_name": "Banana",
        "serving_unit": "1 Medium Banana (120g)",
        "serving_size_g": 120,
        "calories": 105,
        "protein_g": 1.3,
        "carbs_g": 27.0,
        "fat_g": 0.4,
        "fiber_g": 3.1,
        "tags": "Fruit, Vegetarian, Pre-Workout, High-Carb",
        "description": "Quick energy fruit, ideal as a pre-workout snack for carb replenishment.",
        "is_vegetarian": True,
    },
    {
        "food_name": "Almonds (Badam)",
        "serving_unit": "20 Almonds (28g)",
        "serving_size_g": 28,
        "calories": 164,
        "protein_g": 6.0,
        "carbs_g": 6.0,
        "fat_g": 14.0,
        "fiber_g": 3.5,
        "tags": "Snack, Vegetarian, Healthy-Fat, High-Protein",
        "description": "Nutrient-dense nuts rich in healthy monounsaturated fats and vitamin E.",
        "is_vegetarian": True,
    },
    {
        "food_name": "Biryani (Chicken)",
        "serving_unit": "1 Plate (300g)",
        "serving_size_g": 300,
        "calories": 450,
        "protein_g": 25.0,
        "carbs_g": 55.0,
        "fat_g": 14.0,
        "fiber_g": 1.5,
        "tags": "Non-Vegetarian, High-Protein, Rice, Hyderabad",
        "description": "Aromatic basmati rice cooked with spiced chicken — complete meal option.",
        "is_vegetarian": False,
    },
    {
        "food_name": "Vegetable Biryani",
        "serving_unit": "1 Plate (300g)",
        "serving_size_g": 300,
        "calories": 360,
        "protein_g": 9.0,
        "carbs_g": 65.0,
        "fat_g": 8.0,
        "fiber_g": 3.0,
        "tags": "Vegetarian, Rice, Hyderabad",
        "description": "Fragrant basmati rice cooked with mixed vegetables and whole spices.",
        "is_vegetarian": True,
    },
    {
        "food_name": "Whey Protein Shake",
        "serving_unit": "1 Scoop (30g in 250ml milk)",
        "serving_size_g": 280,
        "calories": 230,
        "protein_g": 30.0,
        "carbs_g": 18.0,
        "fat_g": 4.0,
        "fiber_g": 0.5,
        "tags": "High-Protein, Post-Workout, Supplement",
        "description": "Whey protein with milk — optimal post-workout protein shake for muscle recovery.",
        "is_vegetarian": True,
    },
]


def seed_indian_foods():
    """Seed the SQL database and ChromaDB vector store with Indian food data."""
    from database import SessionLocal, IndianFoodItem, create_tables
    create_tables()
    
    db = SessionLocal()
    try:
        existing = db.query(IndianFoodItem).count()
        if existing >= len(INDIAN_FOODS):
            print(f"[OK] {existing} Indian food items already seeded. Skipping SQL seed.")
        else:
            db.query(IndianFoodItem).delete()
            for food in INDIAN_FOODS:
                item = IndianFoodItem(**food)
                db.add(item)
            db.commit()
            print(f"[OK] Seeded {len(INDIAN_FOODS)} Indian food items to database.")
    finally:
        db.close()


def build_chroma_index():
    """Build ChromaDB vector index from Indian food items for RAG."""
    try:
        import chromadb
        from chromadb.config import Settings
        
        client = chromadb.PersistentClient(path="./chroma_db")
        
        # Check if collection exists and is populated
        try:
            collection = client.get_collection("indian_foods")
            if collection.count() >= len(INDIAN_FOODS):
                print(f"[OK] ChromaDB already has {collection.count()} items. Skipping re-index.")
                return
            client.delete_collection("indian_foods")
        except Exception:
            pass
        
        collection = client.create_collection(
            name="indian_foods",
            metadata={"hnsw:space": "cosine"}
        )
        
        # Build documents, metadata, ids
        documents = []
        metadatas = []
        ids = []
        
        for i, food in enumerate(INDIAN_FOODS):
            # Rich text for embedding
            doc = (
                f"Food: {food['food_name']}. "
                f"Serving: {food['serving_unit']}. "
                f"Calories: {food['calories']} kcal. "
                f"Protein: {food['protein_g']}g, Carbs: {food['carbs_g']}g, Fat: {food['fat_g']}g. "
                f"Tags: {food['tags']}. "
                f"Description: {food['description']}"
            )
            documents.append(doc)
            metadatas.append({
                "food_name": food["food_name"],
                "calories": food["calories"],
                "protein_g": food["protein_g"],
                "carbs_g": food["carbs_g"],
                "fat_g": food["fat_g"],
                "tags": food["tags"],
                "is_vegetarian": str(food["is_vegetarian"]),
                "serving_unit": food["serving_unit"],
            })
            ids.append(f"food_{i}")
        
        # Use ChromaDB default embedding (sentence-transformers)
        collection.add(documents=documents, metadatas=metadatas, ids=ids)
        print(f"[OK] ChromaDB index built with {len(INDIAN_FOODS)} food items.")
        
    except ImportError as e:
        print(f"[WARN] ChromaDB not available: {e}. RAG will use SQL fallback.")
    except Exception as e:
        print(f"[WARN] ChromaDB indexing failed: {e}. RAG will use SQL fallback.")


if __name__ == "__main__":
    seed_indian_foods()
    build_chroma_index()
    print("[OK] NutriPulse AI food database ready!")
