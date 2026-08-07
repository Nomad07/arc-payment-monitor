def check_address(address):
    if address.startswith("0x") and len(address) == 42:
        return True

    return False


def main():
    print("Arc Wallet Checker")
    print("------------------")

    address = input("Enter Arc wallet address: ")

    if check_address(address):
        print("Valid wallet address")
    else:
        print("Invalid wallet address")


if __name__ == "__main__":
    main()
