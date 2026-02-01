"""
A/B Testing Framework for dopamine.watch
Test headlines, CTAs, images, and more
"""

import random
import json
import os
from datetime import datetime
from openai import OpenAI


class ABTester:
    """A/B testing for headlines, CTAs, images"""

    def __init__(self):
        self.base_dir = os.path.dirname(__file__)
        self.test_dir = os.path.join(self.base_dir, "logs", "ab_tests")
        os.makedirs(self.test_dir, exist_ok=True)

    def generate_headline_variants(self, original_headline: str) -> tuple:
        """Generate A/B test variants of headline"""

        api_key = os.getenv('OPENAI_API_KEY')

        if not api_key:
            # Fallback variants
            variants = [
                original_headline.replace("Why", "Here's Why"),
                original_headline.replace("Why", "The Reason"),
                f"The Truth About {original_headline.split(' ', 2)[-1]}"
            ]
        else:
            client = OpenAI(api_key=api_key)

            prompt = f"""Generate 3 alternative headlines for this blog post:

ORIGINAL: {original_headline}

Create variants that:
1. Different angle/hook
2. Different emotional appeal
3. Different length/style

All should be compelling and ADHD-friendly.

OUTPUT AS JSON:
{{
  "variants": [
    "Variant 1 headline",
    "Variant 2 headline",
    "Variant 3 headline"
  ]
}}"""

            try:
                response = client.chat.completions.create(
                    model="gpt-4-turbo-preview",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.9
                )

                content = response.choices[0].message.content
                if "```json" in content:
                    content = content.split("```json")[1].split("```")[0].strip()
                elif "```" in content:
                    content = content.split("```")[1].split("```")[0].strip()

                data = json.loads(content)
                variants = data['variants']
            except Exception as e:
                print(f"⚠️ OpenAI error: {e}")
                variants = [
                    original_headline.replace("Why", "Here's Why"),
                    original_headline.replace("Why", "The Reason"),
                    original_headline + " (And What to Do About It)"
                ]

        # Create test
        test_id = self._create_test(
            test_type="headline",
            original=original_headline,
            variants=variants
        )

        return test_id, variants

    def generate_cta_variants(self) -> tuple:
        """Generate CTA button text variants"""

        variants = [
            "Get Started Free",
            "Try It Now",
            "Start Your Free Trial",
            "Find Your Content",
            "Stop Scrolling, Start Watching"
        ]

        test_id = self._create_test(
            test_type="cta",
            original=variants[0],
            variants=variants[1:]
        )

        return test_id, variants

    def _create_test(self, test_type: str, original: str, variants: list) -> str:
        """Create A/B test record"""

        test_id = f"{test_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        test_data = {
            "test_id": test_id,
            "type": test_type,
            "created_at": datetime.now().isoformat(),
            "status": "active",
            "original": original,
            "variants": variants,
            "results": {
                "original": {"views": 0, "clicks": 0, "ctr": 0},
                **{f"variant_{i}": {"views": 0, "clicks": 0, "ctr": 0}
                   for i in range(len(variants))}
            }
        }

        # Save test
        test_file = os.path.join(self.test_dir, f"{test_id}.json")
        with open(test_file, 'w') as f:
            json.dump(test_data, f, indent=2)

        print(f"✅ Created A/B test: {test_id}")

        return test_id

    def get_variant_for_user(self, test_id: str) -> str:
        """Get variant to show user (random assignment)"""

        test_file = os.path.join(self.test_dir, f"{test_id}.json")

        if not os.path.exists(test_file):
            return None

        with open(test_file, 'r') as f:
            test = json.load(f)

        # Random assignment
        all_options = ['original'] + [f'variant_{i}' for i in range(len(test['variants']))]
        chosen = random.choice(all_options)

        if chosen == 'original':
            return test['original']
        else:
            variant_index = int(chosen.split('_')[1])
            return test['variants'][variant_index]

    def record_view(self, test_id: str, variant: str):
        """Record when a variant is viewed"""

        test_file = os.path.join(self.test_dir, f"{test_id}.json")

        if not os.path.exists(test_file):
            return

        with open(test_file, 'r') as f:
            test = json.load(f)

        if variant in test['results']:
            test['results'][variant]['views'] += 1

            with open(test_file, 'w') as f:
                json.dump(test, f, indent=2)

    def record_click(self, test_id: str, variant: str):
        """Record when variant gets clicked"""

        test_file = os.path.join(self.test_dir, f"{test_id}.json")

        if not os.path.exists(test_file):
            return

        with open(test_file, 'r') as f:
            test = json.load(f)

        if variant in test['results']:
            test['results'][variant]['clicks'] += 1

            # Calculate CTR
            views = test['results'][variant]['views']
            clicks = test['results'][variant]['clicks']
            test['results'][variant]['ctr'] = (clicks / views * 100) if views > 0 else 0

            with open(test_file, 'w') as f:
                json.dump(test, f, indent=2)

    def get_winner(self, test_id: str) -> dict:
        """Determine winning variant"""

        test_file = os.path.join(self.test_dir, f"{test_id}.json")

        if not os.path.exists(test_file):
            return None

        with open(test_file, 'r') as f:
            test = json.load(f)

        # Find highest CTR with minimum views threshold
        min_views = 10

        valid_results = {k: v for k, v in test['results'].items()
                        if v['views'] >= min_views}

        if not valid_results:
            return {"status": "insufficient_data", "message": f"Need at least {min_views} views per variant"}

        winner = max(valid_results.items(), key=lambda x: x[1]['ctr'])

        return {
            "variant": winner[0],
            "ctr": winner[1]['ctr'],
            "clicks": winner[1]['clicks'],
            "views": winner[1]['views'],
            "content": test['original'] if winner[0] == 'original' else test['variants'][int(winner[0].split('_')[1])]
        }

    def get_all_tests(self) -> list:
        """Get all A/B tests"""

        tests = []
        for filename in os.listdir(self.test_dir):
            if filename.endswith('.json'):
                with open(os.path.join(self.test_dir, filename), 'r') as f:
                    tests.append(json.load(f))
        return tests

    def generate_report(self):
        """Generate A/B testing report"""

        print("\n" + "="*60)
        print("🧪 A/B TESTING REPORT")
        print(f"   Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        print("="*60 + "\n")

        tests = self.get_all_tests()

        if not tests:
            print("No A/B tests found.")
            return

        for test in tests:
            print(f"TEST: {test['test_id']}")
            print(f"Type: {test['type']}")
            print(f"Status: {test['status']}")
            print(f"Created: {test['created_at'][:10]}")
            print(f"\nORIGINAL: {test['original'][:60]}...")
            print(f"\nRESULTS:")

            for variant, data in test['results'].items():
                print(f"  {variant}:")
                print(f"    Views: {data['views']}")
                print(f"    Clicks: {data['clicks']}")
                print(f"    CTR: {data['ctr']:.2f}%")

            winner = self.get_winner(test['test_id'])
            if winner and winner.get('status') != 'insufficient_data':
                print(f"\n  🏆 WINNER: {winner['variant']} ({winner['ctr']:.2f}% CTR)")
            else:
                print(f"\n  ⏳ Need more data to determine winner")

            print("\n" + "-"*60 + "\n")


if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()

    tester = ABTester()

    # Test headline variants
    print("Testing headline variant generation...")
    test_id, variants = tester.generate_headline_variants(
        "Why ADHD Makes Choosing Content Impossible"
    )

    print(f"\nGenerated variants:")
    for i, variant in enumerate(variants, 1):
        print(f"  {i}. {variant}")

    # Simulate some views and clicks
    print("\nSimulating user interactions...")
    for _ in range(50):
        variant = random.choice(['original'] + [f'variant_{i}' for i in range(len(variants))])
        tester.record_view(test_id, variant)
        if random.random() < 0.15:  # 15% click rate
            tester.record_click(test_id, variant)

    # Generate report
    tester.generate_report()
