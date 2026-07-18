"""
EAFC 26 Underdog Scout Bot
---------------------------
Scans a Kaggle EAFC 26 player dataset and finds "hidden gem" players:
young, currently underrated (low overall), but with high future potential.

Data source: Kaggle - "FC 26 (FIFA 26) Player Data"
https://www.kaggle.com/datasets/rovnez/fc-26-fifa-26-player-data
"""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors


def load_data(file_name):
    """
    Load the CSV file, keep only the columns we need, and clean missing values.

    Parameters:
        file_name (str): path to the EAFC 26 CSV file.

    Returns:
        pd.DataFrame: cleaned dataframe with the relevant scouting columns.
    """
    df = pd.read_csv(file_name, low_memory=False)

    columns = ["short_name", "age", "overall", "potential",
               "club_name", "value_eur", "preferred_foot",
               "player_positions", "club_position"]

    df_short = df[columns].copy()

    # Free agents have no club, so we label them instead of dropping them
    df_short["club_name"] = df_short["club_name"].fillna("Free Agent")
    df_short["club_position"] = df_short["club_position"].fillna("Unassigned")

    return df_short


def filter_underdogs(df, max_age=23, max_overall=75, min_potential=85):
    """
    Filter players who are young, currently underrated, but have high potential.

    Parameters:
        df (pd.DataFrame): the cleaned player dataframe.
        max_age (int): maximum age allowed.
        max_overall (int): maximum current overall rating allowed.
        min_potential (int): minimum potential rating required.

    Returns:
        pd.DataFrame: filtered players, sorted by potential (descending).
    """
    underdogs = df.loc[
        (df["age"] <= max_age) &
        (df["overall"] < max_overall) &
        (df["potential"] >= min_potential)
    ]
    return underdogs.sort_values("potential", ascending=False)


def print_results(sorted_underdogs):
    """Print the filtered players to the terminal in a readable format."""
    print(f"======= HIDDEN GEMS (UNDERDOGS) ======= ({len(sorted_underdogs)} players)")

    for i, (index, player) in enumerate(sorted_underdogs.iterrows(), start=1):
        print(f"{i}. {player['short_name']} | Age: {player['age']} | Overall: {player['overall']} | "
              f"Potential: {player['potential']} | Club: {player['club_name']} | "
              f"Value: {player['value_eur']:,} € | Foot: {player['preferred_foot']} | "
              f"Position: {player['player_positions']}")


def plot_scatter(sorted_underdogs, title="EAFC 26 - Hidden Gems"):
    """
    Draw a scatter plot: age vs potential, point size by market value,
    point color by current overall rating.
    """
    plt.figure(figsize=(10, 6))

    plt.scatter(
        sorted_underdogs["age"],
        sorted_underdogs["potential"],
        s=sorted_underdogs["value_eur"] / 50000,
        alpha=0.6,
        c=sorted_underdogs["overall"],
        cmap="viridis"
    )

    plt.colorbar(label="Overall (Current Rating)")
    plt.xlabel("Age")
    plt.ylabel("Potential")
    plt.title(title)
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.show()


def create_table_image(sorted_underdogs, file_name="hidden_gems_table.png"):
    """
    Build a styled table image (green header, zebra stripes, color-coded
    overall column) and save it as a PNG file.
    """
    table_columns = ["short_name", "age", "overall", "potential",
                      "club_name", "value_eur", "preferred_foot", "player_positions"]

    table_df = sorted_underdogs[table_columns].copy()
    table_df["value_eur"] = table_df["value_eur"].apply(lambda x: f"{x:,.0f} €")
    table_data = table_df.values

    row_count = len(table_df)
    col_count = len(table_columns)

    fig, ax = plt.subplots(figsize=(15, row_count * 0.35 + 1))
    ax.axis("off")

    table = ax.table(
        cellText=table_data,
        colLabels=["Name", "Age", "Overall", "Potential", "Club", "Value (€)", "Foot", "Position"],
        loc="center",
        cellLoc="center"
    )

    table.auto_set_font_size(False)
    table.set_fontsize(9)
    table.scale(1, 1.6)

    # Build a red-yellow-green color scale based on the overall rating
    min_overall = sorted_underdogs["overall"].min()
    max_overall = sorted_underdogs["overall"].max()
    norm = mcolors.Normalize(vmin=min_overall, vmax=max_overall)
    colormap = plt.colormaps["RdYlGn"]

    overall_col_index = 2  # column order: name=0, age=1, overall=2, potential=3...

    # Style the header row
    for col_index in range(col_count):
        cell = table[0, col_index]
        cell.set_facecolor("#1B5E20")
        cell.set_text_props(color="white", weight="bold")
        cell.set_edgecolor("white")

    # Style each data row
    for row_index, player in enumerate(sorted_underdogs.itertuples(), start=1):
        for col_index in range(col_count):
            cell = table[row_index, col_index]
            cell.set_edgecolor("#cccccc")

            if col_index == overall_col_index:
                color = colormap(norm(player.overall))
                cell.set_facecolor(color)
                cell.set_text_props(weight="bold")
            else:
                # Zebra stripes for readability
                cell.set_facecolor("#f2f2f2" if row_index % 2 == 0 else "white")

    plt.title("EAFC 26 - Hidden Gems Full List", fontsize=15, fontweight="bold", pad=20)
    plt.tight_layout()
    plt.savefig(file_name, dpi=200, bbox_inches="tight")
    plt.show()


def ask_user_for_filters():
    print("\n--- Build Your Own Filter (press Enter to use the default value) ---")
    
    try:
        max_age_input = input("Maximum age (default 23): ").strip()
        max_age = int(max_age_input) if max_age_input else 23
        
        max_overall_input = input("Maximum overall rating (default 75): ").strip()
        max_overall = int(max_overall_input) if max_overall_input else 75
        
        min_potential_input = input("Minimum potential (default 85): ").strip()
        min_potential = int(min_potential_input) if min_potential_input else 85
        
    except ValueError:
        print("Hata: Sadece rakam girmelisiniz! Sistem varsayılan değerlerle (23, 75, 85) devam ediyor...")
        return 23, 75, 85

    return max_age, max_overall, min_potential


def main():
    df = load_data("eafc26.csv")

    # 1) Show the general overview using default criteria
    default_underdogs = filter_underdogs(df)
    print(f"[Overview] {len(default_underdogs)} players found with default criteria.")
    plot_scatter(default_underdogs, title="EAFC 26 - Overview (Default Criteria)")

    # 2) Ask the user for their own custom filter
    max_age, max_overall, min_potential = ask_user_for_filters()
    custom_underdogs = filter_underdogs(df, max_age, max_overall, min_potential)

    # 3) Show and save the results based on the custom filter
    print_results(custom_underdogs)
    print(custom_underdogs["value_eur"].describe())

    if len(custom_underdogs) == 0:
        print("\nWarning: No players match these criteria, table cannot be created.")
        return

    create_table_image(custom_underdogs, file_name="custom_filter_table.png")


if __name__ == "__main__":
    main()