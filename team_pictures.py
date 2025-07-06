
franchise = "hg"  # Example franchise code
picture_url = f"https://europeanleague.football/images/franchises/onbright/max/{franchise}.png"
def get_team_picture(franchise_code):
    """
    Returns the URL of the team picture for the given franchise code.
    """
    return f"https://europeanleague.football/images/franchises/onbright/max/{franchise_code}.png"

def main():
    # Example usage
    franchise_code = "hg"   # Replace with the desired franchise code
    picture_url = get_team_picture(franchise_code)
    print(f"Team picture URL for franchise '{franchise_code}': {picture_url}")
if __name__ == "__main__":
    main()
