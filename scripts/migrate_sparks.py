import os

vault = r'c:\Users\picof\Documents\pico-vault'

sparks = [
    {
        'file': r'30_Ideas\AI & Tech\Generative AI Background Footage.md',
        'title': 'Generative AI Background Footage',
        'domain': 'AI/Tech',
        'tags': ['idea', 'gen-ai', 'video', 'content-creation'],
        'content': '> [!abstract] Overview\n> Automated pipeline or marketplace generating high-definition ambient background footage, b-roll, and visual loops using generative video models.\n'
    },
    {
        'file': r'30_Ideas\AI & Tech\Plate and Pulse.md',
        'title': 'Plate and Pulse',
        'domain': 'AI/Tech',
        'tags': ['idea', 'food', 'health', 'app'],
        'content': '> [!abstract] Overview\n> Health, nutrition, and dining platform connecting food choices (plate) with biometric responses (pulse / health metrics).\n'
    },
    {
        'file': r'30_Ideas\Creative & Sports\Red Rising Space Map.md',
        'title': 'Red Rising Space Map',
        'domain': 'Creative',
        'tags': ['idea', 'sci-fi', 'world-building', 'interactive-map'],
        'content': '> [!abstract] Overview\n> Interactive, high-resolution astronomical solar system map tracing planetary orbits, battles, and fleet movements from the Red Rising sci-fi saga.\n'
    },
    {
        'file': r'30_Ideas\AI & Tech\Friend Bazaar Website.md',
        'title': 'Friend Bazaar Website',
        'domain': 'AI/Tech',
        'tags': ['idea', 'community', 'marketplace', 'web'],
        'content': '> [!abstract] Overview\n> Private, community-centric marketplace or talent exchange platform for friends and close social networks.\n'
    },
    {
        'file': r'30_Ideas\Business & Commerce\Fermentation Brand.md',
        'title': 'Fermentation Brand',
        'domain': 'Business',
        'tags': ['idea', 'food', 'fermentation', 'ecommerce'],
        'content': '> [!abstract] Overview\n> Artisanal culinary brand specializing in fermented specialties, probiotic tonics, and craft koji / hot sauce fermentations.\n'
    },
    {
        'file': r'30_Ideas\Business & Commerce\Funk Restaurant and Tapas Beer Hall.md',
        'title': 'Funk Restaurant and Tapas Beer Hall',
        'domain': 'Business',
        'tags': ['idea', 'hospitality', 'food', 'restaurant'],
        'content': '> [!abstract] Overview\n> Vibrant communal dining and social hall blending funky natural wines, craft beer, and elevated small-plate tapas.\n'
    },
    {
        'file': r'30_Ideas\Business & Commerce\Minimal Anime Brand.md',
        'title': 'Minimal Anime Brand',
        'domain': 'Business',
        'tags': ['idea', 'apparel', 'fashion', 'anime'],
        'content': '> [!abstract] Overview\n> Subtle, minimalist streetwear and lifestyle apparel featuring understated anime design cues and premium heavyweight fabrics.\n'
    },
    {
        'file': r'30_Ideas\Creative & Sports\Mixes on YouTube and SoundCloud.md',
        'title': 'Mixes on YouTube and SoundCloud',
        'domain': 'Creative',
        'tags': ['idea', 'music', 'dj', 'youtube', 'soundcloud'],
        'content': '> [!abstract] Overview\n> Curated electronic, house, or ambient DJ mixes paired with custom aesthetic visuals and tracklists across YouTube and SoundCloud.\n'
    },
]

for s in sparks:
    path = os.path.join(vault, s['file'])
    if not os.path.exists(path):
        tags_str = '\n'.join([f'  - {t}' for t in s['tags']])
        md = f'''---
title: "{s['title']}"
type: idea
stage: "💡 Spark"
domain: "{s['domain']}"
effort: "Medium"
value: "Medium"
tags:
{tags_str}
---

# {s['title']}

{s['content']}

## Next Action Items
- [ ] Brainstorm core MVP features
- [ ] Evaluate tech/product requirements
'''
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'w', encoding='utf-8') as f:
            f.write(md)
        print('Created spark note:', s['title'])

# Now remove legacy Ideas Home.md
legacy_ideas = os.path.join(vault, 'Ideas Home.md')
if os.path.exists(legacy_ideas):
    os.remove(legacy_ideas)
    print('Removed legacy Ideas Home.md')

print('Sparks migration complete!')
