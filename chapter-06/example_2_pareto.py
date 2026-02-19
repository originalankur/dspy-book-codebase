laptops = [
    {"name": "Laptop A", "price": 1000, "perf": 80}, # Expensive, okay speed
    {"name": "Laptop B", "price": 900,  "perf": 85}, # Cheaper & faster than A (Dominates A)
    {"name": "Laptop C", "price": 1200, "perf": 95}, # Expensive, but super fast (Efficient)
    {"name": "Laptop D", "price": 600,  "perf": 60}, # Very cheap, slow (Efficient)
    {"name": "Laptop E", "price": 600,  "perf": 55}, # Same price as D, but slower (Dominated by D)
]

def get_pareto_efficient_laptops_fast(candidates, verbose=False):
    if not candidates:
        return []
    
    sorted_candidates = sorted(candidates, key=lambda x: (x['price'], -x['perf']))
    
    pareto_frontier = []
    max_perf_seen = -float('inf')
    
    if verbose:
        print("--- Checking for inefficiencies ---")
    
    for laptop in sorted_candidates:
        if laptop['perf'] > max_perf_seen:
            pareto_frontier.append(laptop)
            max_perf_seen = laptop['perf']
        else:
            if verbose:
                dominator = next((l for l in pareto_frontier 
                                if l['price'] <= laptop['price'] and l['perf'] >= laptop['perf']), 
                               None)
                if dominator:
                    print(f"'{laptop['name']}' is dominated by '{dominator['name']}'")
    
    return pareto_frontier


def get_pareto_efficient_laptops_original(candidates, verbose=False):
    """Original O(n²) implementation for comparison."""
    efficient_list = []
    
    if verbose:
        print("--- Checking for inefficiencies ---")
    
    for current in candidates:
        is_dominated = False
        
        for other in candidates:
            if current is other:
                continue
            
            better_price = other['price'] <= current['price']
            better_perf  = other['perf'] >= current['perf']
            strictly_better = (other['price'] < current['price']) or (other['perf'] > current['perf'])
            
            if better_price and better_perf and strictly_better:
                is_dominated = True
                if verbose:
                    print(f"'{current['name']}' is dominated by '{other['name']}'")
                break
        
        if not is_dominated:
            efficient_list.append(current)
            
    return efficient_list

print("=== EFFICIENT ALGORITHM (O(n log n)) ===")
efficient_laptops = get_pareto_efficient_laptops_fast(laptops, verbose=True)

print("\n--- Pareto Efficient Laptops (The Frontier) ---")
for lap in efficient_laptops:
    print(f"{lap['name']}: ${lap['price']}, Score: {lap['perf']}")

print("\n" + "="*50)
print("=== ORIGINAL ALGORITHM (O(n²)) - For Comparison ===")

efficient_laptops_orig = get_pareto_efficient_laptops_original(laptops, verbose=True)

print("\n--- Pareto Efficient Laptops (The Frontier) ---")
for lap in efficient_laptops_orig:
    print(f"{lap['name']}: ${lap['price']}, Score: {lap['perf']}")

print("\n" + "="*50)
print("=== VERIFICATION ===")
efficient_names = {lap['name'] for lap in efficient_laptops}
orig_names = {lap['name'] for lap in efficient_laptops_orig}

if efficient_names == orig_names:
    print("✓ Both algorithms identified the same Pareto frontier!")
    print(f"  Efficient laptops: {sorted(efficient_names)}")
else:
    print("✗ Algorithms disagree (this shouldn't happen!)")
    print(f"  Fast algorithm: {sorted(efficient_names)}")
    print(f"  Original algorithm: {sorted(orig_names)}")

