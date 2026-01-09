# Task 2B: Inventory and Shopping Cart System


inventory = {
    "apple": 30.0,
    "milk": 45.5,
    "bread": 40.0,
    "eggs": 60.0
}


cart = ["apple", "bread", "milk"]


print("Type of inventory:", type(inventory))
print("Type of one price value:", type(inventory["apple"]))
print("Type of cart:", type(cart))


total_bill = 0
for item in cart:
    if item in inventory:
        total_bill += inventory[item]
    else:
        print(f"{item} not available")

print("Total Bill:", total_bill)


if total_bill > 100:
    print("Bill exceeds 100")
else:
    print("Bill is within limit")


unique_items = set(cart)
print("Unique items:", unique_items)


categories = ("fruits", "dairy", "bakery")
print("Categories:", categories)
print("Type of categories:", type(categories))


inventory["unknown_item"] = None
print("Unknown item price:", inventory["unknown_item"])
print("Type:", type(inventory["unknown_item"]))

# 9. Boolean variable
is_discount_applied = False

if total_bill > 100:
    is_discount_applied = True

print("Discount applied:", is_discount_applied)
print("Type of discount flag:", type(is_discount_applied))
