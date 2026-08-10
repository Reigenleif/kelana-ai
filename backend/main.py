def print_trip_summary(destination,
                    country,
                    days,
                    budget,
                    currency,
                    travel_month,
                    transportation_cost,
                    hotel_cost,
                    food_cost,
                    miscellaneous_cost):
    # Perhitungan total biaya perjalanan
    total_cost = transportation_cost + hotel_cost + food_cost + miscellaneous_cost

    print("========================")
    print("KelanaAI")
    print("========================\n")

    print(f"Destination : {destination}")
    print(f"Country     : {country}")
    print(f"Days        : {days}")
    print(f"Budget      : {budget} {currency}")
    print(f"Currency    : {currency}")
    print(f"Travel Month: {travel_month}")
    
    if total_cost > budget:
        print(f"\nTotal Cost  : {total_cost} {currency}")
        print("Warning: Total cost exceeds budget!")

# Blok input
destination = input("Masukkan destinasi: ")
country = input("Masukkan negara: ")
days = int(input("Masukkan jumlah hari: "))
budget = float(input("Masukkan budget: "))
currency = input("Masukkan mata uang: ")
travel_month = input("Masukkan bulan perjalanan: ")
transportation_cost = float(input("Masukkan biaya transportasi: "))
hotel_cost = float(input("Masukkan biaya hotel: "))
food_cost = float(input("Masukkan biaya makanan: "))
miscellaneous_cost = float(input("Masukkan biaya lainnya: "))

# Memanggil fungsi untuk mencetak informasi perjalanan
print_trip_summary(destination,
                    country,
                    days,
                    budget,
                    currency,
                    travel_month,
                    transportation_cost,
                    hotel_cost,
                    food_cost,
                    miscellaneous_cost)