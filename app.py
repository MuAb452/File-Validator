import streamlit as st
import pandas as pd

# Page setup
st.set_page_config(page_title="NetSuite Role Comparator", layout="wide")

st.title("🔍 NetSuite Role Comparator")
st.write("Upload Sandbox and Production Excel files to compare roles and permissions.")

# Upload files
sandbox_file = st.file_uploader("Upload Sandbox File", type=["xlsx", "xls"])
production_file = st.file_uploader("Upload Production File", type=["xlsx", "xls"])

# 🔧 CHANGE THESE if your column names are different
KEY_COLUMN = "Role Name"
COMPARE_COLUMN = "Permissions"

if sandbox_file and production_file:

    # Read files
    sandbox = pd.read_excel(sandbox_file)
    production = pd.read_excel(production_file)

    # Clean column names
    sandbox.columns = sandbox.columns.str.strip()
    production.columns = production.columns.str.strip()

    # Merge both datasets
    merged = sandbox.merge(
        production,
        on=KEY_COLUMN,
        how="outer",
        suffixes=("_sandbox", "_production"),
        indicator=True
    )

    # Compare logic
    def compare(row):
        if row["_merge"] == "left_only":
            return "❗ Missing in Production"
        elif row["_merge"] == "right_only":
            return "❗ Missing in Sandbox"
        elif row[f"{COMPARE_COLUMN}_sandbox"] == row[f"{COMPARE_COLUMN}_production"]:
            return "✅ Match"
        else:
            return "❌ Mismatch"

    merged["Result"] = merged.apply(compare, axis=1)

    # ✅ More accurate percentage (only rows that exist in BOTH)
    valid_rows = merged[merged["_merge"] == "both"]

    total = len(valid_rows)
    matches = (valid_rows["Result"] == "✅ Match").sum()

    accuracy = (matches / total * 100) if total > 0 else 0

    # 📊 Summary
    st.subheader("📊 Summary")
    col1, col2, col3 = st.columns(3)

    col1.metric("Roles Compared", total)
    col2.metric("Matches", matches)
    col3.metric("Accuracy", f"{accuracy:.2f}%")

    # 🔎 Filter
    st.subheader("🔎 Filter Results")

    option = st.selectbox(
        "Choose view",
        ["All", "Only Mismatches", "Only Matches", "Missing Roles"]
    )

    if option == "Only Mismatches":
        display_df = merged[merged["Result"] == "❌ Mismatch"]
    elif option == "Only Matches":
        display_df = merged[merged["Result"] == "✅ Match"]
    elif option == "Missing Roles":
        display_df = merged[merged["Result"].str.contains("Missing")]
    else:
        display_df = merged

    # 📋 Show table
    st.subheader("📋 Comparison Results")
    st.dataframe(display_df, use_container_width=True)

    # ⬇️ Download results
    st.download_button(
        label="⬇️ Download Results (CSV)",
        data=merged.to_csv(index=False),
        file_name="netsuite_comparison_results.csv",
        mime="text/csv"
    )

else:
    st.info("👆 Upload both Excel files to start comparison.")
