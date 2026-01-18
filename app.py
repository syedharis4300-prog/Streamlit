import streamlit as st
import pandas as pd
import plotly.express as px


@st.cache_data
def load_data(path="bmw.csv"):
	df = pd.read_csv(path)
	df.columns = df.columns.str.strip()
	if "model" in df.columns:
		df["model"] = df["model"].astype(str).str.strip()
	# Ensure numeric columns
	for col in ["price", "year", "mileage", "tax", "mpg", "engineSize"]:
		if col in df.columns:
			df[col] = pd.to_numeric(df[col], errors="coerce")
	return df.dropna(subset=[c for c in ["price", "year"] if c in df.columns])


def main():
	st.set_page_config(page_title="BMW Listings Dashboard", layout="wide")
	st.title("BMW Listings Dashboard")

	df = load_data()

	# Sidebar filters
	st.sidebar.header("Filters")
	models = sorted(df["model"].dropna().unique()) if "model" in df.columns else []
	selected_models = st.sidebar.multiselect("Model", models, default=models)

	year_min = int(df["year"].min()) if "year" in df.columns else 0
	year_max = int(df["year"].max()) if "year" in df.columns else 0
	selected_year = st.sidebar.slider("Year", year_min, year_max, (year_min, year_max))

	price_min = int(df["price"].min()) if "price" in df.columns else 0
	price_max = int(df["price"].max()) if "price" in df.columns else 0
	selected_price = st.sidebar.slider("Price", price_min, price_max, (price_min, price_max))

	transmissions = sorted(df["transmission"].dropna().unique()) if "transmission" in df.columns else []
	selected_trans = st.sidebar.multiselect("Transmission", transmissions, default=transmissions)

	fuels = sorted(df["fuelType"].dropna().unique()) if "fuelType" in df.columns else []
	selected_fuel = st.sidebar.multiselect("Fuel Type", fuels, default=fuels)

	# Apply filters
	df_filtered = df.copy()
	if selected_models:
		df_filtered = df_filtered[df_filtered["model"].isin(selected_models)]
	if "year" in df.columns:
		df_filtered = df_filtered[df_filtered["year"].between(selected_year[0], selected_year[1])]
	if "price" in df.columns:
		df_filtered = df_filtered[df_filtered["price"].between(selected_price[0], selected_price[1])]
	if selected_trans:
		df_filtered = df_filtered[df_filtered["transmission"].isin(selected_trans)]
	if selected_fuel:
		df_filtered = df_filtered[df_filtered["fuelType"].isin(selected_fuel)]

	# Metrics
	col1, col2, col3 = st.columns(3)
	with col1:
		st.metric("Listings", len(df_filtered))
	with col2:
		st.metric("Avg Price", f"£{int(df_filtered['price'].mean() if not df_filtered.empty else 0):,}")
	with col3:
		if "mileage" in df.columns:
			st.metric("Avg Mileage", f"{int(df_filtered['mileage'].mean() if not df_filtered.empty else 0):,}")

	# Main plots
	st.subheader("Price distribution")
	fig_hist = px.histogram(df_filtered, x="price", nbins=50, title="Price distribution")
	st.plotly_chart(fig_hist, use_container_width=True)

	st.subheader("Price vs Mileage")
	if "mileage" in df_filtered.columns:
		fig_scatter = px.scatter(
			df_filtered,
			x="mileage",
			y="price",
			color="fuelType" if "fuelType" in df_filtered.columns else None,
			hover_data=["model", "year"],
			title="Price vs Mileage",
			height=500,
		)
		st.plotly_chart(fig_scatter, use_container_width=True)
	else:
		st.info("No mileage data available for scatter plot.")

	st.subheader("Listings by Model")
	counts = df_filtered["model"].value_counts().reset_index()
	counts.columns = ["model", "count"]
	fig_bar = px.bar(counts, x="model", y="count", title="Listings by Model")
	st.plotly_chart(fig_bar, use_container_width=True)

	st.subheader("Price by Year")
	if "year" in df_filtered.columns:
		fig_box = px.box(df_filtered, x="year", y="price", title="Price by Year")
		st.plotly_chart(fig_box, use_container_width=True)

	# Data and download
	st.subheader("Data (filtered)")
	st.dataframe(df_filtered.reset_index(drop=True))

	csv = df_filtered.to_csv(index=False).encode("utf-8")
	st.download_button("Download filtered data as CSV", csv, "bmw_filtered.csv", "text/csv")


if __name__ == "__main__":
	main()

