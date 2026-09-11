"""
Exercise 2.2b: Polymorphism in Action

Demonstrates:
- A Vehicle base class with a common interface (describe, fuel_cost)
- Three concrete subclasses: Car, Truck, Motorcycle
- describe_fleet() works on any mix of Vehicle subtypes — pure polymorphism
- super().__init__() usage for clean constructor chaining
"""

from abc import ABC, abstractmethod


# =====================================================================
# BASE CLASS
# =====================================================================
class Vehicle(ABC):
    """Abstract base for all vehicles in the fleet."""

    def __init__(self, make: str, model: str, year: int):
        self.make = make
        self.model = model
        self.year = year

    @abstractmethod
    def fuel_cost_per_km(self) -> float:
        """Returns estimated fuel cost in USD per kilometre."""

    def describe(self) -> str:
        return f"{self.year} {self.make} {self.model}"

    def trip_cost(self, distance_km: float) -> float:
        """Returns total fuel cost for a given trip distance."""
        return round(self.fuel_cost_per_km() * distance_km, 2)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.describe()})"


# =====================================================================
# CONCRETE SUBCLASSES
# =====================================================================
class Car(Vehicle):
    """Standard passenger car."""

    def __init__(self, make: str, model: str, year: int, engine_litres: float):
        super().__init__(make, model, year)
        self.engine_litres = engine_litres

    def fuel_cost_per_km(self) -> float:
        # Rough estimate: larger engine → higher cost
        return round(0.08 + self.engine_litres * 0.015, 4)


class Truck(Vehicle):
    """Heavy goods vehicle."""

    def __init__(self, make: str, model: str, year: int, payload_tonnes: float):
        super().__init__(make, model, year)
        self.payload_tonnes = payload_tonnes

    def fuel_cost_per_km(self) -> float:
        # Trucks cost more per km; heavier payload → more fuel
        return round(0.20 + self.payload_tonnes * 0.03, 4)


class Motorcycle(Vehicle):
    """Two-wheeled vehicle — most fuel efficient."""

    def __init__(self, make: str, model: str, year: int, cc: int):
        super().__init__(make, model, year)
        self.cc = cc  # engine displacement in cubic centimetres

    def fuel_cost_per_km(self) -> float:
        return round(0.04 + self.cc * 0.00005, 4)


# =====================================================================
# POLYMORPHIC FUNCTION
# =====================================================================
def describe_fleet(vehicles: list[Vehicle], trip_km: float = 100.0) -> None:
    """
    Prints a fleet report for any mix of Vehicle subtypes.
    This function has zero knowledge of Car, Truck, or Motorcycle —
    it only knows the Vehicle interface. That's polymorphism.
    """
    print(f"\n{'=' * 55}")
    print(f"  FLEET REPORT  |  Trip distance: {trip_km:.0f} km")
    print(f"{'=' * 55}")
    print(f"  {'Vehicle':<32} {'$/km':>7}  {'Trip cost':>10}")
    print(f"  {'-' * 52}")
    for v in vehicles:
        print(
            f"  {v.describe():<32} "
            f"${v.fuel_cost_per_km():>6.4f}  "
            f"${v.trip_cost(trip_km):>9.2f}"
        )
    total = sum(v.trip_cost(trip_km) for v in vehicles)
    print(f"  {'-' * 52}")
    print(f"  {'TOTAL FLEET COST':<40} ${total:>9.2f}")
    print(f"{'=' * 55}\n")


# =====================================================================
# DEMONSTRATION
# =====================================================================
if __name__ == "__main__":
    fleet: list[Vehicle] = [
        Car("Toyota", "Camry",        2022, engine_litres=2.5),
        Car("Tesla",  "Model 3",      2023, engine_litres=0.0),   # EV — minimal cost
        Truck("Volvo", "FH16",        2021, payload_tonnes=20.0),
        Truck("Tata",  "Prima 4938S", 2020, payload_tonnes=35.0),
        Motorcycle("Royal Enfield", "Bullet 350", 2023, cc=350),
        Motorcycle("Ducati",        "Panigale V4", 2022, cc=1103),
    ]

    describe_fleet(fleet, trip_km=250)

    # Prove polymorphism: add a brand-new subclass at runtime, no describe_fleet changes needed
    class ElectricScooter(Vehicle):
        def fuel_cost_per_km(self) -> float:
            return 0.01  # electricity is cheap

    fleet.append(ElectricScooter("Ola", "S1 Pro", 2023))
    describe_fleet(fleet, trip_km=50)
