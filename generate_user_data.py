#!/usr/bin/env python3
"""
Generate individual JSON files for each user from the Excel data.
This is an alternative to the n8n workflow for simpler deployments.

Usage:
    python generate_user_data.py Hackathon_Output_.xlsx output_folder
"""

import pandas as pd
import json
import sys
from pathlib import Path


def calculate_xp_info(tier):
    """Calculate XP values based on tier."""
    xp_values = {
        'Gold Tier': {'current': 1250, 'max': 2000, 'level': 6},
        'Silver Tier': {'current': 800, 'max': 1500, 'level': 4},
        'Bronze Tier': {'current': 400, 'max': 1000, 'level': 2}
    }
    return xp_values.get(tier, xp_values['Silver Tier'])


def generate_user_json(row):
    """Generate JSON data structure for a single user."""
    tier = row.get('tier', 'Silver Tier')
    xp_info = calculate_xp_info(tier)
    
    # Extract missions
    mission1 = row.get('mission-1', 'Post an AutoDM Post')
    mission2 = row.get('mission-2', 'Order a New Product')
    mission3 = row.get('mission-3', 'Upload 5 Catalog Picks')
    
    # Create user data structure
    user_data = {
        'user_id': int(row['user_id']),
        'name': f"Creator {int(row['user_id'])}",  # You can customize this
        'tier': tier,
        'level': xp_info['level'],
        'current_xp': xp_info['current'],
        'max_xp': xp_info['max'],
        'xp_percentage': round((xp_info['current'] / xp_info['max']) * 100),
        'missions': [
            {'text': mission1, 'xp': 20},
            {'text': mission2, 'xp': 5},
            {'text': mission3, 'xp': 15}
        ],
        'analytics': {
            'lifetime_nmv': int(row.get('lifetime_nmv', 0)),
            'posts_30days': int(row.get('posts_30days', 0)),
            'nmv_7days_attribution_30days': float(row.get('nmv_7days_attribution_30days', 0)),
            'daily_avg_products_ordered_30days': float(row.get('daily_avg_products_ordered_30days', 0)),
            'days_till_sale': int(row.get('Days till Sale', 0))
        },
        'quality_scores': {
            'cta': float(row.get('avg quality score of last 30 days for CTA', 0)),
            'price': float(row.get('avg quality score of last 30 days for price', 0)),
            'product_shown': float(row.get('avg quality score of last 30 days for product is shown properly', 0))
        }
    }
    
    return user_data


def main():
    if len(sys.argv) < 3:
        print("Usage: python generate_user_data.py <excel_file> <output_folder>")
        print("Example: python generate_user_data.py Hackathon_Output_.xlsx data")
        sys.exit(1)
    
    excel_file = sys.argv[1]
    output_folder = Path(sys.argv[2])
    
    # Create output folder if it doesn't exist
    output_folder.mkdir(parents=True, exist_ok=True)
    
    print(f"Reading Excel file: {excel_file}")
    df = pd.read_excel(excel_file)
    
    print(f"Found {len(df)} users")
    print(f"Generating JSON files in: {output_folder}")
    
    # Generate JSON file for each user
    for idx, row in df.iterrows():
        user_id = int(row['user_id'])
        user_data = generate_user_json(row)
        
        # Write to JSON file
        output_file = output_folder / f"{user_id}.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(user_data, f, indent=2, ensure_ascii=False)
        
        if (idx + 1) % 100 == 0:
            print(f"Processed {idx + 1} users...")
    
    print(f"\n✓ Successfully generated {len(df)} JSON files")
    print(f"\nNext steps:")
    print(f"1. Upload the '{output_folder}' folder to your GitHub repository")
    print(f"2. Access dashboards via: https://your-username.github.io/creator-dashboard/?user=USER_ID")
    
    # Generate an index file with all user IDs
    index_file = output_folder / "index.json"
    user_index = {
        'total_users': len(df),
        'user_ids': df['user_id'].tolist(),
        'tiers': df['tier'].value_counts().to_dict()
    }
    
    with open(index_file, 'w', encoding='utf-8') as f:
        json.dump(user_index, f, indent=2)
    
    print(f"✓ Created index file: {index_file}")


if __name__ == "__main__":
    main()
