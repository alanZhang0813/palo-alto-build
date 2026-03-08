"""Supplier database and sustainable sourcing recommendations.

Provides suggestions for where to source items when inventory is low,
with preference for sustainable/local suppliers.
"""

from transformers import pipeline

# Map of common item keywords to suppliers
# Format: {category: [supplier_list]}
SUSTAINABLE_SUPPLIERS = {
    "produce": [
        {
            "name": "Local Farmers Market",
            "distance": "2-5 miles",
            "benefits": ["Fresh daily", "Locally grown", "Minimal packaging"],
            "sustainability": "Excellent - 0 miles transport on average"
        },
        {
            "name": "Community Supported Agriculture (CSA)",
            "distance": "10-15 miles",
            "benefits": ["Seasonal selection", "Direct from farms", "Reduces plastic"],
            "sustainability": "Excellent - Direct farm partnership"
        },
        {
            "name": "Organic Grocery Chain",
            "distance": "5-10 miles",
            "benefits": ["Certified organic", "Fair trade options", "Local focus"],
            "sustainability": "Good - Sustainability focused"
        }
    ],
    "beverages": [
        {
            "name": "Local Beverage Distributor",
            "distance": "8-12 miles",
            "benefits": ["Bulk purchasing", "Returnable bottles", "Local brands"],
            "sustainability": "Excellent - Returnable containers"
        },
        {
            "name": "Fair Trade Distributor",
            "distance": "10-20 miles",
            "benefits": ["Ethical sourcing", "Direct partnerships", "Bulk discounts"],
            "sustainability": "Excellent - Fair trade practices"
        }
    ],
    "dairy": [
        {
            "name": "Local Dairy Co-op",
            "distance": "5-10 miles",
            "benefits": ["Fresh milk daily", "Sustainable practices", "Community owned"],
            "sustainability": "Excellent - Local sustainable practices"
        },
        {
            "name": "Organic Dairy Supplier",
            "distance": "15-25 miles",
            "benefits": ["Grass-fed options", "No antibiotics", "Certified organic"],
            "sustainability": "Excellent - Certified organic"
        }
    ],
    "grains": [
        {
            "name": "Bulk Foods Co-op",
            "distance": "3-8 miles",
            "benefits": ["Bring your own containers", "Organic options", "Fair prices"],
            "sustainability": "Excellent - Zero waste focus"
        },
        {
            "name": "Local Mill",
            "distance": "10-20 miles",
            "benefits": ["Fresh-ground flour", "Heritage grains", "Minimal packaging"],
            "sustainability": "Excellent - Direct from mill"
        }
    ],
    "protein": [
        {
            "name": "Local Meat Co-op",
            "distance": "10-15 miles",
            "benefits": ["Grass-fed/pastured", "Whole animal", "Direct from farms"],
            "sustainability": "Excellent - Regenerative practices"
        },
        {
            "name": "Sustainable Seafood Market",
            "distance": "8-15 miles",
            "benefits": ["Responsibly sourced", "Daily catch", "No endangered species"],
            "sustainability": "Excellent - Certified sustainable"
        },
        {
            "name": "Vegetarian Protein Supplier",
            "distance": "5-10 miles",
            "benefits": ["Plant-based proteins", "Fair trade", "Organic"],
            "sustainability": "Excellent - Lower carbon footprint"
        }
    ],
    "default": [
        {
            "name": "Local Wholesale Distributor",
            "distance": "10-15 miles",
            "benefits": ["Bulk purchasing", "Competitive pricing", "Fast delivery"],
            "sustainability": "Good - Bulk reduces packaging"
        },
        {
            "name": "Regional Food Hub",
            "distance": "20-30 miles",
            "benefits": ["Aggregates local suppliers", "Seasonal products", "Community supported"],
            "sustainability": "Excellent - Supports local economy"
        }
    ]
}


def categorize_item(item_name, extra_labels=None):
    """Determine the category of an item to find relevant suppliers using AI.
    
    Uses zero-shot classification for broader categorization, with keyword fallback.
    Can be passed ``extra_labels`` to expand the set of candidate categories
    (useful when calling from templates or alternate flows).
    
    Args:
        item_name (str): name of the item
        extra_labels (iterable[str]|None): additional labels to consider
        
    Returns:
        str: category key (produce, beverages, dairy, grains, protein, or default)
    """
    try:
        # Use AI for categorization
        classifier = pipeline("zero-shot-classification", model="typeform/distilbert-base-uncased-mnli")
        candidate_labels = ["produce", "beverages", "dairy", "grains", "protein"]
        if extra_labels:
            # ensure no duplicates and flatten list
            candidate_labels = list(dict.fromkeys(candidate_labels + list(extra_labels)))
        result = classifier(item_name, candidate_labels)
        
        # Get the top prediction
        top_label = result['labels'][0]
        top_score = result['scores'][0]
        
        # If confidence is high enough, use AI result
        if top_score > 0.5:
            return top_label
    except Exception as e:
        # If AI fails, fall back to keyword matching
        pass
    
    # Fallback to keyword-based categorization
    item_lower = item_name.lower()
    
    # Check for produce keywords
    produce_words = ['apple', 'banana', 'orange', 'lettuce', 'tomato', 'carrot',
                     'vegetable', 'fruit', 'produce', 'greens', 'spinach']
    if any(word in item_lower for word in produce_words):
        return 'produce'
    
    # Check for beverages
    bev_words = ['juice', 'water', 'tea', 'coffee', 'milk', 'beverage', 'drink']
    if any(word in item_lower for word in bev_words):
        if 'milk' in item_lower:
            return 'dairy'
        return 'beverages'
    
    # Check for dairy (excluding milk beverages handled above)
    dairy_words = ['cheese', 'yogurt', 'butter', 'cream', 'dairy']
    if any(word in item_lower for word in dairy_words):
        return 'dairy'
    
    # Check for grains
    grain_words = ['grain', 'flour', 'bread', 'rice', 'wheat', 'cereal', 'oat']
    if any(word in item_lower for word in grain_words):
        return 'grains'
    
    # Check for protein
    protein_words = ['meat', 'fish', 'chicken', 'beef', 'protein', 'poultry',
                     'seafood', 'bean', 'lentil', 'tofu']
    if any(word in item_lower for word in protein_words):
        return 'protein'
    
    return 'default'


def get_supplier_suggestions(item_name, quantity_on_hand, predicted_consumption):
    """Get sustainable supplier suggestions if supply might run out.
    
    Args:
        item_name (str): name of the item
        quantity_on_hand (int): current quantity in inventory
        predicted_consumption (float): predicted consumption over next period
        
    Returns:
        dict: {
            'will_runout': bool,
            'days_until_needed': int or None,
            'suppliers': list of supplier dicts
        }
    """
    # Check if supply will run out
    will_runout = quantity_on_hand < predicted_consumption
    
    category = categorize_item(item_name)
    suppliers = SUSTAINABLE_SUPPLIERS.get(category, SUSTAINABLE_SUPPLIERS['default'])
    
    return {
        'will_runout': will_runout,
        'shortfall': max(0, int(predicted_consumption - quantity_on_hand)),
        'suppliers': suppliers
    }
