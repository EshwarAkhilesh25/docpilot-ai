import inspect
import sys
from pathlib import Path

# Add the app directory to the path
sys.path.insert(0, str(Path(__file__).parent))

# Import individual routers directly
from app.api.v1 import documents, chat, auth, health

print("=" * 80)
print("FASTAPI RUNTIME INTROSPECTION")
print("=" * 80)

# Step 1: Print all registered routes
print("\n" + "=" * 80)
print("STEP 1: ALL REGISTERED ROUTES")
print("=" * 80)

routers = {
    "documents": documents.router,
    "chat": chat.router,
    "auth": auth.router,
    "health": health.router,
}

for router_name, router in routers.items():
    print(f"\n--- {router_name.upper()} ROUTER ROUTES ---")
    for route in router.routes:
        if hasattr(route, "endpoint"):
            print("\n" + "-" * 80)
            print("PATH:", route.path)
            print("METHODS:", route.methods)
            print("ENDPOINT:", route.endpoint)
            print("SIGNATURE:", inspect.signature(route.endpoint))
            print("ROUTE TYPE:", type(route))

# Step 2: Inspect specific endpoints
target_endpoints = [
    ("/documents/upload", "documents"),
    ("/documents", "documents"),
    ("/chat/conversations", "chat"),
]

print("\n" + "=" * 80)
print("STEP 2: DETAILED ENDPOINT INSPECTION")
print("=" * 80)

for target_path, router_name in target_endpoints:
    print("\n" + "=" * 80)
    print(f"INSPECTING: {target_path} (from {router_name} router)")
    print("=" * 80)

    # Find the route in the specific router
    router = routers[router_name]
    route = None
    for r in router.routes:
        if hasattr(r, "path") and r.path == target_path:
            route = r
            break

    if route is None:
        print(f"Route not found: {target_path}")
        # Try to find similar routes
        print("Available routes in this router:")
        for r in router.routes:
            if hasattr(r, "path"):
                print(f"  {r.path}")
        continue

    print("\n--- BASIC INFO ---")
    print("ROUTE TYPE:", type(route))
    print("PATH:", route.path)
    print("METHODS:", route.methods)

    print("\n--- ENDPOINT ---")
    print("ENDPOINT:", route.endpoint)
    print("ENDPOINT TYPE:", type(route.endpoint))

    print("\n--- ENDPOINT SIGNATURE ---")
    try:
        print("SIGNATURE:", inspect.signature(route.endpoint))
    except Exception as e:
        print(f"ERROR getting signature: {e}")

    print("\n--- ENDPOINT SOURCE ---")
    try:
        source = inspect.getsource(route.endpoint)
        print("SOURCE:")
        print(source)
    except Exception as e:
        print(f"ERROR getting source: {e}")

    print("\n--- DEPENDANT ---")
    print("DEPENDANT:", route.dependant)
    print("DEPENDANT TYPE:", type(route.dependant))

    print("\n--- QUERY PARAMS ---")
    print("QUERY PARAMS:", route.dependant.query_params)
    for param in route.dependant.query_params:
        print(f"  {param}")
        print(f"    Type: {type(param)}")
        print(f"    Name: {param.name}")
        print(f"    Field info: {param.field_info}")

    print("\n--- BODY PARAMS ---")
    print("BODY PARAMS:", route.dependant.body_params)
    for param in route.dependant.body_params:
        print(f"  {param}")
        print(f"    Type: {type(param)}")
        print(f"    Name: {param.name}")
        print(f"    Field info: {param.field_info}")

    print("\n--- DEPENDENCIES ---")
    print("DEPENDENCIES:", route.dependant.dependencies)
    for dep in route.dependant.dependencies:
        print(f"\n  Dependency: {dep}")
        print(f"    Type: {type(dep)}")
        print(f"    Call: {dep.call}")
        print(f"    Call type: {type(dep.call)}")
        print(f"    Name: {dep.name}")
        print(f"    Query params: {dep.query_params}")
        print(f"    Body params: {dep.body_params}")
        try:
            print(f"    Call signature: {inspect.signature(dep.call)}")
        except Exception as e:
            print(f"    ERROR getting signature: {e}")
        print(f"    Use cache: {dep.use_cache}")
        print(f"    Scope: {dep.scope}")

print("\n" + "=" * 80)
print("INTROSPECTION COMPLETE")
print("=" * 80)
