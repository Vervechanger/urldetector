import sys
import idna
from confusables import is_confusable

def is_homograph(domain: str) -> bool:
    try:
        ascii_version = idna.encode(domain).decode('ascii')
        if domain == ascii_version:
            
            return False  # Pure ASCII domain, likely safe
    except Exception:
        return True  # Invalid or suspicious IDN

    # Character-by-character confusion check
    for ch in domain:
        if is_confusable(ch, preferred_aliases=["LATIN"]):
            return True

    return False

def main():
    print("🔍 Homograph Attack Detector")
    while True:
        domain = input("Enter a domain (or 'exit'): ").strip()
        if domain.lower() == 'exit':
            break

        if is_homograph(domain):
            print(f"⚠️  Suspicious domain detected: {domain}")
        else:
            print(f"✅ Domain looks safe: {domain}")

if __name__ == "__main__":
    main()
