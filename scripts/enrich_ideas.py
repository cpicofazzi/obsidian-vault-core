import os, re

vault = r'c:\Users\picof\Documents\pico-vault'
ideas_dir = os.path.join(vault, '30_Ideas')

meta = {
    'AI Renders Modeling Real Clothes.md': {'stage': '💡 Spark', 'domain': 'AI/Tech', 'effort': 'Medium', 'value': 'High', 'tags': ['idea', 'gen-ai', 'fashion', 'computer-vision']},
    'AMEX Hotels Trip Planner.md': {'stage': '🌱 Developing', 'domain': 'AI/Tech', 'effort': 'Medium', 'value': 'Medium', 'tags': ['idea', 'travel', 'amex', 'automation']},
    'Dinner Service Optimizer.md': {'stage': '🚀 Ready to Build', 'domain': 'AI/Tech', 'effort': 'High', 'value': 'High', 'tags': ['idea', 'optimization', 'operations', 'ml']},
    'Evolution Battle Royal.md': {'stage': '💡 Spark', 'domain': 'AI/Tech', 'effort': 'High', 'value': 'Medium', 'tags': ['idea', 'gaming', 'reinforcement-learning', 'simulation']},
    'Job Recruiter Agent.md': {'stage': '🚀 Ready to Build', 'domain': 'AI/Tech', 'effort': 'High', 'value': 'High', 'tags': ['idea', 'agents', 'career', 'llm']},
    'Nascar Predictor.md': {'stage': '💡 Spark', 'domain': 'AI/Tech', 'effort': 'Medium', 'value': 'Medium', 'tags': ['idea', 'sports', 'predictive-modeling', 'data-science']},
    'Research Paper Summarizer.md': {'stage': '🌱 Developing', 'domain': 'AI/Tech', 'effort': 'Low', 'value': 'High', 'tags': ['idea', 'nlp', 'llm', 'research-tool']},
    'Secure Financial Advisor App.md': {'stage': '🚀 Ready to Build', 'domain': 'AI/Tech', 'effort': 'High', 'value': 'High', 'tags': ['idea', 'fintech', 'rag', 'security']},
    'Secure Financial Advisor Overview.md': {'stage': '🚀 Ready to Build', 'domain': 'AI/Tech', 'effort': 'High', 'value': 'High', 'tags': ['idea', 'fintech', 'rag', 'architecture']},
    'Superbase.md': {'stage': '⏸️ Backlog', 'domain': 'AI/Tech', 'effort': 'Low', 'value': 'Low', 'tags': ['idea', 'database', 'fantasy-sports']},
    'Trend Scraper.md': {'stage': '💡 Spark', 'domain': 'AI/Tech', 'effort': 'Low', 'value': 'High', 'tags': ['idea', 'scraping', 'market-intelligence', 'automation']},
    'Trip Planner.md': {'stage': '🌱 Developing', 'domain': 'AI/Tech', 'effort': 'Medium', 'value': 'High', 'tags': ['idea', 'travel', 'budgeting', 'forecasting']},
    'Custom Hotsauce Business.md': {'stage': '💡 Spark', 'domain': 'Business', 'effort': 'Medium', 'value': 'Medium', 'tags': ['idea', 'business', 'food', 'ecommerce']},
    'SoCalCoastal.md': {'stage': '🌱 Developing', 'domain': 'Business', 'effort': 'Medium', 'value': 'High', 'tags': ['idea', 'brand', 'ecommerce', 'lifestyle']},
    'Dynasty Basketball Predictor.md': {'stage': '🌱 Developing', 'domain': 'Creative', 'effort': 'Medium', 'value': 'High', 'tags': ['idea', 'sports', 'machine-learning', 'transformers']},
}

for root, dirs, files in os.walk(ideas_dir):
    for f in files:
        if f in meta:
            p = os.path.join(root, f)
            with open(p, 'r', encoding='utf-8', errors='ignore') as fl:
                content = fl.read()
            m = meta[f]
            if content.startswith('---'):
                parts = content.split('---', 2)
                body = parts[2].strip() if len(parts) >= 3 else content
            else:
                body = content.strip()
            
            title = f[:-3]
            tags_yaml = '\n'.join([f'  - {t}' for t in m['tags']])
            new_frontmatter = f'''---
title: "{title}"
type: idea
stage: "{m['stage']}"
domain: "{m['domain']}"
effort: "{m['effort']}"
value: "{m['value']}"
tags:
{tags_yaml}
---

'''
            if body and not body.startswith('#'):
                body = f'# {title}\n\n' + body
            elif not body:
                body = f'# {title}\n\n> [!abstract] Overview\n> Concept for {title}.\n'

            new_content = new_frontmatter + body + '\n'
            with open(p, 'w', encoding='utf-8') as fl:
                fl.write(new_content)
            print(f'Enriched: {f}')

print('Idea enrichment complete.')
